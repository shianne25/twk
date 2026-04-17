from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt, QPoint
import sys

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

    def show_suggestion(self, slang, definition, x, y):
        # Set the label text to show slang and a hint to press Tab
        # Then move the widget to (x, y) and show it
        self.label.setText(f"{slang} - (press Tab to enter)")
        self.label.adjustSize()
        self.adjustSize()
        self.move(QPoint(x, y))
        self.show()

    def hide_suggestion(self):
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = SuggestionOverlay()
    # Test it at a fixed position first
    overlay.show_suggestion("i'm dead", "Extremely tired", 500, 500)
    sys.exit(app.exec())