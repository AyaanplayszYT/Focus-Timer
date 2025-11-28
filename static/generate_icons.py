"""
Generate app icon for the Dynamic Island Timer.
Creates a mint-colored timer icon.
"""

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QFont, QIcon
from PySide6.QtCore import Qt, QRect
import sys
import os


def create_icon(size: int = 256) -> QPixmap:
    """Create the app icon."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Background circle (dark)
    painter.setBrush(QBrush(QColor(25, 25, 35)))
    painter.setPen(Qt.PenStyle.NoPen)
    margin = size * 0.05
    painter.drawEllipse(int(margin), int(margin), 
                        int(size - 2*margin), int(size - 2*margin))
    
    # Progress arc (mint)
    pen = QPen(QColor("#5EEAD4"))
    pen.setWidth(int(size * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    
    arc_margin = size * 0.15
    arc_rect = QRect(int(arc_margin), int(arc_margin),
                     int(size - 2*arc_margin), int(size - 2*arc_margin))
    
    # Draw 270 degree arc (75% progress)
    painter.drawArc(arc_rect, 90 * 16, -270 * 16)
    
    # Center dot
    painter.setBrush(QBrush(QColor("#5EEAD4")))
    painter.setPen(Qt.PenStyle.NoPen)
    center = size // 2
    dot_size = size * 0.12
    painter.drawEllipse(int(center - dot_size/2), int(center - dot_size/2),
                        int(dot_size), int(dot_size))
    
    painter.end()
    return pixmap


def save_icons(output_dir: str):
    """Save icons in various sizes."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Create icons at different sizes
    sizes = [16, 32, 48, 64, 128, 256]
    
    for size in sizes:
        pixmap = create_icon(size)
        pixmap.save(os.path.join(output_dir, f'icon_{size}.png'))
    
    # Save main icon
    main_icon = create_icon(256)
    main_icon.save(os.path.join(output_dir, 'icon.png'))
    
    print(f"Created icons in {output_dir}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(script_dir, 'icons')
    save_icons(icons_dir)
    
    sys.exit(0)
