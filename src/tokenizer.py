"""
Tamil Linguistic Tokenizer and Position Streamer.
Normalizes Tamil script using NFC, extracts words via regex, and tracks 1-based positions.
"""
import re
import unicodedata
from typing import List, Tuple

# Regex pattern matching Tamil unicode characters and alphanumeric terms
TAMIL_WORD_PATTERN = re.compile(r"[\u0B80-\u0BFFa-zA-Z0-9]+", re.UNICODE)


def normalize_tamil_text(text: str) -> str:
    """Normalizes text with Unicode NFC and strips hidden zero-width characters."""
    # Dry-run: "தமிழ்\u200bநாடு" -> NFC composes graphemes, replaces \u200b
    # Result:  "தமிழ்நாடு" (clean standardized string)
    if not text:
        return ""
    normalized = unicodedata.normalize("NFC", text)
    return normalized.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "")


def tokenize(text: str) -> List[str]:
    """Tokenizes normalized text into words, stripping punctuation."""
    # Dry-run: "வணக்கம்! 1947 தமிழ்நாடு." -> matches Tamil and alphanumeric words
    # Result:  ["வணக்கம்", "1947", "தமிழ்நாடு"] (all punctuation like ! and . dropped)
    normalized = normalize_tamil_text(text)
    tokens = TAMIL_WORD_PATTERN.findall(normalized)
    return [t.lower() for t in tokens if t.strip()]


def tokenize_with_positions(text: str) -> List[Tuple[str, int]]:
    """Tokenizes text and returns (term, 1-based_position) pairs."""
    # Dry-run: "தமிழ் வாழ்க" -> tokens=["தமிழ்", "வாழ்க"]
    # Result:  [("தமிழ்", 1), ("வாழ்க", 2)] (1-based positions for IR positional indexing)
    tokens = tokenize(text)
    return [(term, pos) for pos, term in enumerate(tokens, start=1)]
