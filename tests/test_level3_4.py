"""
LEVEL 3 & 4 TEST HARNESS: Positional Index & Frequencies
Run: python3 tests/test_level3_4.py
"""
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.indexer import add_document_to_index, compute_frequencies


def test_level3_index_builder():
    print("Testing Level 3: add_document_to_index()...", end=" ")
    index = {}

    # Doc 1: "தமிழ் வாழ்க தமிழ் வெல்க"
    doc1_tokens = [("தமிழ்", 1), ("வாழ்க", 2), ("தமிழ்", 3), ("வெல்க", 4)]
    add_document_to_index(index, doc_id=1, tokens_with_positions=doc1_tokens)

    # Doc 2: "தமிழ் செம்மொழி"
    doc2_tokens = [("தமிழ்", 1), ("செம்மொழி", 2)]
    add_document_to_index(index, doc_id=2, tokens_with_positions=doc2_tokens)

    # Check terms existence
    assert "தமிழ்" in index, "Failed: 'தமிழ்' missing from index"
    assert "வாழ்க" in index, "Failed: 'வாழ்க' missing from index"
    assert "செம்மொழி" in index, "Failed: 'செம்மொழி' missing from index"

    # Check positional lists for Doc 1 and Doc 2
    assert index["தமிழ்"][1] == [1, 3], f"Expected [1, 3] for தமிழ் in doc 1, got {index['தமிழ்'].get(1)}"
    assert index["தமிழ்"][2] == [1], f"Expected [1] for தமிழ் in doc 2, got {index['தமிழ்'].get(2)}"
    assert index["வாழ்க"][1] == [2], f"Expected [2] for வாழ்க in doc 1, got {index['வாழ்க'].get(1)}"
    assert 2 not in index["வாழ்க"], "Failed: 'வாழ்க' should not be in doc 2"
    print("✅ PASSED")


def test_level4_frequencies():
    print("Testing Level 4: compute_frequencies()...", end=" ")
    # For 'தமிழ்': in Doc 1 at [1, 3], in Doc 2 at [1], in Doc 3 at [5, 12, 19]
    tamil_postings = {
        1: [1, 3],
        2: [1],
        3: [5, 12, 19]
    }
    df, cf = compute_frequencies(tamil_postings)

    # DF = 3 (Docs 1, 2, 3)
    # CF = 2 + 1 + 3 = 6
    assert df == 3, f"Expected DF=3, got {df}"
    assert cf == 6, f"Expected CF=6, got {cf}"
    assert cf >= df, "CRITICAL IR INVARIANT: CF must be >= DF"

    # Single doc rare term
    rare_postings = {10: [42]}
    df_rare, cf_rare = compute_frequencies(rare_postings)
    assert df_rare == 1, f"Expected DF=1, got {df_rare}"
    assert cf_rare == 1, f"Expected CF=1, got {cf_rare}"

    print("✅ PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("⚔️  LEVEL 3 & 4 BOSS FIGHT: Positional Index & Frequencies")
    print("=" * 60)
    try:
        test_level3_index_builder()
        test_level4_frequencies()
        print("\n🎉 LEVEL 3 & 4 COMPLETE! You now master IR Positional Indexing & Analytics!")
        print("Run me when you're ready to proceed to Level 5 (Secondary Storage Serializer).")
    except AssertionError as e:
        print(f"\n❌ BOSS FIGHT FAILED:\n   {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR ENCOUNTERED:\n   {type(e).__name__}: {e}")
        sys.exit(1)
