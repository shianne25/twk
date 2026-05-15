from PyQt6.QtWidgets import QApplication, QLabel, QStyle, QWidget, QSystemTrayIcon, QMenu
from PyQt6.QtCore import Qt, QPoint
import sys
from PyQt6.QtGui import QCursor, QIcon, QAction

class SuggestionOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.setup_label()

    def setup_window(self):
        # Set these window flags:
        # - frameless (no title bar)
        # - always on top
        # - transparent background
        # - tool hint (so it doesn't appear in the taskbar)
        # Hint: look up Qt.WindowType flags, you need 4 of them combined with |
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool | 
            Qt.WindowType.ToolTip
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # transparent background
        self.setStyleSheet("background: transparent;")
        self.hide()

    def setup_label(self):
        # Create a QLabel that will show the suggestion text
        # Style it as a dark pill with white text
        # Hint: use border-radius, padding, background-color in the stylesheet
        self.label = QLabel(self)
        self.label.setStyleSheet(
            """
            color: white;
            background-color: black;
            border-radius: 15px;
            padding: 10px 20px;
            """
        )

    def show_suggestion(self, slang, definition):
        # Set the label text to show slang and a hint to press Tab
        # Then move the widget to (x, y) and show it
        self.label.setText(f"{slang} - (press Tab to enter)")
        self.label.adjustSize()
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