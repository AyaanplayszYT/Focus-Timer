"""
Mini Island View - Sleek pill-shaped floating widget.
Pure black with green accent - Dynamic Island style.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QVBoxLayout,
    QGraphicsDropShadowEffect, QApplication
)
from PySide6.QtCore import (
    Qt, Signal, QPoint, QPropertyAnimation, QEasingCurve, 
    Property, QRect, QSize, QTimer
)
from PySide6.QtGui import (
    QColor, QPainter, QPainterPath, QBrush, QPen, 
    QLinearGradient, QCursor
)
from typing import Optional

from ui.components import MiniCircularProgress, IconButton
from ui.styles import Theme


class MiniIslandWidget(QWidget):
    """
    Sleek pill-shaped floating timer widget.
    Pure black with smooth edges - Dynamic Island aesthetic.
    """
    
    expand_requested = Signal()
    play_pause_clicked = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Window flags for floating always-on-top widget
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Size
        self._width = Theme.ISLAND_WIDTH_MINI
        self._height = Theme.ISLAND_HEIGHT_MINI
        self._radius = Theme.ISLAND_RADIUS
        self.setFixedSize(self._width, self._height)
        
        # State
        self._is_running = False
        self._is_break = False
        self._task_name = "Ready"
        self._time_text = "25:00"
        self._progress = 0.0
        
        # Dragging
        self._drag_pos: Optional[QPoint] = None
        self._is_dragging = False
        
        # Animation
        self._opacity = 1.0
        
        self._setup_ui()
        self._center_on_screen()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 8, 8)
        layout.setSpacing(10)
        
        # Left side - Info section
        info_layout = QVBoxLayout()
        info_layout.setSpacing(0)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # Timer label - prominent
        self.timer_label = QLabel(self._time_text)
        self.timer_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 700;
            color: {Theme.TEXT_PRIMARY};
            letter-spacing: 0.5px;
        """)
        info_layout.addWidget(self.timer_label)
        
        # Task name - smaller, muted
        self.task_label = QLabel(self._task_name)
        self.task_label.setStyleSheet(f"""
            font-size: 10px;
            font-weight: 500;
            color: {Theme.TEXT_MUTED};
        """)
        self.task_label.setMaximumWidth(90)
        info_layout.addWidget(self.task_label)
        
        layout.addLayout(info_layout, 1)
        
        # Right side - Progress circle with play button inside
        self.progress_circle = MiniCircularProgress(32)
        layout.addWidget(self.progress_circle)
        
        # Play/Pause button - Green accent
        self.play_btn = IconButton("play", 32)
        self.play_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Theme.ACCENT};
                border: none;
                border-radius: 16px;
            }}
            QPushButton:hover {{
                background: {Theme.ACCENT_LIGHT};
            }}
            QPushButton:pressed {{
                background: {Theme.ACCENT_DARK};
            }}
        """)
        self.play_btn.clicked.connect(self._on_play_clicked)
        layout.addWidget(self.play_btn)
    
    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = 12
        self.move(x, y)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Perfect pill shape
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 
                           self._radius, self._radius)
        
        # Pure black fill
        painter.fillPath(path, QColor(0, 0, 0, 255))
        
        # Subtle inner glow when running
        if self._is_running:
            glow = QPainterPath()
            glow.addRoundedRect(1, 1, self.width()-2, self.height()-2,
                               self._radius-1, self._radius-1)
            if self._is_break:
                painter.setPen(QPen(QColor(250, 204, 21, 40), 1))
            else:
                painter.setPen(QPen(QColor(74, 222, 128, 40), 1))
            painter.drawPath(glow)
        
        painter.end()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._is_dragging = False
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self._is_dragging = True
            self.move(event.globalPosition().toPoint() - self._drag_pos)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._is_dragging:
                if not self.play_btn.geometry().contains(event.pos()):
                    self.expand_requested.emit()
            self._drag_pos = None
            self._is_dragging = False
    
    def _on_play_clicked(self):
        self.play_pause_clicked.emit()
    
    # ============== Public Methods ==============
    
    def update_timer(self, time_text: str, progress: float):
        self._time_text = time_text
        self._progress = progress
        self.timer_label.setText(time_text)
        self.progress_circle.set_progress(progress)
    
    def update_task(self, task_name: str):
        self._task_name = task_name
        display_name = task_name[:10] + "..." if len(task_name) > 10 else task_name
        self.task_label.setText(display_name)
    
    def set_running(self, is_running: bool):
        self._is_running = is_running
        self.play_btn.set_icon_type("pause" if is_running else "play")
        self.update()  # Redraw for glow effect
    
    def set_break_mode(self, is_break: bool):
        self._is_break = is_break
        self.progress_circle.set_break_mode(is_break)
        self.update()  # Redraw for glow color
        
        if is_break:
            self.task_label.setText("Break")
            self.timer_label.setStyleSheet(f"""
                font-size: 16px;
                font-weight: 700;
                color: {Theme.BREAK_COLOR};
                letter-spacing: 0.5px;
            """)
        else:
            self.timer_label.setStyleSheet(f"""
                font-size: 16px;
                font-weight: 700;
                color: {Theme.TEXT_PRIMARY};
                letter-spacing: 0.5px;
            """)
    
    def get_position(self) -> QPoint:
        return self.pos()
    
    def get_geometry(self) -> QRect:
        return self.geometry()
    
    # ============== Animation Properties ==============
    
    def get_opacity(self) -> float:
        return self._opacity
    
    def set_opacity(self, value: float):
        self._opacity = value
        self.setWindowOpacity(value)
    
    opacity = Property(float, get_opacity, set_opacity)
