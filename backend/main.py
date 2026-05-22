import pyperclip
from pynput import keyboard
import threading
from backend.matcher import CACHE, match
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication
from frontend.overlay import SuggestionOverlay, SystemTray
import sys
import win32gui, win32process, psutil
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

browsers = ["chrome", "firefox", "msedge", "opera", "brave"]

def get_active_app():
    hwnd = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        return psutil.Process(pid).name().lower()
    except:
        return ""

def type_via_clipboard(text):
    import time
    old_clip = pyperclip.paste()
    pyperclip.copy(text)
    time.sleep(0.1)
    
    kb_controller.press(Key.ctrl)
    kb_controller.press('v')
    kb_controller.release('v')
    kb_controller.release(Key.ctrl)
    
    time.sleep(0.1)
    pyperclip.copy(old_clip)

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
    app = get_active_app()
    extra = 1 if any(b in app for b in browsers) else 0
    if is_replacing:
        return

    if hasattr(key, 'char') and key.char == '\\':
        if current_slang and current_formal and overlay.isVisible():
            is_replacing = True
            import time
            time.sleep(0.2)

            for _ in range(len(current_formal) + 1):
                kb_controller.press(Key.backspace)
                kb_controller.release(Key.backspace)
                time.sleep(0.03)  # small delay prevents dropped keystrokes
            
            type_via_clipboard(current_slang)
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