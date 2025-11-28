"""
Dynamic Island styles - Pure black with vibrant green accents.
Matching the sleek Apple Dynamic Island aesthetic.
"""

from PySide6.QtGui import QColor, QFont, QFontDatabase
from PySide6.QtCore import Qt
import os


class Theme:
    """Pure black theme with vibrant green accent - Like the reference image."""
    
    # Core colors - Pure blacks
    BG_DARKEST = "#000000"        # Pure black
    BG_DARK = "#0A0A0A"           # Near black  
    BG_BASE = "#111111"           # Card backgrounds
    BG_ELEVATED = "#1A1A1A"       # Elevated surfaces
    BG_HOVER = "#222222"          # Hover states
    BG_ACTIVE = "#2A2A2A"         # Active/pressed
    
    # Accent - Vibrant Green (matching image)
    ACCENT = "#4ADE80"            # Main green
    ACCENT_LIGHT = "#86EFAC"      # Lighter green
    ACCENT_DARK = "#22C55E"       # Darker green
    ACCENT_MUTED = "rgba(74, 222, 128, 0.15)"
    ACCENT_GLOW = "rgba(74, 222, 128, 0.3)"
    
    # Secondary accent - Yellow/Gold for stats
    SECONDARY = "#FACC15"
    SECONDARY_MUTED = "rgba(250, 204, 21, 0.15)"
    
    # Text - High contrast
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#A3A3A3"
    TEXT_MUTED = "#737373"
    TEXT_DISABLED = "#525252"
    
    # Semantic
    SUCCESS = "#4ADE80"
    WARNING = "#FACC15"
    DANGER = "#F87171"
    BREAK_COLOR = "#FACC15"
    
    # Effects
    BORDER = "rgba(255, 255, 255, 0.06)"
    BORDER_LIGHT = "rgba(255, 255, 255, 0.12)"
    GLOW_SHADOW = "rgba(74, 222, 128, 0.25)"
    
    # Island dimensions - More compact mini pill
    ISLAND_WIDTH_MINI = 240
    ISLAND_HEIGHT_MINI = 48
    ISLAND_RADIUS = 24
    
    # Expanded dimensions  
    ISLAND_WIDTH_EXPANDED = 340
    ISLAND_HEIGHT_EXPANDED = 440
    EXPANDED_RADIUS = 24
    
    # Animation
    EXPAND_DURATION = 400
    COLLAPSE_DURATION = 300
    FADE_DURATION = 150
    
    @staticmethod
    def load_fonts(app_path: str):
        fonts_dir = os.path.join(app_path, "fonts")
        if os.path.exists(fonts_dir):
            for font_file in os.listdir(fonts_dir):
                if font_file.endswith(('.ttf', '.otf')):
                    QFontDatabase.addApplicationFont(os.path.join(fonts_dir, font_file))
    
    @staticmethod
    def get_font(size: int = 12, weight: str = "normal") -> QFont:
        font = QFont("Segoe UI", size)
        weights = {
            "bold": QFont.Weight.Bold,
            "semibold": QFont.Weight.DemiBold,
            "medium": QFont.Weight.Medium,
            "light": QFont.Weight.Light
        }
        font.setWeight(weights.get(weight, QFont.Weight.Normal))
        return font


MIDNIGHT_STYLE = """
* {
    font-family: 'Segoe UI', -apple-system, sans-serif;
    outline: none;
}

QWidget {
    color: #FFFFFF;
    background: transparent;
}

QPushButton {
    background: #1A1A1A;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 8px 14px;
    color: #FFFFFF;
    font-size: 12px;
    font-weight: 500;
}

QPushButton:hover {
    background: #222222;
    border-color: rgba(255,255,255,0.1);
}

QPushButton:pressed {
    background: #111111;
}

QLineEdit {
    background: #0A0A0A;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 10px 14px;
    color: #FFFFFF;
    font-size: 13px;
    selection-background-color: rgba(74,222,128,0.3);
}

QLineEdit:focus {
    border-color: rgba(74,222,128,0.5);
}

QLineEdit::placeholder {
    color: #525252;
}

QScrollArea {
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    background: transparent;
    width: 4px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: rgba(255,255,255,0.1);
    border-radius: 2px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255,255,255,0.15);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
    height: 0;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid rgba(255,255,255,0.15);
    background: #0A0A0A;
}

QCheckBox::indicator:checked {
    background: #4ADE80;
    border-color: #4ADE80;
}

QCheckBox::indicator:hover {
    border-color: rgba(74,222,128,0.5);
}

QSlider::groove:horizontal {
    background: rgba(255,255,255,0.06);
    height: 4px;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #4ADE80;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::sub-page:horizontal {
    background: #4ADE80;
    border-radius: 2px;
}

QComboBox {
    background: #111111;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 8px 12px;
    color: #FFFFFF;
    font-size: 12px;
}

QComboBox:hover {
    border-color: rgba(255,255,255,0.1);
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background: #111111;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 4px;
    selection-background-color: rgba(74,222,128,0.2);
}

QToolTip {
    background: #1A1A1A;
    color: #FFFFFF;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 11px;
}
"""
