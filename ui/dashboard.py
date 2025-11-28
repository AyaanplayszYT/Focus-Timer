"""
Dashboard View - Expanded view with timer controls, tasks, and stats.
Pure black with green accent - Dynamic Island style.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QFrame, QStackedWidget, QComboBox,
    QSlider, QGraphicsDropShadowEffect, QApplication, QSpacerItem,
    QSizePolicy, QTabWidget
)
from PySide6.QtCore import (
    Qt, Signal, QPoint, QPropertyAnimation, QEasingCurve,
    Property, QRect, QTimer, QParallelAnimationGroup
)
from PySide6.QtGui import (
    QColor, QPainter, QPainterPath, QBrush, QPen,
    QLinearGradient, QFont, QKeySequence, QShortcut
)
from typing import Optional, List

from ui.components import (
    CircularProgress, IconButton, ControlButton, TaskItemWidget, 
    StatsBarWidget, GlassCard, AnimatedButton
)
from ui.styles import Theme
from core.database import Task, DailyStats


class DashboardWidget(QWidget):
    """Expanded dashboard view - Pure black with green accents."""
    
    collapse_requested = Signal()
    play_pause_clicked = Signal()
    reset_clicked = Signal()
    skip_clicked = Signal()
    task_added = Signal(str)
    task_toggled = Signal(int, bool)
    task_deleted = Signal(int)
    task_selected = Signal(int)
    setting_changed = Signal(str, str)
    fullscreen_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._width = Theme.ISLAND_WIDTH_EXPANDED
        self._height = Theme.ISLAND_HEIGHT_EXPANDED
        self._radius = Theme.EXPANDED_RADIUS
        self.setFixedSize(self._width, self._height)
        
        # State
        self._is_running = False
        self._is_break = False
        self._time_text = "25:00"
        self._progress = 0.0
        self._current_task: Optional[Task] = None
        
        # Dragging
        self._drag_pos: Optional[QPoint] = None
        self._is_dragging = False
        
        self._setup_ui()
        self._setup_shortcuts()
    
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 16)
        main_layout.setSpacing(10)
        
        # Header
        header = self._create_header()
        main_layout.addLayout(header)
        
        # Tab widget with sleek styling
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: transparent;
            }}
            QTabBar::tab {{
                background: transparent;
                color: {Theme.TEXT_MUTED};
                border: none;
                padding: 8px 16px;
                margin-right: 4px;
                border-radius: 8px;
                font-size: 11px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background: {Theme.ACCENT};
                color: {Theme.BG_DARKEST};
            }}
            QTabBar::tab:hover:!selected {{
                background: rgba(255,255,255,0.05);
                color: {Theme.TEXT_SECONDARY};
            }}
        """)
        
        # Tabs
        self.tabs.addTab(self._create_timer_section(), "Timer")
        self.tabs.addTab(self._create_tasks_section(), "Tasks")
        self.tabs.addTab(self._create_stats_section(), "Stats")
        self.tabs.addTab(self._create_settings_section(), "Settings")
        
        main_layout.addWidget(self.tabs)
    
    def _create_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        # Title with accent dot
        title_layout = QHBoxLayout()
        title_layout.setSpacing(6)
        
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {Theme.ACCENT}; font-size: 8px;")
        title_layout.addWidget(dot)
        
        title = QLabel("Focus")
        title.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 700;
            color: {Theme.TEXT_PRIMARY};
        """)
        title_layout.addWidget(title)
        
        layout.addLayout(title_layout)
        
        # Weather display
        self.weather_label = QLabel("")
        self.weather_label.setStyleSheet(f"""
            font-size: 10px;
            color: {Theme.TEXT_MUTED};
            margin-left: 8px;
        """)
        layout.addWidget(self.weather_label)
        
        layout.addStretch()
        
        # Fullscreen button
        self.fullscreen_btn = IconButton("expand", 24)
        self.fullscreen_btn.setToolTip("Fullscreen (F11)")
        self.fullscreen_btn.clicked.connect(self.fullscreen_requested.emit)
        layout.addWidget(self.fullscreen_btn)
        
        # Collapse button
        self.collapse_btn = IconButton("collapse", 24)
        self.collapse_btn.setToolTip("Collapse")
        self.collapse_btn.clicked.connect(self.collapse_requested.emit)
        layout.addWidget(self.collapse_btn)
        
        return layout
    
    def _create_timer_section(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(10)
        
        # Progress circle with timer inside
        timer_container = QVBoxLayout()
        timer_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.progress_circle = CircularProgress(130)
        timer_container.addWidget(self.progress_circle, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Time label
        self.timer_label = QLabel(self._time_text)
        self.timer_label.setStyleSheet(f"""
            font-size: 42px;
            font-weight: 800;
            color: {Theme.TEXT_PRIMARY};
            letter-spacing: 2px;
        """)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_container.addWidget(self.timer_label)
        
        # Status
        self.status_label = QLabel("Ready to focus")
        self.status_label.setStyleSheet(f"font-size: 11px; color: {Theme.TEXT_MUTED}; font-weight: 500;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_container.addWidget(self.status_label)
        
        layout.addLayout(timer_container)
        
        # Current task pill
        task_pill = QWidget()
        task_pill.setStyleSheet(f"""
            background: {Theme.BG_ELEVATED};
            border-radius: 12px;
        """)
        task_layout = QHBoxLayout(task_pill)
        task_layout.setContentsMargins(14, 8, 14, 8)
        
        task_icon = QLabel("◉")
        task_icon.setStyleSheet(f"color: {Theme.ACCENT}; font-size: 10px;")
        task_layout.addWidget(task_icon)
        
        self.current_task_label = QLabel("No task selected")
        self.current_task_label.setStyleSheet(f"font-size: 11px; color: {Theme.TEXT_SECONDARY}; font-weight: 500;")
        task_layout.addWidget(self.current_task_label)
        task_layout.addStretch()
        
        layout.addWidget(task_pill)
        
        # Control buttons - clean layout
        controls = QHBoxLayout()
        controls.setSpacing(12)
        controls.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.reset_btn = IconButton("reset", 38)
        self.reset_btn.setToolTip("Reset")
        self.reset_btn.clicked.connect(self.reset_clicked.emit)
        controls.addWidget(self.reset_btn)
        
        self.play_btn = ControlButton("play", 52)
        self.play_btn.clicked.connect(self.play_pause_clicked.emit)
        controls.addWidget(self.play_btn)
        
        self.skip_btn = IconButton("skip", 38)
        self.skip_btn.setToolTip("Skip")
        self.skip_btn.clicked.connect(self.skip_clicked.emit)
        controls.addWidget(self.skip_btn)
        
        layout.addLayout(controls)
        layout.addStretch()
        
        return widget
    
    def _create_tasks_section(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(10)
        
        # Add task input
        input_container = QWidget()
        input_container.setStyleSheet(f"""
            background: {Theme.BG_ELEVATED};
            border-radius: 12px;
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(12, 8, 8, 8)
        input_layout.setSpacing(8)
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Add a task...")
        self.task_input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {Theme.TEXT_PRIMARY};
                font-size: 12px;
                padding: 4px 0;
            }}
        """)
        self.task_input.returnPressed.connect(self._on_add_task)
        input_layout.addWidget(self.task_input)
        
        add_btn = IconButton("plus", 30)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Theme.ACCENT};
                border: none;
                border-radius: 15px;
            }}
            QPushButton:hover {{
                background: {Theme.ACCENT_LIGHT};
            }}
        """)
        add_btn.clicked.connect(self._on_add_task)
        input_layout.addWidget(add_btn)
        
        layout.addWidget(input_container)
        
        # Tasks list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setContentsMargins(0, 0, 0, 0)
        self.tasks_layout.setSpacing(6)
        self.tasks_layout.addStretch()
        
        scroll.setWidget(self.tasks_container)
        layout.addWidget(scroll)
        
        return widget
    
    def _create_stats_section(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)
        
        # Today's summary - clean card
        summary_card = QWidget()
        summary_card.setStyleSheet(f"""
            background: {Theme.BG_ELEVATED};
            border-radius: 14px;
        """)
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(16, 14, 16, 14)
        summary_layout.setSpacing(4)
        
        summary_title = QLabel("TODAY")
        summary_title.setStyleSheet(f"font-size: 9px; color: {Theme.TEXT_MUTED}; font-weight: 600; letter-spacing: 1px;")
        summary_layout.addWidget(summary_title)
        
        self.today_focus_label = QLabel("0h 0m")
        self.today_focus_label.setStyleSheet(f"font-size: 28px; font-weight: 800; color: {Theme.ACCENT};")
        summary_layout.addWidget(self.today_focus_label)
        
        self.today_sessions_label = QLabel("0 sessions completed")
        self.today_sessions_label.setStyleSheet(f"font-size: 10px; color: {Theme.TEXT_MUTED};")
        summary_layout.addWidget(self.today_sessions_label)
        
        layout.addWidget(summary_card)
        
        # Weekly chart header
        chart_header = QHBoxLayout()
        chart_label = QLabel("LAST 7 DAYS")
        chart_label.setStyleSheet(f"font-size: 9px; font-weight: 600; color: {Theme.TEXT_MUTED}; letter-spacing: 1px;")
        chart_header.addWidget(chart_label)
        chart_header.addStretch()
        
        self.total_focus_label = QLabel("0h total")
        self.total_focus_label.setStyleSheet(f"font-size: 9px; color: {Theme.TEXT_MUTED};")
        chart_header.addWidget(self.total_focus_label)
        
        layout.addLayout(chart_header)
        
        # Stats bars container
        self.stats_container = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_container)
        self.stats_layout.setContentsMargins(0, 0, 0, 0)
        self.stats_layout.setSpacing(4)
        
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in days:
            bar = StatsBarWidget(day, 0, 8 * 3600)
            self.stats_layout.addWidget(bar)
        
        layout.addWidget(self.stats_container)
        layout.addStretch()
        
        return widget
    
    def _create_settings_section(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)
        
        # Timer settings card
        timer_card = QWidget()
        timer_card.setStyleSheet(f"background: {Theme.BG_ELEVATED}; border-radius: 14px;")
        timer_layout = QVBoxLayout(timer_card)
        timer_layout.setContentsMargins(16, 14, 16, 14)
        timer_layout.setSpacing(14)
        
        # Work duration
        work_row = QHBoxLayout()
        work_label = QLabel("Work duration")
        work_label.setStyleSheet(f"font-size: 12px; color: {Theme.TEXT_SECONDARY}; font-weight: 500;")
        work_row.addWidget(work_label)
        work_row.addStretch()
        
        self.work_duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.work_duration_slider.setRange(5, 60)
        self.work_duration_slider.setValue(25)
        self.work_duration_slider.setFixedWidth(100)
        work_row.addWidget(self.work_duration_slider)
        
        self.work_duration_label = QLabel("25m")
        self.work_duration_label.setStyleSheet(f"font-size: 12px; color: {Theme.ACCENT}; font-weight: 600; min-width: 35px;")
        work_row.addWidget(self.work_duration_label)
        
        self.work_duration_slider.valueChanged.connect(
            lambda v: self._on_slider_change("work_duration", v)
        )
        timer_layout.addLayout(work_row)
        
        # Break duration
        break_row = QHBoxLayout()
        break_label = QLabel("Break duration")
        break_label.setStyleSheet(f"font-size: 12px; color: {Theme.TEXT_SECONDARY}; font-weight: 500;")
        break_row.addWidget(break_label)
        break_row.addStretch()
        
        self.break_duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.break_duration_slider.setRange(1, 30)
        self.break_duration_slider.setValue(5)
        self.break_duration_slider.setFixedWidth(100)
        break_row.addWidget(self.break_duration_slider)
        
        self.break_duration_label = QLabel("5m")
        self.break_duration_label.setStyleSheet(f"font-size: 12px; color: {Theme.SECONDARY}; font-weight: 600; min-width: 35px;")
        break_row.addWidget(self.break_duration_label)
        
        self.break_duration_slider.valueChanged.connect(
            lambda v: self._on_slider_change("break_duration", v)
        )
        timer_layout.addLayout(break_row)
        
        layout.addWidget(timer_card)
        
        # Sound settings card
        sound_card = QWidget()
        sound_card.setStyleSheet(f"background: {Theme.BG_ELEVATED}; border-radius: 14px;")
        sound_layout = QHBoxLayout(sound_card)
        sound_layout.setContentsMargins(16, 12, 16, 12)
        
        alarm_label = QLabel("Alarm sound")
        alarm_label.setStyleSheet(f"font-size: 12px; color: {Theme.TEXT_SECONDARY}; font-weight: 500;")
        sound_layout.addWidget(alarm_label)
        sound_layout.addStretch()
        
        self.alarm_combo = QComboBox()
        self.alarm_combo.addItems(["Chime", "Bell", "Digital", "Gentle"])
        self.alarm_combo.setFixedWidth(100)
        self.alarm_combo.currentTextChanged.connect(
            lambda v: self.setting_changed.emit("alarm_sound", v.lower())
        )
        sound_layout.addWidget(self.alarm_combo)
        
        layout.addWidget(sound_card)
        
        # Shortcuts info
        shortcuts_card = QWidget()
        shortcuts_card.setStyleSheet(f"background: {Theme.BG_ELEVATED}; border-radius: 14px;")
        sc_layout = QVBoxLayout(shortcuts_card)
        sc_layout.setContentsMargins(16, 12, 16, 12)
        sc_layout.setSpacing(4)
        
        sc_title = QLabel("SHORTCUTS")
        sc_title.setStyleSheet(f"font-size: 9px; color: {Theme.TEXT_MUTED}; font-weight: 600; letter-spacing: 1px;")
        sc_layout.addWidget(sc_title)
        
        sc_info = QLabel("Space: Play/Pause  •  R: Reset  •  Esc: Collapse")
        sc_info.setStyleSheet(f"font-size: 10px; color: {Theme.TEXT_MUTED};")
        sc_info.setWordWrap(True)
        sc_layout.addWidget(sc_info)
        
        layout.addWidget(shortcuts_card)
        layout.addStretch()
        
        return widget
    
    def _setup_shortcuts(self):
        space = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        space.activated.connect(self.play_pause_clicked.emit)
        
        r = QShortcut(QKeySequence(Qt.Key.Key_R), self)
        r.activated.connect(self.reset_clicked.emit)
        
        esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc.activated.connect(self.collapse_requested.emit)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Perfect rounded rect
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(),
                           self._radius, self._radius)
        
        # Pure black background
        painter.fillPath(path, QColor(0, 0, 0, 255))
        
        painter.end()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._is_dragging = False
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            if event.pos().y() < 50:
                self._is_dragging = True
                self.move(event.globalPosition().toPoint() - self._drag_pos)
    
    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._is_dragging = False
    
    def _on_add_task(self):
        text = self.task_input.text().strip()
        if text:
            self.task_added.emit(text)
            self.task_input.clear()
    
    def _on_slider_change(self, setting: str, value: int):
        if setting == "work_duration":
            self.work_duration_label.setText(f"{value}m")
        elif setting == "break_duration":
            self.break_duration_label.setText(f"{value}m")
        self.setting_changed.emit(setting, str(value))
    
    # ============== Public Methods ==============
    
    def update_timer(self, time_text: str, progress: float):
        self._time_text = time_text
        self._progress = progress
        self.timer_label.setText(time_text)
        self.progress_circle.set_progress(progress)
    
    def set_running(self, is_running: bool):
        self._is_running = is_running
        self.play_btn.set_icon_type("pause" if is_running else "play")
        
        if is_running:
            self.status_label.setText("Focusing...")
        else:
            self.status_label.setText("Break paused" if self._is_break else "Ready")
    
    def set_break_mode(self, is_break: bool):
        self._is_break = is_break
        self.progress_circle.set_break_mode(is_break)
        
        if is_break:
            self.status_label.setText("Break time")
            self.timer_label.setStyleSheet(f"""
                font-size: 42px;
                font-weight: 800;
                color: {Theme.BREAK_COLOR};
                letter-spacing: 2px;
            """)
        else:
            self.status_label.setText("Ready")
            self.timer_label.setStyleSheet(f"""
                font-size: 42px;
                font-weight: 800;
                color: {Theme.TEXT_PRIMARY};
                letter-spacing: 2px;
            """)
    
    def set_current_task(self, task: Optional[Task]):
        self._current_task = task
        if task:
            self.current_task_label.setText(task.name)
        else:
            self.current_task_label.setText("No task selected")
    
    def update_tasks_list(self, tasks: List[Task]):
        while self.tasks_layout.count() > 1:
            item = self.tasks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for task in tasks:
            item = TaskItemWidget(
                task.id, task.name, task.completed, 
                task.total_focus_seconds
            )
            item.toggled.connect(self.task_toggled.emit)
            item.deleted.connect(self.task_deleted.emit)
            item.selected.connect(self.task_selected.emit)
            self.tasks_layout.insertWidget(self.tasks_layout.count() - 1, item)
    
    def update_stats(self, today: DailyStats, weekly: List[DailyStats], total: dict):
        hours = today.total_focus_seconds // 3600
        minutes = (today.total_focus_seconds % 3600) // 60
        self.today_focus_label.setText(f"{hours}h {minutes}m")
        self.today_sessions_label.setText(f"{today.sessions_completed} sessions completed")
        
        while self.stats_layout.count() > 0:
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        max_seconds = max((s.total_focus_seconds for s in weekly), default=3600)
        max_seconds = max(max_seconds, 3600)
        
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for stat in weekly:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(stat.date)
                day_name = day_names[dt.weekday()]
            except:
                day_name = stat.date[-2:]
            
            bar = StatsBarWidget(day_name, stat.total_focus_seconds, max_seconds)
            self.stats_layout.addWidget(bar)
        
        total_hours = total.get('total_focus_seconds', 0) // 3600
        self.total_focus_label.setText(f"{total_hours}h total")
    
    def load_settings(self, settings: dict):
        work_duration = int(settings.get('work_duration', 25))
        break_duration = int(settings.get('break_duration', 5))
        alarm_sound = settings.get('alarm_sound', 'chime')
        
        self.work_duration_slider.setValue(work_duration)
        self.work_duration_label.setText(f"{work_duration}m")
        
        self.break_duration_slider.setValue(break_duration)
        self.break_duration_label.setText(f"{break_duration}m")
        
        index = self.alarm_combo.findText(alarm_sound.capitalize())
        if index >= 0:
            self.alarm_combo.setCurrentIndex(index)
    
    def get_geometry(self) -> QRect:
        return self.geometry()
    
    def set_weather(self, icon: str, temp: str, location: str):
        """Update the weather display"""
        if hasattr(self, 'weather_label'):
            self.weather_label.setText(f"{icon} {temp} • {location}")
