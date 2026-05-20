from PyQt6.QtWidgets import QApplication, QLabel, QStyle, QWidget, QSystemTrayIcon, QMenu, QHBoxLayout
from PyQt6.QtCore import Qt, QPoint
import sys
from PyQt6.QtGui import QCursor, QIcon, QAction

class SuggestionOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.setup_label()

    def setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.ToolTip
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setStyleSheet("""
            background-color: white;
            border-radius: 10px;
            border: 1px solid #D1D1D6;
        """)
        self.hide()

    def setup_label(self):
        from PyQt6.QtWidgets import QHBoxLayout
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(10)

        self.slang_label = QLabel(self)
        self.slang_label.setStyleSheet("""
            color: #007AFF;
            font-size: 14px;
            font-weight: 600;
            background: white;
            border: none;
        """)

        self.divider = QLabel("|", self)
        self.divider.setStyleSheet("""
            color: #D1D1D6;
            font-size: 14px;
            background: white;
            border: none;
        """)

        self.hint_label = QLabel("tab ↵", self)
        self.hint_label.setStyleSheet("""
            color: #8E8E93;
            font-size: 13px;
            background: white;
            border: none;
        """)

        layout.addWidget(self.slang_label)
        layout.addWidget(self.divider)
        layout.addWidget(self.hint_label)
        self.setLayout(layout)

    def show_suggestion(self, slang, definition):
        self.slang_label.setText(slang)
        self.adjustSize()
        cursor_pos = QCursor.pos()
        self.move(QPoint(cursor_pos.x() + 10, cursor_pos.y() - 60))
        self.show()
    
    def hide_suggestion(self):
        self.hide()

class SystemTray(QSystemTrayIcon):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setup_tray()

    def setup_tray(self):
        # Set an icon — for now use a built-in Qt icon
        # Hint: look up QStyle.StandardPixmap for built-in icons
        # or just use QIcon() with a path to a .ico file if you have one
        self.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.setToolTip("TWK - Slang Assistant")
        self.setVisible(True)

        # Create the right-click menu
        menu = QMenu()
        
        # Add a "Quit" action that closes the app
        # Hint: QAction takes a label string and a parent
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.app.quit)
        
        menu.addAction(quit_action)
        self.setContextMenu(menu)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = SuggestionOverlay()
    tray = SystemTray(app)
    # Test it at a fixed position first
    sys.exit(app.exec())