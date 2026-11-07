"""
LEVEL 5, 6 & 7 TEST HARNESS: Secondary Storage Architecture
Run: python3 tests/test_level5_6_7.py
"""
import sys
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.secondary_storage import serialize_and_write_postings, read_postings_from_disk


def test_secondary_storage_write_and_seek():
    print("Testing Levels 5, 6, 7: Secondary Storage Write, Lexicon & Seek Read...", end=" ")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        postings_path = Path(tmp_dir) / "postings.dat"

        # Mock accumulated in-memory index
        mock_index = {
            "தமிழ்": {1: [1, 5], 2: [3]},
            "நாடு": {1: [2, 6]},
            "செம்மொழி": {2: [4]}
        }

        # Level 5 & 6: Write postings to secondary storage (disk) and get RAM vocab
        vocab = serialize_and_write_postings(mock_index, postings_path)

        # Verification 1: Postings file must exist on disk and be non-empty
        assert postings_path.exists(), "Failed: postings.dat was not created on disk"
        disk_size = postings_path.stat().st_size
        assert disk_size > 0, "Failed: postings.dat on disk is empty"

        # Verification 2: Check RAM Lexicon entries (term -> cf, df, offset, byte_len)
        assert "தமிழ்" in vocab, "Failed: 'தமிழ்' missing in RAM vocabulary"
        assert vocab["தமிழ்"]["df"] == 2, f"Expected DF=2 for தமிழ், got {vocab['தமிழ்']['df']}"
        assert vocab["தமிழ்"]["cf"] == 3, f"Expected CF=3 for தமிழ், got {vocab['தமிழ்']['cf']}"
        assert "offset" in vocab["தமிழ்"], "Missing 'offset' in vocab entry"
        assert "byte_len" in vocab["தமிழ்"], "Missing 'byte_len' in vocab entry"

        # Verification 3: Level 7 - Read each term independently from disk using seek()
        for term, expected_docs in mock_index.items():
            entry = vocab[term]
            # Jump to disk offset and read only this term's bytes!
            retrieved_postings = read_postings_from_disk(
                postings_path,
                offset=entry["offset"],
                byte_len=entry["byte_len"]
            )
            # Reconstruct dict {doc_id: positions}
            retrieved_dict = {doc_id: positions for doc_id, positions in retrieved_postings}
            assert retrieved_dict == expected_docs, (
                f"Disk seek mismatch for term '{term}': "
                f"Expected {expected_docs}, got {retrieved_dict}"
            )

    print("✅ PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("⚔️  LEVEL 5, 6 & 7 BOSS FIGHT: Secondary Storage Architecture")
    print("=" * 60)
    try:
        test_secondary_storage_write_and_seek()
        print("\n🎉 LEVEL 5, 6 & 7 COMPLETE! You mastered Secondary Memory Seek Indexing!")
        print("Run me when you're ready to proceed to Level 8 (Positional Intersect / Phrase Search).")
    except AssertionError as e:
        print(f"\n❌ BOSS FIGHT FAILED:\n   {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR ENCOUNTERED:\n   {type(e).__name__}: {e}")
        sys.exit(1)
