# 🎯 IR Quest: Tamil Positional Indexer with Secondary Storage

> **Mission**: Build an industrial-grade **Positional Indexer** for **Tamil** from scratch in **10 Levels**, adhering strictly to Information Retrieval theory (Manning, Raghavan, Schütze) and the assignment specifications.
>
> **Core Requirement**: The **Vocabulary (Lexicon)** must reside in **Main Memory (RAM)**, while the entire **Postings Lists** reside on **Secondary Storage (Disk / SSD)** with $O(1)$ random-seek disk retrieval.
>
> **Language Choice**: **Tamil (தமிழ்)** — Dravidian script (Unicode block `U+0B80–U+0BFF`). Chosen for its agglutinative morphology, complex grapheme clusters, and high evaluation weightage for Indian languages.

---

## 🗺️ The 10-Level Roadmap

```
+-------------------------------------------------------------------------------+
| LEVEL 1: IR Foundations & System Architecture Blueprint                      |
|          -> Positional Index vs Inverted Index | CF vs DF | Memory vs Disk   |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
| LEVEL 2: Tamil Corpus Acquisition Engine                                      |
|          -> Wikipedia API Crawler & FIRE-compatible XML Generator             |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
| LEVEL 3: Tamil Linguistic Tokenizer & Position Streamer                       |
|          -> Unicode Normalization | Word Boundary Regex | Position Tracking  |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
| LEVEL 4: Positional Postings Accumulator                                      |
|          -> CF (Collection Frequency) & DF (Document Frequency) Analytics     |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
| LEVEL 5: Memory-to-Disk Serialization Architecture                            |
|          -> Binary Postings Pack format | Seek Offset Table Formulation       |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
| LEVEL 6: Secondary Storage Indexer Engine                                     |
|          -> Writing `postings.dat` (Disk) & `vocab.json` (RAM Lexicon)       |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
| LEVEL 7: Low-Latency Secondary Memory Seek Retriever                          |
|          -> O(1) file.seek() disk reader | Minimal RAM footprint benchmark   |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
| LEVEL 8: Positional Query & Phrase Search Engine                              |
|          -> Positional-Intersect Algorithm | Exact Phrase & Proximity (/k)    |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
| LEVEL 9: Rigorous Verification, Test Cases & Rare Terms                       |
|          -> 5 Diverse Query Test Cases | 10 Rare Terms Positional Dump        |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
| LEVEL 10: Submission Packaging & Documentation                                |
|          -> README.md | <RollNo>-src.zip | Verification Checklist            |
+-------------------------------------------------------------------------------+
```

---

## 🧭 Quest Breakdown by Level

### Level 1: Foundations & Architecture
- **Concept**:
  - In a standard inverted index: `term -> [doc_id, doc_id, ...]` (cannot answer phrase queries like `"தமிழ் நாடு"` or proximity queries like `"சென்னை /3 பல்கலைக்கழகம்"`).
  - In a **Positional Index**: `term -> { doc_id: [pos1, pos2, ...], ... }`.
  - **Collection Frequency (CF)**: Total occurrences of the term across all documents in the entire collection ($\sum \text{tf}$).
  - **Document Frequency (DF)**: Number of unique documents containing the term.
  - **Memory vs Disk Trade-off**:
    - Vocabulary size $|V|$ grows roughly as $O(k \cdot N^\beta)$ by Heaps' Law ($~10^4 - 10^5$ terms), which easily fits in main memory (a few megabytes).
    - Postings lists grow linearly with collection size $O(T)$ (gigabytes to terabytes), so they must be stored on secondary storage.
    - Each vocabulary entry stores `(CF, DF, disk_byte_offset, byte_length)`.

### Level 2: Tamil Corpus Acquisition
- Download 50-100 real articles from Tamil Wikipedia via the official Wikimedia API (or parse FIRE XML).
- Standardize into an XML collection format:
  ```xml
  <collection>
    <document id="1" title="...">
      <text>...</text>
    </document>
  </collection>
  ```

### Level 3: Tamil Linguistic Tokenizer & Position Tracker
- Tamil script characters range `\u0B80-\u0BFF` including vowels, consonants, combining vowel signs (*matras*), and pulli/virama (`\u0BCD`).
- Maintain exact 1-based token positions `(doc_id, term, position)`.

### Level 4: Positional Postings Accumulator
- Accumulate positional entries:
  - `vocab[term]["df"] = len(postings)`
  - `vocab[term]["cf"] = sum(len(positions) for positions in postings.values())`
- Validate that $CF \ge DF$ for all terms.

### Level 5 & 6: Secondary Storage Serialization Engine
- Format of `postings.dat`:
  - Binary/compact serialized stream of `(doc_id, count, [pos1, pos2, ...])`.
- In-Memory Lexicon:
  - `{ "term": {"cf": 45, "df": 12, "offset": 1048576, "len": 128} }`
- RAM holds only the lexicon. Disk holds the actual posting lists.

### Level 7: Secondary Memory Seek Retriever
- Lookup term in RAM Lexicon -> Get `offset` and `length`.
- `f.seek(offset)` -> `f.read(length)` -> Deserialize postings.
- RAM usage remains $O(1)$ with respect to postings size!

### Level 8: Positional Query Evaluator
- Exact phrase query: `"கற்க கசடற"` $\rightarrow$ finds docs where term1 and term2 are consecutive ($pos_2 = pos_1 + 1$).
- Proximity search: `TERM1 /k TERM2` $\rightarrow$ finds docs where $|pos_1 - pos_2| \le k$.

### Level 9: Test Cases & 10 Rare Terms Dump
- 5 comprehensive test queries:
  1. Exact 2-word phrase query.
  2. Exact 3-word phrase query.
  3. Proximity query with $k=3$.
  4. Non-matching phrase (verifying zero false positives).
  5. Boolean AND + Positional constraint.
- 10 rare terms (terms with $DF=1$ and low $CF$) with their complete postings list and positions.

### Level 10: Submission Packaging
- Structured project repository.
- `README.md` with complete architecture and execution guide.
- Generation of `<YourRollNo>-src.zip`.
