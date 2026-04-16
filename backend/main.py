from pynput import keyboard
import threading
from backend.matcher import match

# The buffer stores the last N characters the user typed
buffer = ""
MAX_BUFFER = 50

# This will hold the debounce timer so we can reset it on each keypress
debounce_timer = None
DEBOUNCE_SECONDS = 0.4

def on_debounce_fire():
    """Called when the user pauses typing for DEBOUNCE_SECONDS."""
    global buffer
    # Pull the last few words from the buffer to check
    words = buffer.split()

    for n in range (5, 0, -1):
        text_to_check = " ".join(words[-n:])
        result = match(text_to_check)
        if result:
            slang, definition = result
            print(f"Suggestion: {slang} ({definition[:30]}...)")
            return
    
    # text_to_check = " ".join(buffer.split()[-5:])
    
    # result = match(text_to_check)
    # if result:
    #     slang, definition = result
    #     # For now, just print — the overlay comes in Phase 4
    #     print(f"Suggestion: {slang} ({definition[:30]}...)")

def on_press(key):
    """Called on every keypress by pynput."""
    print(f"Key pressed: {key}")  # Debug: see every keypress in the console
    global buffer, debounce_timer
    
    # Cancel the existing timer so it resets
    if debounce_timer:
        debounce_timer.cancel()
    
    # Append the character to the buffer
    try:
        buffer+=key.char
        print(f"Buffer updated: '{buffer}'")  # Debug: see the buffer grow
    except AttributeError:
        if (key == keyboard.Key.space):
            buffer += " "
        elif (key == keyboard.Key.backspace):
            buffer = buffer[:-1]
            print(f"Buffer updated (backspace): '{buffer}'")  # Debug: see the buffer update on backspace 
        else:
            pass
    
    # Trim the buffer so it never exceeds MAX_BUFFER
    buffer = buffer[-MAX_BUFFER:]
    
    # Start a new debounce timer
    debounce_timer = threading.Timer(DEBOUNCE_SECONDS, on_debounce_fire)
    debounce_timer.start()

if __name__ == "__main__":
    print("TWK is running. Start typing...")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()