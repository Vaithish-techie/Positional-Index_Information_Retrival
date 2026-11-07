# Positional Inverted Indexer for Tamil Language

## System Specifications
- **Language**: Tamil (தமிழ்)
- **Dataset**: 50 Tamil Wikipedia articles in a single XML collection file (`data/raw/tamil_wiki_corpus.xml`)
- **Source Code**: Organized under `src/` directory
- **Storage Strategy**: Main Memory (RAM) for Vocabulary Lexicon + Secondary Storage (Disk/SSD) for Postings Lists

---

## 1. Project Overview

This project implements a complete Positional Inverted Index for the Tamil language, following standard Information Retrieval principles.

### Key Capabilities:
1. **Indian Language Focus**: Built specifically for Tamil (Unicode range `U+0B80` to `U+0BFF`).
2. **Dataset Collection**: Crawled 50 full articles from Tamil Wikipedia across science, history, literature, and geography, formatted into a single XML collection file (`tamil_wiki_corpus.xml`). The parser also supports FIRE dataset XML tags (`<DOC><DOCNO>...<TEXT>`).
3. **Positional Tracking**: Stores 1-based token positions for every word occurrence, enabling exact phrase queries and proximity searches.
4. **Frequency Metrics**: Calculates both Document Frequency (DF) and Collection Frequency (CF) for all terms in the vocabulary.
5. **Secondary Storage Separation**: The Vocabulary (lexicon) resides in Main Memory (RAM), while the entire Postings Lists reside on Secondary Storage (`postings.dat`). Individual postings are retrieved on-demand via $O(1)$ random seek (`file.seek`) using byte offsets, keeping RAM footprint minimal.

---

## 2. Architecture and Storage Design

To support large-scale text collections without exceeding RAM limits, the system separates the lexicon from postings:

```
[Main Memory (RAM)]                              [Secondary Storage (Disk/SSD)]
Vocabulary Lexicon                               data/index/postings.dat
---------------------------------------          -----------------------------------------
"தமிழ்"    -> {CF: 6, DF: 2, offset: 0,   len: 28}  ==seek==> Byte 0..27:   [[1,[1,5]], [2,[3]]]
"நாடு"     -> {CF: 3, DF: 1, offset: 28,  len: 19}  ==seek==> Byte 28..46:  [[1,[2,6]]]
"செம்மொழி" -> {CF: 1, DF: 1, offset: 47,  len: 15}  ==seek==> Byte 47..61:  [[2,[4]]]
```

### Components:
1. **Main Memory (RAM) - Vocabulary Lexicon**:
   A dictionary in memory mapping each term to:
   - `cf`: Collection Frequency (total occurrences across all documents).
   - `df`: Document Frequency (number of documents containing the term).
   - `offset`: Byte offset on disk where this term's postings begin.
   - `byte_len`: Byte length of this term's postings block.

2. **Secondary Storage (Disk) - Postings File (`postings.dat`)**:
   Postings lists are stored sequentially on disk in binary UTF-8 format:
   `[(doc_id, [pos1, pos2, ...]), ...]`

3. **Query Retrieval via Seek**:
   When evaluating a query, the engine looks up the term in RAM, gets `(offset, byte_len)`, jumps directly to that position on the disk using `file.seek(offset)`, and reads only that term's postings. The full index is never loaded into RAM.

---

## 3. Module Descriptions

All source code is organized under `src/`:

- **`src/config.py`**:
  Defines project directory paths, file locations, and encoding settings (`utf-8`).

- **`src/corpus_collector.py`**:
  Fetches Tamil Wikipedia articles using the Wikimedia API, saves them into a structured XML file, and provides XML parsing functions compatible with Wikipedia and FIRE datasets.

- **`src/tokenizer.py`**:
  Performs Tamil text normalization using Unicode NFC, removes zero-width spaces, tokenizes words using the regex pattern `[\u0B80-\u0BFFa-zA-Z0-9]+`, and produces 1-based token position pairs `(term, position)`.

- **`src/indexer.py`**:
  Accumulates tokens into the inverted structure `term -> {doc_id: [positions]}` and computes Document Frequency (DF) and Collection Frequency (CF).

- **`src/secondary_storage.py`**:
  Handles disk I/O. `serialize_and_write_postings` writes postings sequentially to disk using `tell()` to record byte offsets and builds the RAM vocabulary table. `read_postings_from_disk` retrieves individual postings lists via `seek(offset)`.

- **`src/query_engine.py`**:
  Implements the two-pointer Positional Intersect algorithm for exact phrase matching ($k=1$) and proximity queries ($1 \le |pos_1 - pos_2| \le k$).

- **`src/main.py`**:
  Command-line interface to index the corpus and execute phrase or proximity queries.

---

## 4. How to Run the Code

Run all commands from the project root (`IR_native_lang/`).

### 1. Build the Index
```bash
python3 -m src.main --index
```
Parses `data/raw/tamil_wiki_corpus.xml`, indexes 56,168 tokens across 21,182 terms, and writes `data/index/postings.dat` (468 KB) on disk and `data/index/vocab.json`.

### 2. Run Phrase Queries
```bash
python3 -m src.main --phrase "தமிழ்நாடு"
python3 -m src.main --phrase "சூரியக் குடும்பம்"
```

### 3. Run Proximity Queries (`/k`)
```bash
python3 -m src.main --proximity "சென்னை" "நகரம்" 3
```

---

## 5. Output and Evaluation Files

- **`output/test_cases_output.txt`**:
  Includes 5 test cases testing:
  1. Exact phrase query: `"தமிழ்நாடு"` -> matches 6 documents.
  2. Exact 3-word phrase query: `"சூரியக் குடும்பம்"` -> matches Doc 4.
  3. Proximity query: `சென்னை /3 நகரம்` -> matches Doc 3.
  4. Literary phrase query: `"இயற்கை வேளாண்மை"` -> matches Doc 6.
  5. Negative test case: `"நிலா வேதியியல் சூரியக்"` -> 0 matches (verifying 0 false positives).

- **`output/10_rare_terms_index.txt`**:
  Includes 10 authentic Tamil terms with $DF = 1$ and $CF = 1$, displaying their collection frequency, document frequency, disk byte offset, block length, document ID, title, and token positions.
