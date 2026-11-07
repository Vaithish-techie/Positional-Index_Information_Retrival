"""
Positional Intersect and Query Engine.
Evaluates exact phrase queries and proximity (/k) queries using postings from secondary storage.
"""
from pathlib import Path
from typing import Dict, List, Tuple

from src.secondary_storage import read_postings_from_disk
from src.tokenizer import tokenize

PostingList = List[Tuple[int, List[int]]]


def positional_intersect(
    p1: PostingList,
    p2: PostingList,
    k: int = 1,
) -> PostingList:
    """
    Two-pointer positional intersection algorithm (Manning et al., Ch 2).
    Finds documents where term2 appears between 1 and k positions after term1.
    """
    # Dry-run: p1=[(1, [1, 5])], p2=[(1, [2, 9])], k=1 -> diff=2-1=1 <= k -> MATCH!
    # Result:  [(1, [2])] (Doc 1 matched at pos 2, enabling multi-word phrase chaining)
    answer: PostingList = []
    i, j = 0, 0

    while i < len(p1) and j < len(p2):
        doc1, pos_list1 = p1[i]
        doc2, pos_list2 = p2[j]

        if doc1 == doc2:
            matched_positions: List[int] = []
            m, n = 0, 0

            while m < len(pos_list1) and n < len(pos_list2):
                pos1 = pos_list1[m]
                pos2 = pos_list2[n]
                diff = pos2 - pos1  # Positive distance: term2 follows term1

                if 1 <= diff <= k:
                    matched_positions.append(pos2)
                    m += 1
                    n += 1
                elif pos2 <= pos1:
                    n += 1
                else:
                    m += 1

            if matched_positions:
                answer.append((doc1, matched_positions))
            i += 1
            j += 1
        elif doc1 < doc2:
            i += 1
        else:
            j += 1

    return answer


def phrase_query(
    phrase: str,
    vocab: Dict[str, Dict[str, int]],
    postings_file_path: Path,
) -> List[int]:
    """
    Evaluates an exact multi-word phrase query (e.g. "தமிழ் நாடு").
    Returns list of matching document IDs.
    """
    # Dry-run: phrase="தமிழ் நாடு" -> tokens=["தமிழ்", "நாடு"] -> fetches both from disk -> k=1 intersect
    # Result:  [1] (matching doc_ids where words appear consecutively in exact order)
    tokens = tokenize(phrase)
    if not tokens:
        return []

    for token in tokens:
        if token not in vocab:
            return []

    first_info = vocab[tokens[0]]
    current_postings = read_postings_from_disk(
        postings_file_path, first_info["offset"], first_info["byte_len"]
    )

    for next_token in tokens[1:]:
        next_info = vocab[next_token]
        next_postings = read_postings_from_disk(
            postings_file_path, next_info["offset"], next_info["byte_len"]
        )
        current_postings = positional_intersect(current_postings, next_postings, k=1)
        if not current_postings:
            return []

    return [doc_id for doc_id, _ in current_postings]


def proximity_query(
    term1: str,
    term2: str,
    k: int,
    vocab: Dict[str, Dict[str, int]],
    postings_file_path: Path,
) -> List[int]:
    """
    Evaluates a proximity query: term1 /k term2 (e.g. "சென்னை" /3 "நகரம்").
    Matches documents where distance between terms is <= k (1 <= |pos1 - pos2| <= k).
    """
    # Dry-run: term1="சென்னை", term2="நகரம்", k=3 -> checks 1 <= |pos1 - pos2| <= 3 in same doc
    # Result:  [3] (matching doc_ids where terms appear within window of k words)
    t1_tokens = tokenize(term1)
    t2_tokens = tokenize(term2)
    if not t1_tokens or not t2_tokens:
        return []

    w1, w2 = t1_tokens[0], t2_tokens[0]
    if w1 not in vocab or w2 not in vocab:
        return []

    p1 = read_postings_from_disk(postings_file_path, vocab[w1]["offset"], vocab[w1]["byte_len"])
    p2 = read_postings_from_disk(postings_file_path, vocab[w2]["offset"], vocab[w2]["byte_len"])

    p1_dict = {doc_id: pos_list for doc_id, pos_list in p1}
    p2_dict = {doc_id: pos_list for doc_id, pos_list in p2}

    common_docs = sorted(set(p1_dict.keys()) & set(p2_dict.keys()))
    matching_docs: List[int] = []

    for doc_id in common_docs:
        pos1 = p1_dict[doc_id]
        pos2 = p2_dict[doc_id]
        if any(1 <= abs(p_a - p_b) <= k for p_a in pos1 for p_b in pos2):
            matching_docs.append(doc_id)

    return matching_docs
