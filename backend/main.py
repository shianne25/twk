from pynput import keyboard
import threading
from backend.matcher import CACHE, match
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication
from frontend.overlay import SuggestionOverlay, SystemTray
import sys
from pynput.keyboard import Controller, Key
kb_controller = Controller()

# The bridge — safely connects listener thread to the UI thread
class Bridge(QObject):
    suggestion_ready = pyqtSignal(str, str)  # emits (slang, definition)
    hide_overlay = pyqtSignal()              # emits when suggestion should disappear

# The buffer stores the last N characters the user typed
buffer = ""
MAX_BUFFER = 50

# This will hold the debounce timer so we can reset it on each keypress
debounce_timer = None
DEBOUNCE_SECONDS = 0.4

bridge = None
overlay = None
listener = None
is_replacing = False

current_slang = None
current_formal = None

def on_debounce_fire():
    """Called when the user pauses typing for DEBOUNCE_SECONDS."""
    global buffer
    global current_slang, current_formal
    # Pull the last few words from the buffer to check
    words = buffer.split()

    for n in range(1, 6):
        text_to_check = " ".join(words[-n:])
        result = match(text_to_check)
        if result:
            slang, definition = result
            current_slang = slang
            current_formal = text_to_check
            bridge.suggestion_ready.emit(slang, definition)
            return
    

def on_press(key):
    """Called on every keypress by pynput."""
    global buffer, debounce_timer, is_replacing
    if is_replacing:
        return

    if key==keyboard.Key.tab:
        if current_slang and current_formal and overlay.isVisible():
            is_replacing = True
            import time
            time.sleep(0.05)

            for _ in range(len(current_formal) + 1):
                kb_controller.press(Key.backspace)
                kb_controller.release(Key.backspace)
                time.sleep(0.01)  # small delay prevents dropped keystrokes
            
            kb_controller.type(current_slang)
            buffer = ""
            is_replacing = False
        bridge.hide_overlay.emit()  # Hide the overlay immediately
        return
    
    # Cancel the existing timer so it resets
    if debounce_timer:
        debounce_timer.cancel()
    
    # Append the character to the buffer
    try:
        buffer+=key.char
    except AttributeError:
        if (key == keyboard.Key.space):
            buffer += " "
        elif (key == keyboard.Key.backspace):
            buffer = buffer[:-1]
        else:
            pass
    
    # Trim the buffer so it never exceeds MAX_BUFFER
    buffer = buffer[-MAX_BUFFER:]
    
    # Start a new debounce timer
    debounce_timer = threading.Timer(DEBOUNCE_SECONDS, on_debounce_fire)
    debounce_timer.start()

if __name__ == "__main__":
    print("TWK is running. Start typing...")
    app = QApplication(sys.argv)
    bridge = Bridge()
    overlay = SuggestionOverlay()
    tray = SystemTray(app)
    bridge.suggestion_ready.connect(overlay.show_suggestion)
    bridge.hide_overlay.connect(overlay.hide_suggestion)

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    app.exec()