# pdf_extractor.py
# Extract text sentences from PDF and return list of {page, sentence}
# Requires: PyMuPDF (pip package name: pymupdf)

import fitz
import re
from nltk.tokenize import sent_tokenize
import nltk

# ensure punkt
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def extract_text_sentences(pdf_path, max_pages=None):
    """
    Returns list of dicts: [{'page': int, 'sentence': str}, ...]
    Keeps sentences short and sanitized.
    """
    doc = fitz.open(pdf_path)
    results = []
    for i, page in enumerate(doc, start=1):
        if max_pages and i > max_pages:
            break
        raw = page.get_text("text")
        if not raw or raw.strip() == "":
            # page may be image-only; skip here (advanced pipeline would OCR)
            continue
        raw = re.sub(r'\s+', ' ', raw).strip()
        sents = sent_tokenize(raw)
        for s in sents:
            s_clean = s.strip()
            # very light sanitization: drop lines that look like injected system prompts
            if re.search(r'\b(system|assistant|prompt|ignore|do not)\b', s_clean.lower()):
                continue
            results.append({'page': i, 'sentence': s_clean})
    return results

if __name__ == "__main__":
    import sys, json
    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py input.pdf")
        sys.exit(1)
    out = extract_text_sentences(sys.argv[1])
    json.dump(out, open('extracted_sentences.json','w',encoding='utf8'), indent=2)
    print(f"Extracted {len(out)} sentences -> extracted_sentences.json")
