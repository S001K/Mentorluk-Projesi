import re

# This regex pattern matches any character that is NOT (^)
# in the allowed set:
# - a-z, A-Z (letters)
# - 0-9 (numbers)
# - \n, \r (newlines)
# - A space ' '
# - The punctuation marks .,?!';:"-()
# This guarantees that only safe, speakable characters are left.
ALLOWED_CHARS_PATTERN = re.compile(
    r"[^a-zA-Z0-9\n\r .,?!';:\"\-()]",
    flags=re.UNICODE
)

def filter_allowed_text(text: str) -> str:
    """
    Strips all characters from a string except for a whitelist of
    English alphabet, numbers, newlines, and common punctuation.
    """
    return ALLOWED_CHARS_PATTERN.sub(r'', text)