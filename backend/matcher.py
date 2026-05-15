from backend.database import get_connection
import ollama

# Level 1: instant dictionary cache (RAM)
# These are your most common/obvious mappings - no DB hit needed
# Format: "formal phrase" -> ("slang term", "definition")
CACHE = {
    "charisma": ("rizz", "Slang term for charisma or charm, often used to describe someone who has a magnetic personality or is particularly attractive"),
    "old" : ("unc" , "Slang term for something that is old or outdated, often used humorously to describe something that is no longer relevant or fashionable"),

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
    conn.close()
    return result

def match_from_ollama(text):
    """Ask local Ollama to suggest slang. Returns a tuple or None."""
    if len(text.split()) < 2:
        return None
    try:
        response = ollama.chat(
            model="llama3.2",
            options={"temperature": 0},
            messages=[
                {
                    "role": "system",
                    "content": """You are a US internet slang translator for non-native English speakers.
                    When given a formal or plain English phrase, respond with ONLY a JSON object like this:
                    {"slang": "the slang term", "definition": "brief definition"}

                    Rules:
                    - If the phrase can be shortened to an acronym using its exact letters, always use that. Example: "laughing my ass off" -> "lmao", "what the heck" -> "wth"
                    - If there is no acronym, suggest the most natural Gen-Z or internet slang equivalent. Example: "that is very good" -> "that's fire", "so yummy" -> "bussin", "no lie" -> "no cap", "i am very tired" -> "i'm dead"
                    - The slang must match the MEANING and SENTIMENT of the phrase exactly — do not suggest a random slang word
                    - Never suggest slang that means something different from the input
                    - If the phrase is already slang or you have no confident suggestion, respond with: {"slang": null, "definition": null}
                    - Never explain yourself. Only output the JSON."""
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )
        
        import json
        data = json.loads(response.message.content)
        if data["slang"]:
            slang_clean = data["slang"].lower().strip()
            input_clean = text.lower().strip()
            if slang_clean == input_clean or input_clean in slang_clean:
                return None
            if len(slang_clean) > len(input_clean) * 1.5:
                return None
            return (data["slang"], data["definition"])
    except Exception:
        # Ollama isn't running — fail silently
        return None

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
    result = match_from_ollama(text)
    if result:
        return result
    return None

if __name__ == "__main__":
    # Quick self-test — try a few phrases and print results
    test_phrases = ["i'm tired", "charisma", "something with no match", "i'm going to", "no lie"]
    for phrase in test_phrases:
        result = match(phrase)
        print(f"'{phrase}' -> {result}")