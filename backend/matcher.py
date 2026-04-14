from backend.database import get_connection

# Level 1: instant dictionary cache (RAM)
# These are your most common/obvious mappings - no DB hit needed
# Format: "formal phrase" -> ("slang term", "definition")
CACHE = {
    "charisma": ("rizz", "Slang term for charisma or charm, often used to describe someone who has a magnetic personality or is particularly attractive"),

}

def match_from_cache(text):
    """Check the RAM dictionary first. Returns a tuple or None."""
    cleaned_text = text.strip().lower()
    return CACHE.get(cleaned_text)

def match_from_db(text):
    """Query SQLite for a match. Returns a tuple or None."""
    conn = get_connection()
    cursor = conn.cursor()
    SELECT_QUERY = "SELECT slang_term, definition FROM mappings WHERE formal_phrase = ? COLLATE NOCASE"
    cursor.execute (SELECT_QUERY, (text.strip().lower(),))
    result  = cursor.fetchone()
    return result


def match(text):
    """
    Main entry point. Tries cache first, then DB, then returns None.
    (Ollama fallback comes later in Phase 5)
    """
    result = match_from_cache(text)
    if result:
        return result
    result = match_from_db(text)
    if result:
        return result
    return None

if __name__ == "__main__":
    # Quick self-test — try a few phrases and print results
    test_phrases = ["i'm tired", "charisma", "something with no match"]
    for phrase in test_phrases:
        result = match(phrase)
        print(f"'{phrase}' -> {result}")