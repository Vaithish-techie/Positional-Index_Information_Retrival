"""
LEVEL 8 & 9 TEST HARNESS: Positional Intersect & Query Engine
Run: python3 tests/test_level8_9.py
"""
import sys
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.secondary_storage import serialize_and_write_postings
from src.query_engine import positional_intersect, phrase_query, proximity_query


def test_positional_intersect_basic():
    print("Testing Level 8: positional_intersect() algorithm...", end=" ")
    # Term 1 ("தமிழ்"): in doc 1 at pos [1, 5], in doc 2 at pos [10]
    p1 = [(1, [1, 5]), (2, [10])]
    # Term 2 ("நாடு"): in doc 1 at pos [2, 9], in doc 2 at pos [20]
    p2 = [(1, [2, 9]), (2, [20])]

    # Exact consecutive phrase: k=1 -> requires pos2 - pos1 == 1
    # In Doc 1: pos1=1, pos2=2 -> match!
    # In Doc 2: pos1=10, pos2=20 -> diff is 10 > 1 -> no match!
    matched = positional_intersect(p1, p2, k=1)
    assert len(matched) == 1, f"Expected 1 matching document, got {len(matched)}"
    assert matched[0][0] == 1, f"Expected Doc 1, got {matched[0][0]}"
    assert 2 in matched[0][1], f"Expected matched pos 2, got {matched[0][1]}"
    print("✅ PASSED")


def test_phrase_query_e2e():
    print("Testing Level 8: End-to-End Phrase Query from Secondary Storage...", end=" ")
    with tempfile.TemporaryDirectory() as tmp_dir:
        postings_path = Path(tmp_dir) / "postings.dat"

        # Mock index:
        # Doc 1: "தமிழ் நாடு அரசு" (Exact phrase: 'தமிழ் நாடு' and 'தமிழ் நாடு அரசு')
        # Doc 2: "தமிழ் மொழியை நாடு முழுவதும் பேசுகின்றனர்" (Words present, but NOT a phrase)
        # Doc 3: "சென்னை தமிழ்நாடு தலைநகரம்"
        mock_index = {
            "தமிழ்": {1: [1], 2: [1], 3: [2]},
            "நாடு": {1: [2], 2: [4], 3: [10]},
            "அரசு": {1: [3]}
        }
        vocab = serialize_and_write_postings(mock_index, postings_path)

        # 2-word phrase query: "தமிழ் நாடு"
        # Should match Doc 1 (pos 1, 2)
        # Should NOT match Doc 2 (pos 1, 4 -> diff is 3 != 1)
        # Should NOT match Doc 3 (pos 2, 10 -> diff is 8 != 1)
        res1 = phrase_query("தமிழ் நாடு", vocab, postings_path)
        assert res1 == [1], f"Expected [1], got {res1}"

        # 3-word phrase query: "தமிழ் நாடு அரசு"
        res2 = phrase_query("தமிழ் நாடு அரசு", vocab, postings_path)
        assert res2 == [1], f"Expected [1], got {res2}"

        # Non-matching phrase
        res3 = phrase_query("நாடு அரசு தமிழ்", vocab, postings_path)
        assert res3 == [], f"Expected [], got {res3}"

    print("✅ PASSED")


def test_proximity_query():
    print("Testing Level 9: Proximity Query (/k)...", end=" ")
    with tempfile.TemporaryDirectory() as tmp_dir:
        postings_path = Path(tmp_dir) / "postings.dat"

        # Doc 1: pos diff = 2 - 1 = 1 (within /3)
        # Doc 2: pos diff = 4 - 1 = 3 (within /3)
        # Doc 3: pos diff = 10 - 2 = 8 (NOT within /3, but within /10)
        mock_index = {
            "தமிழ்": {1: [1], 2: [1], 3: [2]},
            "நாடு": {1: [2], 2: [4], 3: [10]}
        }
        vocab = serialize_and_write_postings(mock_index, postings_path)

        # Proximity with k=3
        res_k3 = proximity_query("தமிழ்", "நாடு", k=3, vocab=vocab, postings_file_path=postings_path)
        assert set(res_k3) == {1, 2}, f"Expected {1, 2}, got {res_k3}"

        # Proximity with k=1 (equivalent to adjacent words)
        res_k1 = proximity_query("தமிழ்", "நாடு", k=1, vocab=vocab, postings_file_path=postings_path)
        assert res_k1 == [1], f"Expected [1], got {res_k1}"

        # Proximity with k=10 (all 3 documents match)
        res_k10 = proximity_query("தமிழ்", "நாடு", k=10, vocab=vocab, postings_file_path=postings_path)
        assert set(res_k10) == {1, 2, 3}, f"Expected {1, 2, 3}, got {res_k10}"

    print("✅ PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("⚔️  LEVEL 8 & 9 BOSS FIGHT: Positional Intersect & Query Engine")
    print("=" * 60)
    try:
        test_positional_intersect_basic()
        test_phrase_query_e2e()
        test_proximity_query()
        print("\n🎉 LEVEL 8 & 9 COMPLETE! You have conquered Positional & Proximity Search!")
        print("Run me when you're ready for Boss Level 10 (Deliverables & Packaging).")
    except AssertionError as e:
        print(f"\n❌ BOSS FIGHT FAILED:\n   {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR ENCOUNTERED:\n   {type(e).__name__}: {e}")
        sys.exit(1)
