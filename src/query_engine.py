"""
LEVEL 8 & 9 CHALLENGE: Positional Intersect & Query Engine
==========================================================
Your goal:
1. Level 8: Implement the Positional Intersect algorithm for exact phrase queries
   (e.g., "தமிழ் நாடு" where pos2 - pos1 == 1).
2. Level 9: Implement Proximity queries (e.g., term1 /k term2 where 1 <= |pos2 - pos1| <= k).
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
    # TODO 8: Implement two-pointer doc_id merge and nested position verification
    pass


def phrase_query(
    phrase: str,
    vocab: Dict[str, Dict[str, int]],
    postings_file_path: Path,
) -> List[int]:
    """
    Evaluates an exact multi-word phrase query (e.g. "தமிழ் நாடு").
    Returns list of matching document IDs.
    
    Steps:
    1. Tokenize query using tokenize(phrase).
    2. If any token is missing in vocab -> phrase cannot exist, return [].
    3. Read postings for first term from disk via read_postings_from_disk().
    4. For subsequent terms:
       - Read their postings from disk.
       - Intersect with running result using positional_intersect(..., k=1).
    5. Return list of matching doc_ids: [doc_id for doc_id, _ in result].
    """
    # TODO 8: Implement phrase query evaluation
    pass


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
    
    Steps:
    1. Clean / tokenize term1 and term2.
    2. Check if both exist in vocab (if not, return []).
    3. Read postings for term1 and term2 from disk.
    4. For docs matching both terms:
       Check if any pos1 in positions1 and pos2 in positions2 satisfy:
       1 <= abs(pos1 - pos2) <= k
    5. Return list of matching doc_ids.
    """
    # TODO 9: Implement proximity search
    pass
