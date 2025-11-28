"""
Fullscreen Focus Mode - Immersive timer display.
Shows time, greeting, weather, and timer in a beautiful fullscreen view.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsOpacityEffect, QApplication
)
from PySide6.QtCore import (
    Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, Property
)
from PySide6.QtGui import (
    QColor, QPainter, QPainterPath, QLinearGradient, QFont,
    QKeySequence, QShortcut
)
from datetime import datetime
from typing import Optional

from ui.styles import Theme
from ui.components import IconButton


class FullscreenMode(QWidget):
    """
    Fullscreen immersive focus mode.
    Shows current time, greeting, weather, and timer.
    """
    
    close_requested = Signal()
    play_pause_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        # State
        self._time_text = "25:00"
        self._progress = 0.0
        self._is_running = False
        self._is_break = False
        self._weather_text = ""
        self._weather_icon = ""
        self._weather_temp = ""
        
        # Clock update timer
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.setInterval(1000)
        
        self._setup_ui()
        self._setup_shortcuts()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(20)
        
        # Top bar with close button
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        
        self.close_btn = QPushButton("Exit Focus Mode")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px;
                padding: 10px 24px;
                color: {Theme.TEXT_SECONDARY};
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.12);
                color: {Theme.TEXT_PRIMARY};
            }}
        """)
        self.close_btn.clicked.connect(self.close_requested.emit)
        top_bar.addWidget(self.close_btn)
        
        layout.addLayout(top_bar)
        layout.addStretch()
        
        # Center content
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.setSpacing(16)
        
        # Greeting
        self.greeting_label = QLabel()
        self.greeting_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.greeting_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 300;
            color: {Theme.TEXT_SECONDARY};
            letter-spacing: 2px;
        """)
        center_layout.addWidget(self.greeting_label)
        
        # Current time (large)
        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clock_label.setStyleSheet(f"""
            font-size: 120px;
            font-weight: 200;
            color: {Theme.TEXT_PRIMARY};
            letter-spacing: 4px;
        """)
        center_layout.addWidget(self.clock_label)
        
        # Date
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 400;
            color: {Theme.TEXT_MUTED};
            letter-spacing: 1px;
        """)
        center_layout.addWidget(self.date_label)
        
        # Weather
        self.weather_label = QLabel()
        self.weather_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.weather_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 400;
            color: {Theme.TEXT_SECONDARY};
            margin-top: 20px;
        """)
        center_layout.addWidget(self.weather_label)
        
        # Timer section (only visible when timer is active)
        self.timer_container = QWidget()
        timer_layout = QVBoxLayout(self.timer_container)
        timer_layout.setContentsMargins(0, 40, 0, 0)
        timer_layout.setSpacing(8)
        timer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Timer status
        self.timer_status = QLabel("Focus Timer")
        self.timer_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_status.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {Theme.ACCENT};
            letter-spacing: 2px;
            text-transform: uppercase;
        """)
        timer_layout.addWidget(self.timer_status)
        
        # Timer display
        self.timer_display = QLabel(self._time_text)
        self.timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_display.setStyleSheet(f"""
            font-size: 64px;
            font-weight: 600;
            color: {Theme.ACCENT};
            letter-spacing: 2px;
        """)
        timer_layout.addWidget(self.timer_display)
        
        # Play/Pause hint
        self.hint_label = QLabel("Press SPACE to pause")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet(f"""
            font-size: 12px;
            color: {Theme.TEXT_MUTED};
        """)
        timer_layout.addWidget(self.hint_label)
        
        center_layout.addWidget(self.timer_container)
        
        layout.addLayout(center_layout)
        layout.addStretch()
        
        # Bottom hint
        bottom_hint = QLabel("Press ESC to exit • Press SPACE to start/pause timer")
        bottom_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_hint.setStyleSheet(f"""
            font-size: 11px;
            color: {Theme.TEXT_MUTED};
            opacity: 0.5;
        """)
        layout.addWidget(bottom_hint)
    
    def _setup_shortcuts(self):
        # ESC to close
        esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc.activated.connect(self.close_requested.emit)
        
        # Space for play/pause
        space = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        space.activated.connect(self.play_pause_clicked.emit)
    
    def _update_clock(self):
        now = datetime.now()
        
        # Update time
        self.clock_label.setText(now.strftime("%H:%M"))
        
        # Update date
        self.date_label.setText(now.strftime("%A, %B %d"))
        
        # Update greeting
        hour = now.hour
        if 5 <= hour < 12:
            greeting = "Good Morning"
        elif 12 <= hour < 17:
            greeting = "Good Afternoon"
        elif 17 <= hour < 21:
            greeting = "Good Evening"
        else:
            greeting = "Good Night"
        
        self.greeting_label.setText(greeting)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Deep gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(8, 8, 10))
        gradient.setColorAt(0.5, QColor(12, 12, 15))
        gradient.setColorAt(1, QColor(5, 5, 6))
        
        painter.fillRect(self.rect(), gradient)
        
        # Subtle accent glow at top
        glow = QLinearGradient(0, 0, 0, 200)
        glow.setColorAt(0, QColor(6, 182, 212, 8))
        glow.setColorAt(1, QColor(6, 182, 212, 0))
        painter.fillRect(0, 0, self.width(), 200, glow)
        
        painter.end()
    
    def showEvent(self, event):
        super().showEvent(event)
        self._update_clock()
        self._clock_timer.start()
        
        # Fullscreen
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
    
    def hideEvent(self, event):
        super().hideEvent(event)
        self._clock_timer.stop()
    
    # ============== Public Methods ==============
    
    def update_timer(self, time_text: str, progress: float):
        self._time_text = time_text
        self._progress = progress
        self.timer_display.setText(time_text)
    
    def set_running(self, is_running: bool):
        self._is_running = is_running
        
        if is_running:
            self.hint_label.setText("Press SPACE to pause")
            self.timer_status.setText("FOCUSING" if not self._is_break else "BREAK")
        else:
            self.hint_label.setText("Press SPACE to start")
            self.timer_status.setText("PAUSED")
    
    def set_break_mode(self, is_break: bool):
        self._is_break = is_break
        
        if is_break:
            self.timer_status.setText("BREAK TIME")
            self.timer_display.setStyleSheet(f"""
                font-size: 64px;
                font-weight: 600;
                color: {Theme.BREAK_COLOR};
                letter-spacing: 2px;
            """)
            self.timer_status.setStyleSheet(f"""
                font-size: 14px;
                font-weight: 600;
                color: {Theme.BREAK_COLOR};
                letter-spacing: 2px;
                text-transform: uppercase;
            """)
        else:
            self.timer_status.setText("FOCUS TIMER")
            self.timer_display.setStyleSheet(f"""
                font-size: 64px;
                font-weight: 600;
                color: {Theme.ACCENT};
                letter-spacing: 2px;
            """)
            self.timer_status.setStyleSheet(f"""
                font-size: 14px;
                font-weight: 600;
                color: {Theme.ACCENT};
                letter-spacing: 2px;
                text-transform: uppercase;
            """)
    
    def set_weather(self, icon: str, temp: str, condition: str):
        self._weather_icon = icon
        self._weather_temp = temp
        self._weather_text = condition
        self.weather_label.setText(f"{icon}  {temp}  •  {condition}")
    
    def show_timer(self, visible: bool = True):
        self.timer_container.setVisible(visible)
