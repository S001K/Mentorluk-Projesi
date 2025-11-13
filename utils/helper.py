# utils/helper.py
import re

# This regex pattern matches any character that is NOT (^)
# in the allowed set:
# - a-z, A-Z (letters)
# - 0-9 (numbers)
# - \n, \r (newlines)
# - a space ' '
# - the punctuation marks .,?!';:"-()
# This guarantees that only safe, speakable ASCII characters are left.
ALLOWED_CHARS_PATTERN = re.compile(
    r"[^a-zA-Z0-9\n\r .,?!';:\"\-()]",
    flags=re.UNICODE,
)


def filter_allowed_text(text: str) -> str:
    """
    Strips all characters from a string except for a whitelist of
    English alphabet, numbers, newlines, and common punctuation.
    Intended for Text-to-Speech friendly output.
    """
    return ALLOWED_CHARS_PATTERN.sub("", text)
