"""
Quick Search Widget - Alt+Space activated search bar.
Spotlight/Alfred style quick search that opens in browser.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel,
    QListWidget, QListWidgetItem, QApplication
)
from PySide6.QtCore import (
    Qt, Signal, QPropertyAnimation, QEasingCurve, Property, QTimer
)
from PySide6.QtGui import (
    QColor, QPainter, QPainterPath, QKeySequence, QShortcut, QFont
)
from typing import Optional
import webbrowser
import urllib.parse

from ui.styles import Theme
from ui.icons import IconPainter
from ui.components import IconButton


class SearchWidget(QWidget):
    """
    Quick search widget - Alt+Space activated.
    Opens search queries in the default browser.
    """
    
    close_requested = Signal()
    
    # Popular search engines
    SEARCH_ENGINES = {
        "Google": "https://www.google.com/search?q=",
        "Brave": "https://search.brave.com/search?q=",
        "DuckDuckGo": "https://duckduckgo.com/?q=",
        "Bing": "https://www.bing.com/search?q=",
        "YouTube": "https://www.youtube.com/results?search_query=",
    }
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Window flags - floating, always on top, frameless
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Size
        self._width = 500
        self._height = 60
        self._radius = 16
        self._expanded_height = 200
        self._is_expanded = False
        
        self.setFixedSize(self._width, self._height)
        
        # Current search engine
        self._search_engine = "Google"
        
        # Search history for suggestions
        self._search_history = []
        
        self._setup_ui()
        self._setup_shortcuts()
        self._center_on_screen()
    
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(8)
        
        # Search bar container
        search_container = QHBoxLayout()
        search_container.setSpacing(10)
        
        # Search icon
        self.search_icon = QLabel("🔍")
        self.search_icon.setStyleSheet(f"font-size: 18px;")
        search_container.addWidget(self.search_icon)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search the web...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {Theme.TEXT_PRIMARY};
                font-size: 18px;
                font-weight: 500;
                padding: 4px 0;
            }}
            QLineEdit::placeholder {{
                color: {Theme.TEXT_MUTED};
            }}
        """)
        self.search_input.returnPressed.connect(self._perform_search)
        self.search_input.textChanged.connect(self._on_text_changed)
        search_container.addWidget(self.search_input, 1)
        
        # Search engine label
        self.engine_label = QLabel(f"↵ {self._search_engine}")
        self.engine_label.setStyleSheet(f"""
            font-size: 11px;
            color: {Theme.ACCENT};
            font-weight: 600;
            padding: 4px 10px;
            background: {Theme.ACCENT_MUTED};
            border-radius: 8px;
        """)
        self.engine_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.engine_label.mousePressEvent = self._cycle_search_engine
        search_container.addWidget(self.engine_label)
        
        main_layout.addLayout(search_container)
        
        # Suggestions list (hidden initially)
        self.suggestions_list = QListWidget()
        self.suggestions_list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                color: {Theme.TEXT_SECONDARY};
                padding: 8px 12px;
                border-radius: 8px;
                margin: 2px 0;
            }}
            QListWidget::item:hover {{
                background: {Theme.BG_HOVER};
                color: {Theme.TEXT_PRIMARY};
            }}
            QListWidget::item:selected {{
                background: {Theme.ACCENT_MUTED};
                color: {Theme.ACCENT};
            }}
        """)
        self.suggestions_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.suggestions_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.suggestions_list.itemClicked.connect(self._on_suggestion_clicked)
        self.suggestions_list.hide()
        main_layout.addWidget(self.suggestions_list)
        
        # Shortcut hints
        self.hints_label = QLabel("Tab: Switch Engine • Esc: Close • Enter: Search")
        self.hints_label.setStyleSheet(f"""
            font-size: 9px;
            color: {Theme.TEXT_MUTED};
        """)
        self.hints_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hints_label.hide()
        main_layout.addWidget(self.hints_label)
    
    def _setup_shortcuts(self):
        # Escape to close
        esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc.activated.connect(self._close_widget)
        
        # Tab to cycle search engines
        tab = QShortcut(QKeySequence(Qt.Key.Key_Tab), self)
        tab.activated.connect(self._cycle_search_engine)
        
        # Down arrow for suggestions
        down = QShortcut(QKeySequence(Qt.Key.Key_Down), self)
        down.activated.connect(self._select_next_suggestion)
        
        # Up arrow for suggestions
        up = QShortcut(QKeySequence(Qt.Key.Key_Up), self)
        up.activated.connect(self._select_prev_suggestion)
    
    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        # Position in upper third but ensure it stays on screen
        y = screen.height() // 4
        # Make sure widget doesn't go off screen when expanded
        max_y = screen.height() - self._expanded_height - 50
        y = min(y, max_y)
        y = max(50, y)  # At least 50px from top
        self.move(x, y)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(),
                           self._radius, self._radius)
        
        # Pure black fill with slight transparency
        painter.fillPath(path, QColor(0, 0, 0, 250))
        
        # Subtle border
        painter.setPen(QColor(255, 255, 255, 15))
        painter.drawPath(path)
        
        painter.end()
    
    def _cycle_search_engine(self, event=None):
        """Cycle through available search engines."""
        engines = list(self.SEARCH_ENGINES.keys())
        current_idx = engines.index(self._search_engine)
        next_idx = (current_idx + 1) % len(engines)
        self._search_engine = engines[next_idx]
        self.engine_label.setText(f"↵ {self._search_engine}")
    
    def _on_text_changed(self, text: str):
        """Handle text changes - show/hide suggestions."""
        if text:
            # Show suggestions based on history and common searches
            self._update_suggestions(text)
        else:
            self._collapse_suggestions()
    
    def _update_suggestions(self, query: str):
        """Update suggestions list."""
        self.suggestions_list.clear()
        
        # Quick search prefixes
        quick_searches = [
            f"Search {self._search_engine}: {query}",
            f"YouTube: {query}",
            f"Images: {query}",
        ]
        
        # Add items from history that match
        for item in self._search_history:
            if query.lower() in item.lower():
                quick_searches.append(item)
        
        for search in quick_searches[:5]:
            item = QListWidgetItem(f"  {search}")
            self.suggestions_list.addItem(item)
        
        if self.suggestions_list.count() > 0:
            self._expand_suggestions()
    
    def _expand_suggestions(self):
        """Expand to show suggestions."""
        if not self._is_expanded:
            self._is_expanded = True
            self.suggestions_list.show()
            self.hints_label.show()
            self.setFixedHeight(self._expanded_height)
    
    def _collapse_suggestions(self):
        """Collapse suggestions."""
        if self._is_expanded:
            self._is_expanded = False
            self.suggestions_list.hide()
            self.hints_label.hide()
            self.setFixedHeight(self._height)
    
    def _select_next_suggestion(self):
        """Select next item in suggestions."""
        if self.suggestions_list.isVisible():
            current = self.suggestions_list.currentRow()
            if current < self.suggestions_list.count() - 1:
                self.suggestions_list.setCurrentRow(current + 1)
    
    def _select_prev_suggestion(self):
        """Select previous item in suggestions."""
        if self.suggestions_list.isVisible():
            current = self.suggestions_list.currentRow()
            if current > 0:
                self.suggestions_list.setCurrentRow(current - 1)
    
    def _on_suggestion_clicked(self, item: QListWidgetItem):
        """Handle suggestion click."""
        text = item.text().strip()
        
        # Parse the suggestion
        if text.startswith("Search"):
            # Use current engine
            query = text.split(":", 1)[1].strip() if ":" in text else ""
            self._search_with_query(query, self._search_engine)
        elif text.startswith("YouTube:"):
            query = text.split(":", 1)[1].strip()
            self._search_with_query(query, "YouTube")
        elif text.startswith("Images:"):
            query = text.split(":", 1)[1].strip()
            url = f"https://www.google.com/search?tbm=isch&q={urllib.parse.quote(query)}"
            webbrowser.open(url)
            self._close_widget()
        else:
            # Direct search
            self._search_with_query(text, self._search_engine)
    
    def _perform_search(self):
        """Perform search with current input."""
        query = self.search_input.text().strip()
        if query:
            # Check if selected suggestion
            if self.suggestions_list.currentItem():
                self._on_suggestion_clicked(self.suggestions_list.currentItem())
            else:
                self._search_with_query(query, self._search_engine)
    
    def _search_with_query(self, query: str, engine: str):
        """Open search in browser."""
        if query:
            # Add to history
            if query not in self._search_history:
                self._search_history.insert(0, query)
                self._search_history = self._search_history[:20]  # Keep last 20
            
            # Build URL
            base_url = self.SEARCH_ENGINES.get(engine, self.SEARCH_ENGINES["Google"])
            url = base_url + urllib.parse.quote(query)
            
            # Open in default browser
            webbrowser.open(url)
            
            self._close_widget()
    
    def _close_widget(self):
        """Close the search widget."""
        self.search_input.clear()
        self._collapse_suggestions()
        self.hide()
        self.close_requested.emit()
    
    def show_and_focus(self):
        """Show widget and focus input."""
        self._center_on_screen()
        self.show()
        self.raise_()
        self.activateWindow()
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def set_search_engine(self, engine: str):
        """Set the default search engine."""
        if engine in self.SEARCH_ENGINES:
            self._search_engine = engine
            self.engine_label.setText(f"↵ {self._search_engine}")
    
    def get_search_engine(self) -> str:
        """Get current search engine."""
        return self._search_engine
