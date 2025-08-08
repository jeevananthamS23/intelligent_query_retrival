import requests
import fitz  # PyMuPDF
import re
import asyncio
import tiktoken
import validators  # pip install validators

async def process_document(blob_or_text: str) -> tuple[str, dict]:
    """
    If input is a valid URL -> Download PDF and extract text.
    If input is not a URL -> Treat it as raw plain text.
    """
    loop = asyncio.get_event_loop()

    # Case 1: PDF from URL
    if validators.url(blob_or_text):
        resp = await loop.run_in_executor(None, lambda: requests.get(blob_or_text))
        resp.raise_for_status()
        pdf = fitz.open(stream=resp.content, filetype="pdf")
        doc_text = ""
        for page in pdf:
            doc_text += page.get_text()
        return doc_text, {"num_pages": pdf.page_count}

    # Case 2: Direct raw text
    return blob_or_text.strip(), {"num_pages": 1}


def split_into_clauses(text: str) -> list[dict]:
    """
    Tries to split text by legal-style headings like "Section 1", "Section 1.1 ...".
    Falls back to paragraph-level splitting if no such headers are found.
    Returns list of {"section": str, "text": str}.
    """
    patterns = [
        r'(Section\s+\d+[\.\d]*\s*[\w\s]*)',
        r'(Clause\s+\d+[\.\d]*\s*[\w\s]*)',
        r'([A-Z][\w\s]*:\s*)',
        r'(\d+\.\s*[A-Z][\w\s]*)'
    ]
    
    for pattern in patterns:
        sections = re.split(pattern, text)
        if len(sections) > 3:
            clauses = [{"section": s.strip(), "text": t.strip()} for s, t in zip(sections[1::2], sections[2::2])]
            filtered_clauses = [c for c in clauses if c["text"]]
            if filtered_clauses:
                return filtered_clauses
    
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50]
    fallback_clauses = [{"section": f"Paragraph {i+1}", "text": p} for i, p in enumerate(paragraphs)]
    
    if not fallback_clauses or any(len(c["text"]) > 2000 for c in fallback_clauses):
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        fallback_clauses = [{"section": f"Sentence {i+1}", "text": s} for i, s in enumerate(sentences) if len(s) > 20]
    
    if not fallback_clauses:
        return [{"section": "Entire Document", "text": text.strip()}]
    
    return fallback_clauses


def chunk_text_by_tokens(text: str, max_tokens: int = 1000, overlap: int = 100) -> list[str]:
    """
    Splits text into token-based chunks with optional overlap.
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + max_tokens
        chunk_tokens = tokens[start:end]
        chunks.append(encoding.decode(chunk_tokens))
        start += max_tokens - overlap
    return chunks
