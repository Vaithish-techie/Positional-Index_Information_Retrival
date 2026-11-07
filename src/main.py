"""
Main CLI Application for Tamil Positional Indexer.
Provides commands to:
1. Index the Tamil text corpus (--index)
2. Execute exact phrase queries (--phrase "தமிழ்நாடு")
3. Execute proximity queries (--proximity "சென்னை" "நகரம்" 3)
"""
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List

from src.config import DEFAULT_CORPUS_FILE, POSTINGS_FILE, VOCAB_FILE
from src.corpus_collector import build_corpus_from_wikipedia, load_documents_from_xml
from src.indexer import add_document_to_index
from src.query_engine import phrase_query, proximity_query
from src.secondary_storage import serialize_and_write_postings
from src.tokenizer import tokenize_with_positions

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TamilIR")


def build_full_index(corpus_xml_path: Path = DEFAULT_CORPUS_FILE) -> Dict[str, Dict[str, int]]:
    """Builds positional index from corpus XML and writes postings to secondary storage."""
    if not corpus_xml_path.exists():
        logger.info(f"Corpus file not found. Crawling Tamil Wikipedia articles...")
        build_corpus_from_wikipedia(num_docs=50, output_xml_path=corpus_xml_path)

    documents = load_documents_from_xml(corpus_xml_path)
    logger.info(f"Loaded {len(documents)} documents. Starting positional tokenization...")

    in_memory_index: Dict[str, Dict[int, List[int]]] = {}
    total_tokens = 0

    for doc_id, doc_info in documents.items():
        full_text = f"{doc_info['title']} {doc_info['text']}"
        tokens_with_pos = tokenize_with_positions(full_text)
        total_tokens += len(tokens_with_pos)
        add_document_to_index(in_memory_index, doc_id, tokens_with_pos)

    logger.info(
        f"Tokenization complete. Total tokens: {total_tokens}, "
        f"Unique vocabulary: {len(in_memory_index)} terms"
    )

    # Write postings to disk (secondary storage) and get in-memory lexicon
    vocab = serialize_and_write_postings(in_memory_index, POSTINGS_FILE)

    # Save vocabulary table to JSON for fast in-memory loading
    VOCAB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(VOCAB_FILE, "w", encoding="utf-8") as vf:
        json.dump(vocab, vf, ensure_ascii=False, indent=2)

    disk_size_kb = POSTINGS_FILE.stat().st_size / 1024
    logger.info(f"Index built! Disk postings size: {disk_size_kb:.2f} KB")
    return vocab


def load_vocab() -> Dict[str, Dict[str, int]]:
    """Loads vocabulary lexicon into RAM, building the index if missing."""
    if not VOCAB_FILE.exists() or not POSTINGS_FILE.exists():
        logger.info("Index not found. Building index first...")
        return build_full_index()

    with open(VOCAB_FILE, "r", encoding="utf-8") as vf:
        return json.load(vf)


def main():
    parser = argparse.ArgumentParser(description="Tamil Positional Text Indexer")
    parser.add_argument("--index", action="store_true", help="Build positional index from corpus XML")
    parser.add_argument("--phrase", type=str, help="Search exact consecutive phrase")
    parser.add_argument("--proximity", nargs=3, metavar=("TERM1", "TERM2", "K"), help="Search proximity query (TERM1 /K TERM2)")

    args = parser.parse_args()

    if args.index:
        build_full_index()

    elif args.phrase:
        vocab = load_vocab()
        documents = load_documents_from_xml(DEFAULT_CORPUS_FILE)
        matched_docs = phrase_query(args.phrase, vocab, POSTINGS_FILE)

        print(f"\nQuery Phrase: \"{args.phrase}\"")
        print(f"Total Matches: {len(matched_docs)} documents")
        print(f"Matched Doc IDs: {matched_docs}")
        for doc_id in matched_docs[:3]:
            title = documents.get(doc_id, {}).get("title", f"Doc {doc_id}")
            snippet = documents.get(doc_id, {}).get("text", "")[:120].strip()
            print(f"  * [Doc {doc_id}] {title}: \"{snippet}...\"")
        print()

    elif args.proximity:
        t1, t2, k_str = args.proximity
        k = int(k_str)
        vocab = load_vocab()
        documents = load_documents_from_xml(DEFAULT_CORPUS_FILE)
        matched_docs = proximity_query(t1, t2, k, vocab, POSTINGS_FILE)

        print(f"\nProximity Query: {t1} /{k} {t2}")
        print(f"Total Matches: {len(matched_docs)} documents")
        print(f"Matched Doc IDs: {matched_docs}")
        for doc_id in matched_docs[:3]:
            title = documents.get(doc_id, {}).get("title", f"Doc {doc_id}")
            snippet = documents.get(doc_id, {}).get("text", "")[:120].strip()
            print(f"  * [Doc {doc_id}] {title}: \"{snippet}...\"")
        print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
