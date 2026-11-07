# 🇮🇳 Tamil Positional Indexer with Secondary Storage Architecture

An Information Retrieval system built from scratch for the **Tamil (தமிழ்)** language, implementing a **Positional Inverted Index** with strict separation between **Main Memory (RAM)** and **Secondary Storage (Disk / SSD)**.

Developed as part of the Information Retrieval (IR) assignment on Indian Language Collections (FIRE / Wikipedia).

---

## 🏛️ System Architecture

The indexer adheres to textbook Information Retrieval architecture (*Manning, Raghavan, Schütze — Introduction to Information Retrieval*):

```
                   +-----------------------------------------------+
                   |              Tamil Corpus (XML)               |
                   |       (50 Wikipedia Articles, 1.4 MB)        |
                   +-----------------------------------------------+
                                          │
                                          ▼
                   +-----------------------------------------------+
                   |     Unicode Linguistic Tokenizer (NFC)        |
                   |   - Word boundary extraction (\u0B80-\u0BFF)  |
                   |   - 1-based token position streaming          |
                   +-----------------------------------------------+
                                          │
                                          ▼
                   +-----------------------------------------------+
                   |       Positional Index Accumulator            |
                   |   - term -> { doc_id: [pos1, pos2, ...] }     |
                   |   - CF & DF calculation                       |
                   +-----------------------------------------------+
                                          │
                       ┌──────────────────┴──────────────────┐
                       ▼                                     ▼
        +-----------------------------+       +-----------------------------+
        |     MAIN MEMORY (RAM)       |       |  SECONDARY STORAGE (DISK)   |
        |     Vocab Lexicon Table     |       |        postings.dat         |
        |-----------------------------|       |-----------------------------|
        | term: {                     |       | Binary / UTF-8 packed       |
        |   "cf": int,                |  seek | postings lists:             |
        |   "df": int,                | =====>| [ (doc_id, [pos1, ...]), .. ]
        |   "offset": int (byte addr),|       |                             |
        |   "byte_len": int           |       | O(1) random-seek retrieval  |
        | }                           |       | No full index loaded in RAM |
        +-----------------------------+       +-----------------------------+
                       ▲                                     ▲
                       └──────────────────┬──────────────────┘
                                          │
                                          ▼
                   +-----------------------------------------------+
                   |        Query Evaluation Engine                |
                   |   - Positional Intersect (Exact Phrase: k=1)  |
                   |   - Proximity Search (Window distance /k)     |
                   +-----------------------------------------------+
```

---

## 📦 Project Structure & Module Descriptions

```
IR_native_lang/
├── README.md                          # Comprehensive documentation & execution guide
├── QUEST_PLAN.md                      # 10-level pedagogical roadmap
├── data/
│   ├── raw/
│   │   └── tamil_wiki_corpus.xml      # 50 crawled authentic Tamil Wikipedia articles
│   └── index/
│       ├── vocab.json                 # In-Memory Vocabulary Table (CF, DF, offset, length)
│       └── postings.dat               # Secondary Memory Postings Storage (SSD/HDD)
├── src/
│   ├── __init__.py                    # Python package initializer
│   ├── config.py                      # Centralized paths and hyperparameters
│   ├── corpus_collector.py            # Level 2: Wikimedia API crawler & FIRE/Wiki XML parser
│   ├── tokenizer.py                   # Level 2: Tamil Unicode NFC tokenizer & position tracker
│   ├── indexer.py                     # Level 3 & 4: Positional index builder & CF/DF analytics
│   ├── secondary_storage.py           # Level 5, 6 & 7: Disk serializer & O(1) seek retriever
│   ├── query_engine.py                # Level 8 & 9: Positional intersect & proximity evaluator
│   └── main.py                        # Level 10: Unified CLI application & packager
├── tests/
│   ├── test_level2.py                 # Unit tests for tokenizer & positions
│   ├── test_level3_4.py               # Unit tests for index accumulator & CF/DF
│   ├── test_level5_6_7.py             # Unit tests for secondary storage seek & read
│   └── test_level8_9.py               # Unit tests for phrase search & proximity queries
└── output/
    ├── test_cases_output.txt          # Assignment Deliverable: 5 Test cases with outputs
    └── 10_rare_terms_index.txt        # Assignment Deliverable: 10 Rare terms with positional lists
```

### Module Descriptions:

1. **`src/tokenizer.py`**:
   - Implements Unicode NFC normalization (`unicodedata.normalize('NFC', text)`) to properly compose Tamil base characters and vowel signs (*matras*).
   - Strips zero-width invisible spaces (`\u200b`, `\u200c`, `\u200d`).
   - Uses pre-compiled regex `[\u0B80-\u0BFFa-zA-Z0-9]+` to extract words, punctuation-free.
   - Streams 1-based token positions `(term, position)` for positional indexing.

2. **`src/indexer.py`**:
   - Accumulates tokens into the inverted structure: `term -> {doc_id: [positions]}`.
   - Computes Document Frequency ($DF = \text{number of documents}$) and Collection Frequency ($CF = \sum \text{positions}$).
   - Guarantees the IR invariant: $CF \ge DF$.

3. **`src/secondary_storage.py`**:
   - **Requirement (d) Compliance**: Writes postings lists sequentially into `postings.dat` on secondary storage.
   - Uses `file.tell()` to capture the exact disk byte address (`offset`) and block length (`byte_len`).
   - Builds the in-memory Vocabulary table loaded into RAM.
   - Provides `read_postings_from_disk(offset, byte_len)` which executes `file.seek(offset)` to jump directly to the byte address on the SSD, reading only that term's postings without loading the full index into RAM.

4. **`src/query_engine.py`**:
   - Implements Manning et al.'s **Positional Intersect algorithm** using a two-pointer merge on document IDs, followed by nested two-pointer position matching.
   - Supports **Exact Phrase Queries** (consecutive words where $pos_2 - pos_1 = 1$, chainable for multi-word phrases).
   - Supports **Proximity Queries** (`term1 /k term2`, matching documents where $1 \le |pos_1 - pos_2| \le k$).

5. **`src/main.py`**:
   - Unified command-line interface for indexing, querying, testing, and packaging.

---

## 🚀 How to Run the Code

### 1. Prerequisites
- Python 3.8+ (Tested on Python 3.13)
- No external heavy dependencies required (uses standard library `urllib`, `xml`, `re`, `json`, `pathlib`).

### 2. Run All Unit Tests
Run the test harness for each level:
```bash
python3 tests/test_level2.py
python3 tests/test_level3_4.py
python3 tests/test_level5_6_7.py
python3 tests/test_level8_9.py
```

### 3. Build the Full Positional Index
```bash
python3 -m src.main --index
```
*Output:*
- Indexes 50 Tamil documents (56,168 tokens, 21,182 unique terms).
- Writes secondary memory postings to `data/index/postings.dat` (468 KB).
- Saves RAM lexicon to `data/index/vocab.json`.

### 4. Run Phrase & Proximity Queries
**Exact Phrase Query:**
```bash
python3 -m src.main --phrase "தமிழ்நாடு"
python3 -m src.main --phrase "சூரியக் குடும்பம்"
```

**Proximity Query (`/k`):**
```bash
python3 -m src.main --proximity "சென்னை" "நகரம்" 3
```

### 5. Generate Assignment Deliverables (5 Test Cases + 10 Rare Terms)
```bash
python3 -m src.main --deliverables
```
Generates:
- `output/test_cases_output.txt`
- `output/10_rare_terms_index.txt`

### 6. Create Submission ZIP Archive (`<RollNo>-src.zip`)
```bash
python3 -m src.main --package <YourRollNo>
```
*Example:*
```bash
python3 -m src.main --package CS21B001
```
Creates `CS21B001-src.zip` containing all source code, tests, documentation, and output files.

---

## 📊 Index Statistics & Benchmarks

| Metric | Measurement |
| :--- | :--- |
| **Language** | Tamil (தமிழ், Unicode `U+0B80–U+0BFF`) |
| **Total Documents** | 50 full articles |
| **Total Tokens Indexed** | 56,168 tokens |
| **Unique Vocabulary Terms** | 21,182 terms |
| **Secondary Memory File (`postings.dat`)** | 468.65 KB |
| **In-Memory Lexicon Size** | ~1.8 MB (JSON format), < 400 KB in raw memory |
| **Index Construction Time** | < 0.35 seconds |
| **Disk Seek Latency per Query** | < 0.15 milliseconds |

---

## 📋 Deliverables Summary

### 1. 10 Rare Terms with Positional Index (Sample excerpt from `output/10_rare_terms_index.txt`):
All 10 terms have $DF=1, CF=1$, featuring genuine Tamil words:
1. **`அஃதாவது`** (That is to say) $\rightarrow$ Doc 2 (*திருக்குறள்*), Pos `[366]`, Disk Offset: `Byte 37782`
2. **`அகக்கோள்களைப்`** (Inner planets) $\rightarrow$ Doc 4 (*சூரியக் குடும்பம்*), Pos `[183]`, Disk Offset: `Byte 37837`
3. **`அகண்ட`** (Vast) $\rightarrow$ Doc 8 (*காவிரி ஆறு*), Pos `[471]`, Disk Offset: `Byte 37848`
4. **`அகண்டு`** (Widened) $\rightarrow$ Doc 8 (*காவிரி ஆறு*), Pos `[466]`, Disk Offset: `Byte 37859`
5. **`அகதிகளால்`** (By refugees) $\rightarrow$ Doc 30 (*சா. ஜே. வே. செல்வநாயகம்*), Pos `[344]`, Disk Offset: `Byte 37870`
6. **`அகதிகளுக்கு`** (To refugees) $\rightarrow$ Doc 30, Pos `[360]`, Disk Offset: `Byte 37882`
7. **`அகத்திய`** (Agastya's) $\rightarrow$ Doc 8, Pos `[42]`, Disk Offset: `Byte 37894`
8. **`அகத்தியமலை`** (Agastya Mountain) $\rightarrow$ Doc 8, Pos `[118]`, Disk Offset: `Byte 37905`
9. **`அகத்தியருக்குக்`** (To Sage Agastya) $\rightarrow$ Doc 1 (*தமிழ்நாடு*), Pos `[666]`, Disk Offset: `Byte 37919`
10. **`அகநானூற்றுப்`** (Of Agananuru) $\rightarrow$ Doc 33 (*இளங்கீரனார்*), Pos `[21]`, Disk Offset: `Byte 37936`

### 2. 5 Test Cases Summary (from `output/test_cases_output.txt`):
- **Test Case 1 (Exact Phrase)**: `"தமிழ்நாடு"` $\rightarrow$ Matched Docs: `[1, 3, 5, 6, 8, 47]`
- **Test Case 2 (3-Word Phrase)**: `"சூரியக் குடும்பம்"` $\rightarrow$ Matched Doc: `[4]`
- **Test Case 3 (Proximity Query /3)**: `சென்னை /3 நகரம்` $\rightarrow$ Matched Doc: `[3]`
- **Test Case 4 (Literary Phrase)**: `"இயற்கை வேளாண்மை"` $\rightarrow$ Matched Doc: `[6]`
- **Test Case 5 (Negative Test)**: `"நிலா வேதியியல் சூரியக்"` $\rightarrow$ Matched Docs: `[]` (0 false positives)
