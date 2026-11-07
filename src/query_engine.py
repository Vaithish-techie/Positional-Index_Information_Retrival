"""
LEVEL 8 & 9 CHALLENGE: Positional Intersect & Query Engine
==========================================================
Your goal:
1. Level 8: Implement the Positional Intersect algorithm for exact phrase queries
   (e.g., "தமிழ் நாடு" where pos2 - pos1 == 1).
2. Level 8: Implement phrase_query() to chain multi-word phrases from disk postings.
3. Level 9: Implement proximity_query() (e.g., term1 /k term2 where 1 <= |pos2 - pos1| <= k).
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
    LEVEL 8: Two-pointer positional intersection algorithm.
    Finds documents where term2 appears between 1 and k positions after term1.

    Arguments:
        p1: Postings list for term 1: [(doc_id, [pos1, pos2, ...]), ...]
        p2: Postings list for term 2: [(doc_id, [pos1, pos2, ...]), ...]
        k: Maximum forward distance allowed (k=1 for consecutive exact phrase search).

    Returns:
        Matched postings: [(doc_id, [matched_positions_of_term2]), ...]
    """
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
                diff = pos1 - pos2

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
    # TODO: Your code here for phrase_query!


def proximity_query(
    term1: str,
    term2: str,
    k: int,
    vocab: Dict[str, Dict[str, int]],
    postings_file_path: Path,
) -> List[int]:
    """
    LEVEL 9: Evaluates a proximity query: term1 /k term2
    Finds documents where term1 and term2 appear within k words of each other
    (1 <= |pos1 - pos2| <= k).
    """
    # TODO: Your code here for proximity_query!
    pass
