"""
Positional Inverted Index Builder & Frequency Analytics.
Builds the term -> {doc_id: [positions]} structure and computes DF & CF.
"""

from typing import Dict, List, Tuple


def add_document_to_index(
    index: Dict[str, Dict[int, List[int]]],
    doc_id: int,
    tokens_with_positions: List[Tuple[str, int]],
) -> None:
    """Adds (term, position) tokens of a document into the positional index."""
    # Dry-run: ("தமிழ்", 1) then ("தமிழ்", 3) in doc 1 -> index["தமிழ்"][1] becomes [1, 3]
    # Memory:  index = {"தமிழ்": {1: [1, 3]}, "வாழ்க": {1: [2]}}
    for term, position in tokens_with_positions:
        if term not in index:
            index[term] = {}

        if doc_id not in index[term]:
            index[term][doc_id] = []

        index[term][doc_id].append(position)


def compute_frequencies(doc_dict: Dict[int, List[int]]) -> Tuple[int, int]:
    """Computes Document Frequency (DF) and Collection Frequency (CF) for a term."""
    # Dry-run: doc_dict = {1: [1, 3], 2: [5]} -> DF = len(keys) = 2 docs
    # CF = sum([len([1, 3]), len([5])]) = 2 + 1 = 3 total occurrences across corpus
    df = len(doc_dict)
    cf = sum(len(positions) for positions in doc_dict.values())
    return df, cf
