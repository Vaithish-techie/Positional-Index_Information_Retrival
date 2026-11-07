"""
LEVEL 2 TEST HARNESS: Tamil Tokenizer & Position Streamer
Run: python3 tests/test_level2.py
"""
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.tokenizer import normalize_tamil_text, tokenize, tokenize_with_positions


def test_normalization():
    print("Testing normalize_tamil_text()...", end=" ")
    raw = "தமிழ்\u200bநாடு\u200c"
    normalized = normalize_tamil_text(raw)
    assert "\u200b" not in normalized, "Failed: Zero-width space (\\u200b) not removed"
    assert "\u200c" not in normalized, "Failed: Zero-width non-joiner (\\u200c) not removed"
    assert normalized == "தமிழ்நாடு", f"Expected 'தமிழ்நாடு', got '{normalized}'"
    print("✅ PASSED")


def test_tokenization():
    print("Testing tokenize()...", end=" ")
    text = "வணக்கம்! தமிழ் ஒரு செம்மொழி (Classical Language) ஆகும்."
    tokens = tokenize(text)
    expected = ["வணக்கம்", "தமிழ்", "ஒரு", "செம்மொழி", "classical", "language", "ஆகும்"]
    assert tokens == expected, f"Failed: Expected {expected}, got {tokens}"
    print("✅ PASSED")


def test_positions():
    print("Testing tokenize_with_positions()...", end=" ")
    text = "கற்க கசடறக் கற்பவை"
    token_pos = list(tokenize_with_positions(text))
    expected = [
        ("கற்க", 1),
        ("கசடறக்", 2),
        ("கற்பவை", 3),
    ]
    assert token_pos == expected, f"Failed: Expected {expected}, got {token_pos}"
    
    # Check 1-based indexing explicitly
    assert token_pos[0][1] == 1, "Failed: Position must be 1-based (start at 1, not 0)"
    assert token_pos[1][1] == 2, "Failed: Position index sequence error"
    assert token_pos[2][1] == 3, "Failed: Position index sequence error"
    print("✅ PASSED")


def test_empty_string():
    print("Testing edge case: empty input...", end=" ")
    assert tokenize("") == [], "Failed on empty string tokenize"
    assert list(tokenize_with_positions("")) == [], "Failed on empty string positions"
    print("✅ PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("⚔️  LEVEL 2 BOSS FIGHT: Tamil Tokenizer & Position Streamer")
    print("=" * 60)
    try:
        test_normalization()
        test_tokenization()
        test_positions()
        test_empty_string()
        print("\n🎉 LEVEL 2 COMPLETE! You have mastered Tamil Unicode Tokenization!")
        print("Run me when you're ready to proceed to Level 3.")
    except AssertionError as e:
        print(f"\n❌ BOSS FIGHT FAILED:\n   {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR ENCOUNTERED:\n   {type(e).__name__}: {e}")
        sys.exit(1)
