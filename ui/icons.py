"""
Custom SVG-style icons drawn with QPainter.
Clean, minimal icons for the Dynamic Island Timer.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QLinearGradient


class IconPainter:
    """Utility class for drawing custom icons."""
    
    @staticmethod
    def draw_play(painter: QPainter, rect: QRectF, color: QColor):
        """Draw a play triangle icon."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        
        # Calculate triangle points (slightly offset right for visual center)
        cx, cy = rect.center().x() + rect.width() * 0.05, rect.center().y()
        size = min(rect.width(), rect.height()) * 0.35
        
        path = QPainterPath()
        path.moveTo(cx - size * 0.4, cy - size * 0.5)
        path.lineTo(cx + size * 0.5, cy)
        path.lineTo(cx - size * 0.4, cy + size * 0.5)
        path.closeSubpath()
        
        painter.drawPath(path)
    
    @staticmethod
    def draw_pause(painter: QPainter, rect: QRectF, color: QColor):
        """Draw pause bars icon."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        
        cx, cy = rect.center().x(), rect.center().y()
        size = min(rect.width(), rect.height()) * 0.3
        bar_width = size * 0.3
        gap = size * 0.25
        height = size * 1.0
        
        # Left bar
        painter.drawRoundedRect(
            QRectF(cx - gap - bar_width, cy - height/2, bar_width, height),
            bar_width * 0.3, bar_width * 0.3
        )
        # Right bar
        painter.drawRoundedRect(
            QRectF(cx + gap, cy - height/2, bar_width, height),
            bar_width * 0.3, bar_width * 0.3
        )
    
    @staticmethod
    def draw_reset(painter: QPainter, rect: QRectF, color: QColor):
        """Draw a reset/refresh circular arrow icon."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = rect.center().x(), rect.center().y()
        size = min(rect.width(), rect.height()) * 0.32
        
        pen = QPen(color)
        pen.setWidth(max(2, int(size * 0.15)))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Draw arc (270 degrees)
        arc_rect = QRectF(cx - size, cy - size, size * 2, size * 2)
        painter.drawArc(arc_rect, 45 * 16, 270 * 16)
        
        # Draw arrow head
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        arrow_size = size * 0.35
        # Arrow at the end of arc (pointing down-right)
        path = QPainterPath()
        ax, ay = cx + size * 0.7, cy - size * 0.7
        path.moveTo(ax, ay - arrow_size * 0.6)
        path.lineTo(ax + arrow_size * 0.6, ay + arrow_size * 0.3)
        path.lineTo(ax - arrow_size * 0.3, ay + arrow_size * 0.3)
        path.closeSubpath()
        painter.drawPath(path)
    
    @staticmethod
    def draw_skip(painter: QPainter, rect: QRectF, color: QColor):
        """Draw skip/forward icon."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        
        cx, cy = rect.center().x(), rect.center().y()
        size = min(rect.width(), rect.height()) * 0.28
        
        # First triangle
        path1 = QPainterPath()
        path1.moveTo(cx - size * 0.8, cy - size * 0.5)
        path1.lineTo(cx + size * 0.1, cy)
        path1.lineTo(cx - size * 0.8, cy + size * 0.5)
        path1.closeSubpath()
        painter.drawPath(path1)
        
        # Second triangle
        path2 = QPainterPath()
        path2.moveTo(cx + size * 0.1, cy - size * 0.5)
        path2.lineTo(cx + size * 1.0, cy)
        path2.lineTo(cx + size * 0.1, cy + size * 0.5)
        path2.closeSubpath()
        painter.drawPath(path2)
    
    @staticmethod
    def draw_check(painter: QPainter, rect: QRectF, color: QColor):
        """Draw checkmark icon."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = rect.center().x(), rect.center().y()
        size = min(rect.width(), rect.height()) * 0.3
        
        pen = QPen(color)
        pen.setWidth(max(2, int(size * 0.2)))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        path = QPainterPath()
        path.moveTo(cx - size * 0.5, cy)
        path.lineTo(cx - size * 0.1, cy + size * 0.4)
        path.lineTo(cx + size * 0.6, cy - size * 0.4)
        painter.drawPath(path)
    
    @staticmethod
    def draw_plus(painter: QPainter, rect: QRectF, color: QColor):
        """Draw plus icon."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = rect.center().x(), rect.center().y()
        size = min(rect.width(), rect.height()) * 0.28
        
        pen = QPen(color)
        pen.setWidth(max(2, int(size * 0.18)))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        painter.drawLine(QPointF(cx - size, cy), QPointF(cx + size, cy))
        painter.drawLine(QPointF(cx, cy - size), QPointF(cx, cy + size))
    
    @staticmethod
    def draw_trash(painter: QPainter, rect: QRectF, color: QColor):
        """Draw trash/delete icon."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = rect.center().x(), rect.center().y()
        size = min(rect.width(), rect.height()) * 0.3
        
        pen = QPen(color)
        pen.setWidth(max(1, int(size * 0.12)))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Trash can body
        body_rect = QRectF(cx - size * 0.6, cy - size * 0.3, size * 1.2, size * 1.1)
        path = QPainterPath()
        path.moveTo(body_rect.topLeft())
        path.lineTo(body_rect.left() + size * 0.15, body_rect.bottom())
        path.lineTo(body_rect.right() - size * 0.15, body_rect.bottom())
        path.lineTo(body_rect.topRight())
        painter.drawPath(path)
        
        # Lid
        painter.drawLine(
            QPointF(cx - size * 0.8, cy - size * 0.4),
            QPointF(cx + size * 0.8, cy - size * 0.4)
        )
        
        # Handle
        painter.drawLine(
            QPointF(cx - size * 0.25, cy - size * 0.4),
            QPointF(cx - size * 0.25, cy - size * 0.6)
        )
        painter.drawLine(
            QPointF(cx - size * 0.25, cy - size * 0.6),
            QPointF(cx + size * 0.25, cy - size * 0.6)
        )
        painter.drawLine(
            QPointF(cx + size * 0.25, cy - size * 0.6),
            QPointF(cx + size * 0.25, cy - size * 0.4)
        )
    
    @staticmethod
    def draw_collapse(painter: QPainter, rect: QRectF, color: QColor):
        """Draw collapse/chevron up icon."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = rect.center().x(), rect.center().y()
        size = min(rect.width(), rect.height()) * 0.25
        
        pen = QPen(color)
        pen.setWidth(max(2, int(size * 0.2)))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        path = QPainterPath()
        path.moveTo(cx - size, cy + size * 0.3)
        path.lineTo(cx, cy - size * 0.3)
        path.lineTo(cx + size, cy + size * 0.3)
        painter.drawPath(path)
    
    @staticmethod
    def draw_settings(painter: QPainter, rect: QRectF, color: QColor):
        """Draw settings/gear icon."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = rect.center().x(), rect.center().y()
        size = min(rect.width(), rect.height()) * 0.32
        
        pen = QPen(color)
        pen.setWidth(max(1, int(size * 0.12)))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Outer circle with notches
        painter.drawEllipse(QRectF(cx - size * 0.4, cy - size * 0.4, size * 0.8, size * 0.8))
        
        # Inner circle
        painter.drawEllipse(QRectF(cx - size * 0.2, cy - size * 0.2, size * 0.4, size * 0.4))
        
        # Gear teeth (6 lines radiating out)
        import math
        for i in range(6):
            angle = i * math.pi / 3
            x1 = cx + math.cos(angle) * size * 0.5
            y1 = cy + math.sin(angle) * size * 0.5
            x2 = cx + math.cos(angle) * size * 0.8
            y2 = cy + math.sin(angle) * size * 0.8
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
    
    @staticmethod
    def draw_expand(painter: QPainter, rect: QRectF, color: QColor):
        """Draw expand arrows icon."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = rect.center().x(), rect.center().y()
        size = min(rect.width(), rect.height()) * 0.25
        
        pen = QPen(color)
        pen.setWidth(max(2, int(size * 0.18)))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        # Down chevron
        path = QPainterPath()
        path.moveTo(cx - size, cy - size * 0.3)
        path.lineTo(cx, cy + size * 0.3)
        path.lineTo(cx + size, cy - size * 0.3)
        painter.drawPath(path)
    
    @staticmethod
    def draw_close(painter: QPainter, rect: QRectF, color: QColor):
        """Draw close X icon."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = rect.center().x(), rect.center().y()
        size = min(rect.width(), rect.height()) * 0.22
        
        pen = QPen(color)
        pen.setWidth(max(2, int(size * 0.2)))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # Draw X
        painter.drawLine(QPointF(cx - size, cy - size), QPointF(cx + size, cy + size))
        painter.drawLine(QPointF(cx + size, cy - size), QPointF(cx - size, cy + size))
