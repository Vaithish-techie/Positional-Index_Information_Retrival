"""
Secondary Storage Manager for Positional Postings.
Writes postings to disk (SSD/HDD) and provides O(1) seek-based retrieval.
Stores the term lexicon (CF, DF, offset, byte_len) in Main Memory (RAM).
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple

ENCODING = "utf-8"
PostingList = List[Tuple[int, List[int]]]


def serialize_and_write_postings(
    in_memory_index: Dict[str, Dict[int, List[int]]],
    postings_file_path: Path,
) -> Dict[str, Dict[str, int]]:
    """Writes postings lists to disk and returns the in-memory vocabulary lexicon."""
    # Dry-run: term="தமிழ்", docs={1:[1,5], 2:[3]} -> writes bytes to SSD at offset=0
    # Result:  RAM vocab stores {"தமிழ்": {"cf": 3, "df": 2, "offset": 0, "byte_len": 28}}
    vocab: Dict[str, Dict[str, int]] = {}
    postings_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(postings_file_path, "wb") as pf:
        for term in sorted(in_memory_index.keys()):
            doc_dict = in_memory_index[term]

            df = len(doc_dict)
            cf = sum(len(positions) for positions in doc_dict.values())
            sorted_postings = [
                (doc_id, sorted(positions))
                for doc_id, positions in sorted(doc_dict.items())
            ]

            offset = pf.tell()
            data_bytes = json.dumps(sorted_postings, separators=(",", ":")).encode(ENCODING)
            byte_len = len(data_bytes)

            pf.write(data_bytes)
            vocab[term] = {
                "cf": cf,
                "df": df,
                "offset": offset,
                "byte_len": byte_len,
            }

    return vocab


def read_postings_from_disk(
    postings_file_path: Path,
    offset: int,
    byte_len: int,
) -> PostingList:
    """Reads only the postings list for a term from disk using random-access seek."""
    # Dry-run: offset=0, byte_len=28 -> seek(0) jumps straight to byte 0 on SSD
    # Result:  reads only 28 bytes into RAM -> [(1, [1, 5]), (2, [3])], postings lists stay on disk!
    with open(postings_file_path, "rb") as pf:
        pf.seek(offset)
        raw_bytes = pf.read(byte_len)
        postings = json.loads(raw_bytes.decode(ENCODING))
        return [(doc_id, positions) for doc_id, positions in postings]
