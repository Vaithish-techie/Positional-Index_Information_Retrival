"""
Configuration module for Tamil Positional Indexer.
Defines directory paths, constants, and default hyperparameters.
"""
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INDEX_DIR = DATA_DIR / "index"
OUTPUT_DIR = PROJECT_ROOT / "output"

# File Paths
DEFAULT_CORPUS_FILE = RAW_DATA_DIR / "tamil_wiki_corpus.xml"
VOCAB_FILE = INDEX_DIR / "vocab.json"
POSTINGS_FILE = INDEX_DIR / "postings.dat"
TEST_CASES_OUTPUT_FILE = OUTPUT_DIR / "test_cases_output.txt"
RARE_TERMS_OUTPUT_FILE = OUTPUT_DIR / "10_rare_terms_index.txt"

# Crawler Settings
WIKIPEDIA_API_URL = "https://ta.wikipedia.org/w/api.php"
USER_AGENT = "TamilIRIndexer/1.0 (academic assignment; student project; contact: student@university.edu)"
DEFAULT_NUM_DOCS = 60  # Good size for indexing test and rare terms

# Encoding
ENCODING = "utf-8"
