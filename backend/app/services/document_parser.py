from pathlib import Path

import pandas as pd
from docx import Document
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv"}


def parse_document(path: Path) -> str:
    extension = path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError("Unsupported file type. Use PDF, DOCX, TXT, or CSV.")
    if extension == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if extension == ".docx":
        doc = Document(str(path))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs).strip()
    if extension == ".csv":
        frame = pd.read_csv(path)
        return frame.to_csv(index=False)
    return path.read_text(encoding="utf-8", errors="ignore").strip()
