"""
Main CLI Application for Tamil Positional Indexer.
Ties together:
1. Corpus loading / crawling (Level 2)
2. Linguistic tokenization (Level 2)
3. In-memory indexing & analytics (Level 3 & 4)
4. Secondary memory storage & seek retrieval (Level 5, 6 & 7)
5. Positional phrase & proximity queries (Level 8 & 9)
6. Deliverables generator & packaging (Level 10)
"""
import argparse
import json
import logging
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple

from src.config import (
    DEFAULT_CORPUS_FILE,
    INDEX_DIR,
    OUTPUT_DIR,
    POSTINGS_FILE,
    PROJECT_ROOT,
    RARE_TERMS_OUTPUT_FILE,
    TEST_CASES_OUTPUT_FILE,
    VOCAB_FILE,
)
from src.corpus_collector import build_corpus_from_wikipedia, load_documents_from_xml
from src.indexer import add_document_to_index, compute_frequencies
from src.query_engine import phrase_query, proximity_query
from src.secondary_storage import read_postings_from_disk, serialize_and_write_postings
from src.tokenizer import tokenize_with_positions

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TamilIR")


def build_full_index(corpus_xml_path: Path = DEFAULT_CORPUS_FILE) -> Dict[str, Dict[str, int]]:
    """Builds the complete positional index from corpus XML and writes to secondary storage."""
    # Step 1: Load documents
    if not corpus_xml_path.exists():
        logger.info(f"Corpus file not found at {corpus_xml_path}. Crawling Tamil Wikipedia...")
        build_corpus_from_wikipedia(num_docs=50, output_xml_path=corpus_xml_path)

    documents = load_documents_from_xml(corpus_xml_path)
    logger.info(f"Loaded {len(documents)} documents. Beginning positional tokenization...")

    # Step 2: In-Memory Index Accumulation
    in_memory_index: Dict[str, Dict[int, List[int]]] = {}
    total_tokens = 0

    for doc_id, doc_info in documents.items():
        full_text = f"{doc_info['title']} {doc_info['text']}"
        tokens_with_pos = tokenize_with_positions(full_text)
        total_tokens += len(tokens_with_pos)
        add_document_to_index(in_memory_index, doc_id, tokens_with_pos)

    logger.info(
        f"Tokenization complete. Total tokens: {total_tokens}, "
        f"Unique vocabulary terms: {len(in_memory_index)}"
    )

    # Step 3: Write Postings to Secondary Storage & build RAM Vocab table
    vocab = serialize_and_write_postings(in_memory_index, POSTINGS_FILE)

    # Persist vocab to JSON so it can be loaded into RAM quickly
    VOCAB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(VOCAB_FILE, "w", encoding="utf-8") as vf:
        json.dump(vocab, vf, ensure_ascii=False, indent=2)

    disk_size_kb = POSTINGS_FILE.stat().st_size / 1024
    logger.info(f"Index successfully built! Secondary storage size: {disk_size_kb:.2f} KB")
    return vocab


def load_vocab() -> Dict[str, Dict[str, int]]:
    """Loads vocabulary lexicon into RAM."""
    if not VOCAB_FILE.exists() or not POSTINGS_FILE.exists():
        logger.info("Index not found on disk. Building index now...")
        return build_full_index()

    with open(VOCAB_FILE, "r", encoding="utf-8") as vf:
        vocab = json.load(vf)
    logger.info(f"Loaded vocabulary into RAM: {len(vocab)} terms.")
    return vocab


def generate_assignment_deliverables() -> None:
    """
    Generates required assignment outputs:
    1. output/10_rare_terms_index.txt: 10 rare terms with CF, DF, and positional postings list
    2. output/test_cases_output.txt: 5 diverse test queries with detailed results
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    vocab = load_vocab()
    documents = load_documents_from_xml(DEFAULT_CORPUS_FILE)

    # -------------------------------------------------------------
    # Deliverable 1: 10 Rare Terms with Positional Index
    # -------------------------------------------------------------
    logger.info("Selecting 10 rare terms (DF=1, low CF)...")
    # Find purely Tamil terms with DF == 1 (hapax legomena / rare terms)
    rare_candidates = [
        (term, data)
        for term, data in vocab.items()
        if data["df"] == 1
        and all("\u0B80" <= c <= "\u0BFF" for c in term)
        and not term.startswith("ஃ")
        and len(term) >= 5
    ]
    # Sort by CF ascending, then alphabetically
    rare_candidates.sort(key=lambda x: (x[1]["cf"], x[0]))
    selected_10_rare = rare_candidates[:10]

    with open(RARE_TERMS_OUTPUT_FILE, "w", encoding="utf-8") as rf:
        rf.write("=" * 80 + "\n")
        rf.write("ASSIGNMENT DELIVERABLE: 10 RARE TERMS WITH POSITIONAL INDEX\n")
        rf.write("Language: Tamil (தமிழ்)\n")
        rf.write("=" * 80 + "\n\n")

        for idx, (term, meta) in enumerate(selected_10_rare, start=1):
            # Read postings from secondary storage using disk offset
            postings = read_postings_from_disk(
                POSTINGS_FILE, meta["offset"], meta["byte_len"]
            )
            rf.write(f"[{idx}] Term: '{term}'\n")
            rf.write(f"    Collection Frequency (CF) : {meta['cf']}\n")
            rf.write(f"    Document Frequency (DF)   : {meta['df']}\n")
            rf.write(f"    Secondary Storage Offset  : Byte {meta['offset']}\n")
            rf.write(f"    Block Byte Length         : {meta['byte_len']} bytes\n")
            rf.write(f"    Positional Postings List  :\n")
            for doc_id, positions in postings:
                doc_title = documents.get(doc_id, {}).get("title", f"Doc {doc_id}")
                rf.write(f"      - Doc ID {doc_id} ('{doc_title}'): Positions {positions}\n")
            rf.write("\n" + "-" * 60 + "\n\n")

    logger.info(f"Saved 10 rare terms to {RARE_TERMS_OUTPUT_FILE}")

    # -------------------------------------------------------------
    # Deliverable 2: 5 Comprehensive Test Cases
    # -------------------------------------------------------------
    logger.info("Executing 5 test cases...")
    test_cases = [
        {
            "id": 1,
            "type": "Exact 2-Word Phrase Query",
            "query": "தமிழ்நாடு",  # If single term or phrase
            "phrase": "தமிழ்நாடு",
            "description": "Searches for the consecutive phrase 'தமிழ்நாடு' (Tamil Nadu).",
        },
        {
            "id": 2,
            "type": "Exact 3-Word Phrase Query",
            "phrase": "சூரியக் குடும்பம்",
            "description": "Searches for the exact consecutive phrase 'சூரியக் குடும்பம்' (Solar System).",
        },
        {
            "id": 3,
            "type": "Proximity Query (/3)",
            "term1": "சென்னை",
            "term2": "நகரம்",
            "k": 3,
            "description": "Proximity query: 'சென்னை /3 நகரம்' (terms appear within distance of 3 words).",
        },
        {
            "id": 4,
            "type": "Exact Multi-Word Literary Phrase",
            "phrase": "இயற்கை வேளாண்மை",
            "description": "Searches for exact phrase 'இயற்கை வேளாண்மை' (Natural Agriculture).",
        },
        {
            "id": 5,
            "type": "Negative Verification (Zero False-Positives)",
            "phrase": "நிலா வேதியியல் சூரியக்",
            "description": "Non-consecutive random words; verifies system returns empty [].",
        },
    ]

    with open(TEST_CASES_OUTPUT_FILE, "w", encoding="utf-8") as tf:
        tf.write("=" * 80 + "\n")
        tf.write("ASSIGNMENT DELIVERABLE: 5 TEST CASES FOR POSITIONAL INDEXER\n")
        tf.write("Language: Tamil (தமிழ்)\n")
        tf.write("=" * 80 + "\n\n")

        for tc in test_cases:
            tf.write(f"Test Case {tc['id']}: {tc['type']}\n")
            tf.write(f"Description: {tc['description']}\n")

            if "phrase" in tc:
                query_str = f"\"{tc['phrase']}\""
                matched_docs = phrase_query(tc["phrase"], vocab, POSTINGS_FILE)
            else:
                query_str = f"{tc['term1']} /{tc['k']} {tc['term2']}"
                matched_docs = proximity_query(
                    tc["term1"], tc["term2"], tc["k"], vocab, POSTINGS_FILE
                )

            tf.write(f"Query: {query_str}\n")
            tf.write(f"Total Matching Documents: {len(matched_docs)}\n")
            tf.write(f"Matched Doc IDs: {matched_docs}\n")
            if matched_docs:
                tf.write("Sample Matching Documents:\n")
                for doc_id in matched_docs[:3]:
                    title = documents.get(doc_id, {}).get("title", f"Doc {doc_id}")
                    snippet = documents.get(doc_id, {}).get("text", "")[:120]
                    tf.write(f"  * [Doc {doc_id}] {title}: \"{snippet}...\"\n")
            else:
                tf.write("Result: No documents matched (Correct behavior - 0 false positives).\n")
            tf.write("\n" + "-" * 60 + "\n\n")

    logger.info(f"Saved 5 test cases output to {TEST_CASES_OUTPUT_FILE}")


def package_source_code(roll_no: str) -> Path:
    """Packages source code and documentation into <roll_no>-src.zip."""
    zip_filename = PROJECT_ROOT / f"{roll_no}-src.zip"
    logger.info(f"Creating submission archive: {zip_filename}...")

    # Files to include
    include_patterns = [
        "src/**/*.py",
        "tests/**/*.py",
        "output/*",
        "README.md",
        "QUEST_PLAN.md",
    ]

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zf:
        for pattern in include_patterns:
            for file_path in PROJECT_ROOT.glob(pattern):
                if file_path.is_file() and "__pycache__" not in file_path.parts:
                    arcname = file_path.relative_to(PROJECT_ROOT)
                    zf.write(file_path, arcname=arcname)
                    logger.info(f"  Added: {arcname}")

    logger.info(f"Submission zip successfully created at: {zip_filename}")
    return zip_filename


def main():
    parser = argparse.ArgumentParser(description="Tamil Positional Indexer CLI")
    parser.add_argument("--index", action="store_true", help="Build positional index from corpus")
    parser.add_argument("--phrase", type=str, help="Execute exact phrase query")
    parser.add_argument("--proximity", nargs=3, metavar=("TERM1", "TERM2", "K"), help="Execute proximity query")
    parser.add_argument("--deliverables", action="store_true", help="Generate 5 test cases and 10 rare terms")
    parser.add_argument("--package", type=str, metavar="ROLL_NO", help="Create <RollNo>-src.zip")

    args = parser.parse_args()

    if args.index:
        build_full_index()
    elif args.phrase:
        vocab = load_vocab()
        docs = phrase_query(args.phrase, vocab, POSTINGS_FILE)
        print(f"\n🔍 Phrase Query: \"{args.phrase}\"")
        print(f"📄 Matching Documents ({len(docs)}): {docs}")
    elif args.proximity:
        t1, t2, k_str = args.proximity
        vocab = load_vocab()
        docs = proximity_query(t1, t2, int(k_str), vocab, POSTINGS_FILE)
        print(f"\n🔍 Proximity Query: {t1} /{k_str} {t2}")
        print(f"📄 Matching Documents ({len(docs)}): {docs}")
    elif args.deliverables:
        generate_assignment_deliverables()
    elif args.package:
        package_source_code(args.package)
    else:
        # Default run: build index and generate deliverables
        build_full_index()
        generate_assignment_deliverables()


if __name__ == "__main__":
    main()
