"""
Main Application Controller - Orchestrates all components.
Dynamic island with weather, fullscreen mode, and smooth animations.
"""

import sys
import os
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QWidget
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
    QRect, QPoint, QTimer, Signal, QObject
)
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction

from core.timer import PomodoroTimer, TimerState
from core.database import Database, Task
from core.sounds import SoundManager
from core.weather import WeatherService
from ui.island import MiniIslandWidget
from ui.dashboard import DashboardWidget
from ui.fullscreen import FullscreenMode
from ui.styles import Theme, MIDNIGHT_STYLE


class AppController(QObject):
    """Main application controller with weather and fullscreen support."""
    
    def __init__(self):
        super().__init__()
        
        # Get app directory
        if getattr(sys, 'frozen', False):
            self.app_dir = sys._MEIPASS
        else:
            self.app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Initialize components
        self.db = Database()
        self.timer = PomodoroTimer()
        self.sound_manager = SoundManager(os.path.join(self.app_dir, 'static', 'sounds'))
        self.weather_service = WeatherService()
        
        # Load settings
        self._load_settings()
        
        # UI components
        self.island: Optional[MiniIslandWidget] = None
        self.dashboard: Optional[DashboardWidget] = None
        self.fullscreen: Optional[FullscreenMode] = None
        self.tray_icon: Optional[QSystemTrayIcon] = None
        
        # State
        self._is_expanded = False
        self._is_fullscreen = False
        self._current_task: Optional[Task] = None
        self._current_session_id: Optional[int] = None
        
        # Weather refresh timer (every 30 minutes)
        self._weather_timer = QTimer(self)
        self._weather_timer.timeout.connect(self._fetch_weather)
        self._weather_timer.setInterval(30 * 60 * 1000)
        
        # Animation
        self._anim_group: Optional[QParallelAnimationGroup] = None
    
    def _load_settings(self):
        settings = self.db.get_all_settings()
        
        work_duration = int(settings.get('work_duration', 25))
        break_duration = int(settings.get('break_duration', 5))
        alarm_sound = settings.get('alarm_sound', 'chime')
        
        self.timer.set_work_duration(work_duration)
        self.timer.set_break_duration(break_duration)
        self.sound_manager.set_sound(alarm_sound)
    
    def initialize(self):
        # Create mini island
        self.island = MiniIslandWidget()
        self.island.expand_requested.connect(self._expand_to_dashboard)
        self.island.play_pause_clicked.connect(self._toggle_timer)
        
        # Create dashboard
        self.dashboard = DashboardWidget()
        self.dashboard.collapse_requested.connect(self._collapse_to_island)
        self.dashboard.play_pause_clicked.connect(self._toggle_timer)
        self.dashboard.reset_clicked.connect(self._reset_timer)
        self.dashboard.skip_clicked.connect(self._skip_timer)
        self.dashboard.task_added.connect(self._add_task)
        self.dashboard.task_toggled.connect(self._toggle_task)
        self.dashboard.task_deleted.connect(self._delete_task)
        self.dashboard.task_selected.connect(self._select_task)
        self.dashboard.setting_changed.connect(self._on_setting_changed)
        self.dashboard.fullscreen_requested.connect(self._enter_fullscreen)
        self.dashboard.hide()
        
        # Create fullscreen mode
        self.fullscreen = FullscreenMode()
        self.fullscreen.close_requested.connect(self._exit_fullscreen)
        self.fullscreen.play_pause_clicked.connect(self._toggle_timer)
        self.fullscreen.hide()
        
        # Connect timer signals
        self.timer.tick.connect(self._on_timer_tick)
        self.timer.state_changed.connect(self._on_timer_state_changed)
        self.timer.timer_finished.connect(self._on_work_finished)
        self.timer.break_completed.connect(self._on_break_finished)
        
        # Connect weather
        self.weather_service.weather_updated.connect(self._on_weather_updated)
        
        # Setup system tray
        self._setup_tray()
        
        # Load initial data
        self._refresh_tasks()
        self._refresh_stats()
        
        # Load settings into dashboard
        settings = self.db.get_all_settings()
        settings.setdefault('work_duration', '25')
        settings.setdefault('break_duration', '5')
        settings.setdefault('alarm_sound', 'chime')
        self.dashboard.load_settings(settings)
        
        # Fetch weather
        self._fetch_weather()
        self._weather_timer.start()
        
        # Show island
        self.island.show()
    
    def _setup_tray(self):
        self.tray_icon = QSystemTrayIcon()
        
        # Create green circle icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(Theme.ACCENT))  # Green #4ADE80
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 28, 28)
        painter.end()
        
        self.tray_icon.setIcon(QIcon(pixmap))
        self.tray_icon.setToolTip("Focus Timer")
        
        # Create menu with pure black box and green accent
        menu = QMenu()
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: #000000;
                border: 1px solid #222222;
                border-radius: 12px;
                padding: 8px 4px;
            }}
            QMenu::item {{
                background-color: transparent;
                color: #FFFFFF;
                padding: 10px 28px 10px 16px;
                margin: 2px 4px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
            }}
            QMenu::item:selected {{
                background-color: #4ADE80;
                color: #000000;
            }}
            QMenu::item:disabled {{
                color: #555555;
            }}
            QMenu::separator {{
                height: 1px;
                background: #222222;
                margin: 6px 12px;
            }}
        """)
        
        show_action = QAction("Show", menu)
        show_action.triggered.connect(self._show_app)
        menu.addAction(show_action)
        
        fullscreen_action = QAction("Fullscreen Mode", menu)
        fullscreen_action.triggered.connect(self._enter_fullscreen)
        menu.addAction(fullscreen_action)
        
        hide_action = QAction("Hide", menu)
        hide_action.triggered.connect(self._hide_app)
        menu.addAction(hide_action)
        
        menu.addSeparator()
        
        start_action = QAction("Start/Pause", menu)
        start_action.triggered.connect(self._toggle_timer)
        menu.addAction(start_action)
        
        reset_action = QAction("Reset", menu)
        reset_action.triggered.connect(self._reset_timer)
        menu.addAction(reset_action)
        
        menu.addSeparator()
        
        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(self._quit_app)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()
    
    def _fetch_weather(self):
        """Fetch weather data."""
        self.weather_service.fetch_weather("")  # Auto-detect location
    
    def _on_weather_updated(self, weather):
        """Handle weather update."""
        if weather:
            self.fullscreen.set_weather(
                weather.icon,
                weather.display_temp,
                weather.display_condition
            )
            # Update dashboard too
            self.dashboard.set_weather(
                weather.icon,
                weather.display_temp,
                weather.location
            )
    
    def _expand_to_dashboard(self):
        """Animate expansion from mini island to dashboard."""
        if self._is_expanded:
            return
        
        self._is_expanded = True
        
        # Get island position
        island_rect = self.island.geometry()
        island_center_x = island_rect.center().x()
        
        # Calculate dashboard position
        dashboard_width = Theme.ISLAND_WIDTH_EXPANDED
        dashboard_height = Theme.ISLAND_HEIGHT_EXPANDED
        
        dashboard_x = island_center_x - dashboard_width // 2
        dashboard_y = island_rect.top()
        
        # Keep on screen
        screen = QApplication.primaryScreen().geometry()
        dashboard_x = max(10, min(dashboard_x, screen.width() - dashboard_width - 10))
        dashboard_y = max(10, min(dashboard_y, screen.height() - dashboard_height - 10))
        
        # Fade out island
        self.island.set_opacity(0)
        self.island.hide()
        
        # Position and show dashboard
        self.dashboard.setFixedSize(dashboard_width, dashboard_height)
        self.dashboard.move(dashboard_x, dashboard_y)
        self.dashboard.setWindowOpacity(0)
        self.dashboard.show()
        
        # Fade in animation
        self._anim_group = QParallelAnimationGroup()
        
        opacity_anim = QPropertyAnimation(self.dashboard, b"windowOpacity")
        opacity_anim.setDuration(Theme.EXPAND_DURATION)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_group.addAnimation(opacity_anim)
        
        self._anim_group.start()
    
    def _collapse_to_island(self):
        """Animate collapse from dashboard to mini island."""
        if not self._is_expanded:
            return
        
        self._is_expanded = False
        
        # Get dashboard position
        dashboard_rect = self.dashboard.geometry()
        dashboard_center_x = dashboard_rect.center().x()
        
        # Calculate island position
        island_width = Theme.ISLAND_WIDTH_MINI
        island_height = Theme.ISLAND_HEIGHT_MINI
        
        island_x = dashboard_center_x - island_width // 2
        island_y = dashboard_rect.top()
        
        # Keep on screen
        screen = QApplication.primaryScreen().geometry()
        island_x = max(10, min(island_x, screen.width() - island_width - 10))
        island_y = max(10, island_y)
        
        # Hide dashboard
        self.dashboard.hide()
        
        # Position and show island
        self.island.setFixedSize(island_width, island_height)
        self.island.move(island_x, island_y)
        self.island.set_opacity(0)
        self.island.show()
        
        # Fade in animation
        self._anim_group = QParallelAnimationGroup()
        
        opacity_anim = QPropertyAnimation(self.island, b"opacity")
        opacity_anim.setDuration(Theme.COLLAPSE_DURATION)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_group.addAnimation(opacity_anim)
        
        self._anim_group.start()
    
    def _enter_fullscreen(self):
        """Enter fullscreen focus mode."""
        self._is_fullscreen = True
        self.island.hide()
        self.dashboard.hide()
        self.fullscreen.show()
        
        # Update fullscreen with current timer state
        self.fullscreen.update_timer(self.timer.remaining_formatted, self.timer.progress)
        self.fullscreen.set_running(self.timer.state in (TimerState.RUNNING, TimerState.BREAK))
        self.fullscreen.set_break_mode(self.timer.is_break)
    
    def _exit_fullscreen(self):
        """Exit fullscreen mode."""
        self._is_fullscreen = False
        self.fullscreen.hide()
        
        if self._is_expanded:
            self.dashboard.show()
        else:
            self.island.show()
    
    # ============== Timer Controls ==============
    
    def _toggle_timer(self):
        if self.timer.state == TimerState.IDLE:
            self._current_session_id = self.db.start_session(
                self._current_task.id if self._current_task else None,
                "work"
            )
        
        self.timer.toggle()
    
    def _reset_timer(self):
        if self._current_session_id and self.timer.state != TimerState.IDLE:
            elapsed = self.timer.get_elapsed_seconds()
            self.db.end_session(self._current_session_id, elapsed, completed=False)
            self._current_session_id = None
        
        self.timer.reset()
        self._update_ui()
    
    def _skip_timer(self):
        if self.timer.is_break:
            self.timer.skip_break()
        else:
            self.timer.skip_to_break()
    
    def _on_timer_tick(self, remaining: int):
        time_text = self.timer.remaining_formatted
        progress = self.timer.progress
        
        self.island.update_timer(time_text, progress)
        self.dashboard.update_timer(time_text, progress)
        self.fullscreen.update_timer(time_text, progress)
    
    def _on_timer_state_changed(self, state: TimerState):
        is_running = state in (TimerState.RUNNING, TimerState.BREAK)
        is_break = state in (TimerState.BREAK, TimerState.BREAK_PAUSED)
        
        self.island.set_running(is_running)
        self.island.set_break_mode(is_break)
        
        self.dashboard.set_running(is_running)
        self.dashboard.set_break_mode(is_break)
        
        self.fullscreen.set_running(is_running)
        self.fullscreen.set_break_mode(is_break)
        
        if is_running:
            status = "Break" if is_break else "Working"
            self.tray_icon.setToolTip(f"Focus Timer - {status}: {self.timer.remaining_formatted}")
        else:
            self.tray_icon.setToolTip("Focus Timer - Paused")
    
    def _on_work_finished(self):
        if self._current_session_id:
            elapsed = self.timer.config.work_duration
            self.db.end_session(self._current_session_id, elapsed, completed=True)
            self._current_session_id = None
        
        self.sound_manager.play_alarm()
        
        self.tray_icon.showMessage(
            "Work Complete",
            "Time for a break!",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
        
        self._current_session_id = self.db.start_session(
            self._current_task.id if self._current_task else None,
            "break"
        )
        
        self._refresh_stats()
    
    def _on_break_finished(self):
        if self._current_session_id:
            self.db.end_session(self._current_session_id, 
                               self.timer.config.short_break, completed=True)
            self._current_session_id = None
        
        self.sound_manager.play_break_end()
        
        self.tray_icon.showMessage(
            "Break Over",
            "Ready to focus?",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
    
    # ============== Task Management ==============
    
    def _add_task(self, name: str):
        self.db.add_task(name)
        self._refresh_tasks()
    
    def _toggle_task(self, task_id: int, completed: bool):
        if completed:
            self.db.complete_task(task_id)
        else:
            self.db.uncomplete_task(task_id)
        self._refresh_tasks()
        self._refresh_stats()
    
    def _delete_task(self, task_id: int):
        if self._current_task and self._current_task.id == task_id:
            self._current_task = None
            self.timer.set_task(None)
            self.dashboard.set_current_task(None)
            self.island.update_task("Ready to focus")
        
        self.db.delete_task(task_id)
        self._refresh_tasks()
    
    def _select_task(self, task_id: int):
        task = self.db.get_task(task_id)
        if task and not task.completed:
            self._current_task = task
            self.timer.set_task(task_id)
            self.dashboard.set_current_task(task)
            self.island.update_task(task.name)
    
    def _refresh_tasks(self):
        tasks = self.db.get_all_tasks()
        self.dashboard.update_tasks_list(tasks)
    
    def _refresh_stats(self):
        today = self.db.get_today_stats()
        weekly = self.db.get_daily_stats(7)
        total = self.db.get_total_stats()
        self.dashboard.update_stats(today, weekly, total)
    
    # ============== Settings ==============
    
    def _on_setting_changed(self, key: str, value: str):
        self.db.set_setting(key, value)
        
        if key == "work_duration":
            self.timer.set_work_duration(int(value))
            if self.timer.state == TimerState.IDLE:
                self._update_ui()
        elif key == "break_duration":
            self.timer.set_break_duration(int(value))
        elif key == "alarm_sound":
            self.sound_manager.set_sound(value)
    
    # ============== Tray Actions ==============
    
    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_app()
    
    def _show_app(self):
        if self._is_fullscreen:
            self.fullscreen.show()
            self.fullscreen.raise_()
        elif self._is_expanded:
            self.dashboard.show()
            self.dashboard.raise_()
            self.dashboard.activateWindow()
        else:
            self.island.show()
            self.island.raise_()
    
    def _hide_app(self):
        self.island.hide()
        self.dashboard.hide()
        self.fullscreen.hide()
    
    def _quit_app(self):
        if self._current_session_id:
            elapsed = self.timer.get_elapsed_seconds()
            self.db.end_session(self._current_session_id, elapsed, completed=False)
        
        self.tray_icon.hide()
        QApplication.quit()
    
    # ============== Helpers ==============
    
    def _update_ui(self):
        time_text = self.timer.remaining_formatted
        progress = self.timer.progress
        
        self.island.update_timer(time_text, progress)
        self.dashboard.update_timer(time_text, progress)
        self.fullscreen.update_timer(time_text, progress)


def main():
    # Enable high DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Apply midnight style
    app.setStyleSheet(MIDNIGHT_STYLE)
    
    # Load fonts
    app_dir = os.path.dirname(os.path.abspath(__file__))
    Theme.load_fonts(app_dir)
    
    # Create and initialize controller
    controller = AppController()
    controller.initialize()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
