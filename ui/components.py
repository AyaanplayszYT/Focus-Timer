"""
Reusable UI components for the Dynamic Island Timer.
Pure black with green accent - Dynamic Island style.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QPushButton, QCheckBox, QLineEdit, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize, QPropertyAnimation, QEasingCurve, Property, QRect
from PySide6.QtGui import QColor, QPainter, QPainterPath, QBrush, QPen, QFont, QPixmap
from typing import Optional
from ui.icons import IconPainter
from ui.styles import Theme


class CircularProgress(QWidget):
    """Circular progress indicator for timer display."""
    
    def __init__(self, size: int = 180, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._progress = 0.0
        self._size = size
        self._line_width = 5
        self._is_break = False
        
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
    def get_progress(self) -> float:
        return self._progress
    
    def set_progress(self, value: float):
        self._progress = max(0.0, min(1.0, value))
        self.update()
    
    progress = Property(float, get_progress, set_progress)
    
    def set_break_mode(self, is_break: bool):
        self._is_break = is_break
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        margin = self._line_width + 2
        rect = self.rect().adjusted(margin, margin, -margin, -margin)
        
        # Background track - very subtle
        bg_color = QColor(255, 255, 255, 10)
        painter.setPen(QPen(bg_color, self._line_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawEllipse(rect)
        
        # Progress arc - green or yellow
        if self._progress > 0:
            if self._is_break:
                progress_color = QColor(Theme.SECONDARY)  # Yellow for break
            else:
                progress_color = QColor(Theme.ACCENT)  # Green for work
            
            painter.setPen(QPen(progress_color, self._line_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            
            start_angle = 90 * 16
            span_angle = -int(self._progress * 360 * 16)
            painter.drawArc(rect, start_angle, span_angle)
        
        painter.end()


class MiniCircularProgress(QWidget):
    """Small circular progress for mini island view."""
    
    def __init__(self, size: int = 32, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._progress = 0.0
        self._size = size
        self._line_width = 2.5
        self._is_break = False
        
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
    def get_progress(self) -> float:
        return self._progress
    
    def set_progress(self, value: float):
        self._progress = max(0.0, min(1.0, value))
        self.update()
    
    progress = Property(float, get_progress, set_progress)
    
    def set_break_mode(self, is_break: bool):
        self._is_break = is_break
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        margin = self._line_width + 1
        rect = self.rect().adjusted(margin, margin, -margin, -margin)
        
        # Background - subtle
        bg_color = QColor(255, 255, 255, 12)
        painter.setPen(QPen(bg_color, self._line_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawEllipse(rect)
        
        # Progress
        if self._progress > 0:
            color = QColor(Theme.SECONDARY) if self._is_break else QColor(Theme.ACCENT)
            painter.setPen(QPen(color, self._line_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            
            start_angle = 90 * 16
            span_angle = -int(self._progress * 360 * 16)
            painter.drawArc(rect, start_angle, span_angle)
        
        painter.end()


class IconButton(QPushButton):
    """Custom icon button using painted icons."""
    
    ICON_TYPES = ['play', 'pause', 'reset', 'skip', 'check', 'plus', 'trash', 'collapse', 'settings', 'expand', 'close']
    
    def __init__(self, icon_type: str = "play", size: int = 32, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._icon_type = icon_type
        self._size = size
        self._icon_size = int(size * 0.5)
        self._hovered = False
        
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: {Theme.BG_ELEVATED};
                border: none;
                border-radius: {size // 2}px;
            }}
            QPushButton:hover {{
                background: {Theme.BG_HOVER};
            }}
            QPushButton:pressed {{
                background: {Theme.BG_ACTIVE};
            }}
        """)
    
    def set_icon_type(self, icon_type: str):
        self._icon_type = icon_type
        self.update()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Center the icon
        x = (self._size - self._icon_size) // 2
        y = (self._size - self._icon_size) // 2
        rect = QRect(x, y, self._icon_size, self._icon_size)
        
        color = QColor(Theme.ACCENT_LIGHT if self.underMouse() else Theme.TEXT_PRIMARY)
        
        # Draw appropriate icon
        if self._icon_type == 'play':
            IconPainter.draw_play(painter, rect, color)
        elif self._icon_type == 'pause':
            IconPainter.draw_pause(painter, rect, color)
        elif self._icon_type == 'reset':
            IconPainter.draw_reset(painter, rect, color)
        elif self._icon_type == 'skip':
            IconPainter.draw_skip(painter, rect, color)
        elif self._icon_type == 'check':
            IconPainter.draw_check(painter, rect, color)
        elif self._icon_type == 'plus':
            IconPainter.draw_plus(painter, rect, color)
        elif self._icon_type == 'trash':
            IconPainter.draw_trash(painter, rect, color)
        elif self._icon_type == 'collapse':
            IconPainter.draw_collapse(painter, rect, color)
        elif self._icon_type == 'settings':
            IconPainter.draw_settings(painter, rect, color)
        elif self._icon_type == 'expand':
            IconPainter.draw_expand(painter, rect, color)
        elif self._icon_type == 'close':
            IconPainter.draw_close(painter, rect, color)
        
        painter.end()


class ControlButton(QPushButton):
    """Large control button for play/pause - Green accent."""
    
    def __init__(self, icon_type: str = "play", size: int = 48, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._icon_type = icon_type
        self._size = size
        self._icon_size = int(size * 0.45)
        
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: {Theme.ACCENT};
                border: none;
                border-radius: {size // 2}px;
            }}
            QPushButton:hover {{
                background: {Theme.ACCENT_LIGHT};
            }}
            QPushButton:pressed {{
                background: {Theme.ACCENT_DARK};
            }}
        """)
    
    def set_icon_type(self, icon_type: str):
        self._icon_type = icon_type
        self.update()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        x = (self._size - self._icon_size) // 2
        y = (self._size - self._icon_size) // 2
        rect = QRect(x, y, self._icon_size, self._icon_size)
        
        color = QColor(Theme.BG_DARKEST)
        
        if self._icon_type == 'play':
            IconPainter.draw_play(painter, rect, color)
        elif self._icon_type == 'pause':
            IconPainter.draw_pause(painter, rect, color)
        
        painter.end()


class TaskItemWidget(QWidget):
    """Individual task item with checkbox and delete button."""
    
    toggled = Signal(int, bool)
    deleted = Signal(int)
    selected = Signal(int)
    
    def __init__(self, task_id: int, name: str, completed: bool = False, 
                 focus_time: int = 0, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.task_id = task_id
        self._completed = completed
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(48)
        self._apply_style()
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 8, 8)
        layout.setSpacing(10)
        
        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(completed)
        self.checkbox.toggled.connect(self._on_toggle)
        self.checkbox.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {Theme.BORDER_LIGHT};
                background: {Theme.BG_DARK};
            }}
            QCheckBox::indicator:checked {{
                background: {Theme.ACCENT};
                border-color: {Theme.ACCENT};
            }}
        """)
        layout.addWidget(self.checkbox)
        
        # Task info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(1)
        
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet(f"""
            color: {Theme.TEXT_MUTED if completed else Theme.TEXT_PRIMARY};
            font-size: 12px;
            font-weight: 500;
            text-decoration: {"line-through" if completed else "none"};
        """)
        info_layout.addWidget(self.name_label)
        
        # Focus time
        hours = focus_time // 3600
        minutes = (focus_time % 3600) // 60
        time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        self.time_label = QLabel(time_str if focus_time > 0 else "0m")
        self.time_label.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-size: 10px;")
        info_layout.addWidget(self.time_label)
        
        layout.addLayout(info_layout, 1)
        
        # Delete button
        self.delete_btn = IconButton("trash", 28)
        self.delete_btn.clicked.connect(lambda: self.deleted.emit(self.task_id))
        self.delete_btn.setToolTip("Delete")
        layout.addWidget(self.delete_btn)
    
    def _apply_style(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: {Theme.BG_ELEVATED};
                border-radius: 10px;
            }}
            QWidget:hover {{
                background: {Theme.BG_HOVER};
            }}
        """)
    
    def _on_toggle(self, checked: bool):
        self._completed = checked
        self.name_label.setStyleSheet(f"""
            color: {Theme.TEXT_MUTED if checked else Theme.TEXT_PRIMARY};
            font-size: 12px;
            font-weight: 500;
            text-decoration: {"line-through" if checked else "none"};
        """)
        self._apply_style()
        self.toggled.emit(self.task_id, checked)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.checkbox.geometry().contains(event.pos()) and \
               not self.delete_btn.geometry().contains(event.pos()):
                self.selected.emit(self.task_id)
        super().mousePressEvent(event)


class StatsBarWidget(QWidget):
    """Horizontal bar chart for stats display."""
    
    def __init__(self, label: str, value: float, max_value: float, 
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._value = value
        self._max_value = max_value
        
        self.setFixedHeight(28)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Label row
        label_layout = QHBoxLayout()
        self.label = QLabel(label)
        self.label.setStyleSheet(f"font-size: 10px; color: {Theme.TEXT_MUTED}; font-weight: 500;")
        self.label.setFixedWidth(30)
        label_layout.addWidget(self.label)
        
        self.value_label = QLabel(self._format_value(value))
        self.value_label.setStyleSheet(f"font-size: 10px; color: {Theme.TEXT_SECONDARY};")
        label_layout.addWidget(self.value_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(label_layout)
        
        # Bar container
        self.bar_container = QWidget()
        self.bar_container.setFixedHeight(3)
        self.bar_container.setStyleSheet(f"""
            background: rgba(74, 222, 128, 0.15);
            border-radius: 2px;
        """)
        
        self.bar_fill = QWidget(self.bar_container)
        self.bar_fill.setFixedHeight(3)
        self.bar_fill.setStyleSheet(f"""
            background: {Theme.ACCENT};
            border-radius: 2px;
        """)
        
        layout.addWidget(self.bar_container)
        
        self._update_fill()
    
    def _format_value(self, seconds: float) -> str:
        hours = int(seconds) // 3600
        minutes = (int(seconds) % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    def _update_fill(self):
        if self._max_value > 0:
            ratio = min(self._value / self._max_value, 1.0)
            container_width = self.bar_container.width() or 200
            fill_width = int(container_width * ratio)
            self.bar_fill.setFixedWidth(max(fill_width, 0))
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_fill()
    
    def set_value(self, value: float, max_value: float):
        self._value = value
        self._max_value = max_value
        self.value_label.setText(self._format_value(value))
        self._update_fill()


class GlassCard(QFrame):
    """Card container for dark theme."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setStyleSheet(f"""
            QFrame {{
                background: {Theme.BG_ELEVATED};
                border-radius: 14px;
            }}
        """)


class AnimatedButton(QPushButton):
    """Button with scale animation on press."""
    
    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self._scale = 1.0
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._scale_anim = QPropertyAnimation(self, b"scale")
        self._scale_anim.setDuration(100)
        self._scale_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def get_scale(self) -> float:
        return self._scale
    
    def set_scale(self, value: float):
        self._scale = value
        self.update()
    
    scale = Property(float, get_scale, set_scale)
    
    def enterEvent(self, event):
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(1.02)
        self._scale_anim.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(1.0)
        self._scale_anim.start()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(0.95)
        self._scale_anim.start()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(1.0)
        self._scale_anim.start()
        super().mouseReleaseEvent(event)
