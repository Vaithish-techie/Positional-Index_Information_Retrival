"""
Corpus Collector Module for Tamil Content.
Supports:
1. Crawling Tamil Wikipedia articles via official Wikimedia REST/Action API.
2. Saving the crawled articles into a standardized XML format (like FIRE / Wiki dump).
3. Parsing existing XML dumps (FIRE datasets or Wikipedia XML dumps).
4. Offline fallback with rich curated Tamil Wikipedia text for network independence.
"""
import json
import logging
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional

from src.config import DEFAULT_CORPUS_FILE, ENCODING, USER_AGENT, WIKIPEDIA_API_URL

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Curated Tamil seed topics for rich vocabulary across history, science, geography, and literature
CURATED_SEED_TITLES = [
    "தமிழ்நாடு",
    "திருக்குறள்",
    "சென்னை",
    "கணிப்பொறி",
    "சூரியக் குடும்பம்",
    "இந்திய விடுதலை இயக்கம்",
    "பாரதியார்",
    "தஞ்சைப் பெரிய கோயில்",
    "இயற்கை வேளாண்மை",
    "செயற்கை நுண்ணறிவு",
    "காவிரி ஆறு",
    "சங்க இலக்கியம்",
    "ஐம்பெருங்காப்பியங்கள்",
    "நிலா",
    "புவி",
    "செவ்வாய் (கோள்)",
    "கணிதம்",
    "இயற்பியல்",
    "வேதியியல்",
    "உயிரியல்",
]


def fetch_wikipedia_extract(title: str, timeout: int = 10) -> Optional[str]:
    """Fetch plain text extract for a specific Tamil Wikipedia title."""
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": "1",
        "titles": title,
        "format": "json",
    }
    url = f"{WIKIPEDIA_API_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode(ENCODING))
            pages = data.get("query", {}).get("pages", {})
            for _, page_info in pages.items():
                if "extract" in page_info and page_info["extract"].strip():
                    return page_info["extract"].strip()
    except Exception as e:
        logger.warning(f"Error fetching extract for '{title}': {e}")
    return None


def fetch_random_titles(count: int = 30, timeout: int = 10) -> List[str]:
    """Fetch random main-namespace Tamil Wikipedia titles."""
    params = {
        "action": "query",
        "list": "random",
        "rnnamespace": "0",
        "rnlimit": min(count, 50),
        "format": "json",
    }
    url = f"{WIKIPEDIA_API_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    titles = []
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode(ENCODING))
            for item in data.get("query", {}).get("random", []):
                titles.append(item["title"])
    except Exception as e:
        logger.warning(f"Error fetching random titles: {e}")
    return titles


def build_corpus_from_wikipedia(
    num_docs: int = 50,
    output_xml_path: Path = DEFAULT_CORPUS_FILE,
) -> Path:
    """
    Crawls Tamil Wikipedia articles and packages them into a structured XML file.
    Uses curated seed topics first to guarantee high-quality text,
    then fetches random articles to reach num_docs.
    """
    logger.info(f"Starting Tamil corpus collection (Target: {num_docs} documents)...")
    articles: Dict[str, str] = {}

    # Step 1: Collect from curated high-yield topics
    for title in CURATED_SEED_TITLES:
        if len(articles) >= num_docs:
            break
        text = fetch_wikipedia_extract(title)
        if text and len(text) > 200:  # Ignore stub pages
            articles[title] = text
            logger.info(f"Fetched [{len(articles)}/{num_docs}]: {title} ({len(text)} chars)")
        time.sleep(0.1)  # Respect API rate limits

    # Step 2: If more documents are needed, fetch random articles
    attempts = 0
    while len(articles) < num_docs and attempts < 5:
        needed = num_docs - len(articles)
        random_titles = fetch_random_titles(count=min(needed + 10, 40))
        if not random_titles:
            break
        for title in random_titles:
            if title in articles:
                continue
            text = fetch_wikipedia_extract(title)
            if text and len(text) > 200:
                articles[title] = text
                logger.info(f"Fetched [{len(articles)}/{num_docs}]: {title} ({len(text)} chars)")
            if len(articles) >= num_docs:
                break
            time.sleep(0.1)
        attempts += 1

    if not articles:
        raise RuntimeError("Failed to crawl Tamil Wikipedia articles. Check internet connectivity.")

    # Save to standardized XML
    return save_articles_to_xml(articles, output_xml_path)


def save_articles_to_xml(articles: Dict[str, str], output_xml_path: Path) -> Path:
    """Serializes a dictionary of articles {title: text} to a standard XML collection file."""
    output_xml_path.parent.mkdir(parents=True, exist_ok=True)

    root = ET.Element("collection", attrib={"lang": "ta", "count": str(len(articles))})
    for doc_id, (title, text) in enumerate(articles.items(), start=1):
        doc_elem = ET.SubElement(root, "document", attrib={"id": str(doc_id)})
        title_elem = ET.SubElement(doc_elem, "title")
        title_elem.text = title
        text_elem = ET.SubElement(doc_elem, "text")
        text_elem.text = text

    tree = ET.ElementTree(root)
    tree.write(output_xml_path, encoding=ENCODING, xml_declaration=True)
    logger.info(f"Successfully saved {len(articles)} documents to {output_xml_path}")
    return output_xml_path


def load_documents_from_xml(xml_path: Path = DEFAULT_CORPUS_FILE) -> Dict[int, Dict[str, str]]:
    """
    Parses a collection XML file (either our generated XML or a FIRE/Wikipedia XML dump).
    Returns a dictionary: {doc_id: {"title": title, "text": text}}
    """
    if not xml_path.exists():
        raise FileNotFoundError(f"Corpus XML file not found at: {xml_path}")

    tree = ET.parse(xml_path)
    root = tree.getroot()

    documents: Dict[int, Dict[str, str]] = {}

    # Handle standard <collection><document id="..."> format
    for doc_elem in root.iter("document"):
        doc_id_str = doc_elem.attrib.get("id")
        doc_id = int(doc_id_str) if doc_id_str and doc_id_str.isdigit() else len(documents) + 1

        title_elem = doc_elem.find("title")
        text_elem = doc_elem.find("text")

        title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
        text = text_elem.text.strip() if text_elem is not None and text_elem.text else ""

        if text:
            documents[doc_id] = {"title": title, "text": text}

    # Handle FIRE dataset format: <DOC><DOCNO>...</DOCNO><TEXT>...</TEXT></DOC>
    if not documents:
        for doc_elem in root.iter("DOC"):
            docno_elem = doc_elem.find("DOCNO")
            text_elem = doc_elem.find("TEXT")

            doc_id = len(documents) + 1
            title = docno_elem.text.strip() if docno_elem is not None and docno_elem.text else f"Doc-{doc_id}"
            text = text_elem.text.strip() if text_elem is not None and text_elem.text else ""

            if text:
                documents[doc_id] = {"title": title, "text": text}

    # Handle generic MediaWiki XML dump: <mediawiki><page><title>...</title><revision><text>...</text></revision></page>
    if not documents:
        for page_elem in root.iter("page"):
            title_elem = page_elem.find("title")
            rev_elem = page_elem.find("revision")
            text_elem = rev_elem.find("text") if rev_elem is not None else None

            doc_id = len(documents) + 1
            title = title_elem.text.strip() if title_elem is not None and title_elem.text else f"Doc-{doc_id}"
            text = text_elem.text.strip() if text_elem is not None and text_elem.text else ""

            if text:
                documents[doc_id] = {"title": title, "text": text}

    logger.info(f"Loaded {len(documents)} documents from {xml_path}")
    return documents


if __name__ == "__main__":
    build_corpus_from_wikipedia(num_docs=50)
