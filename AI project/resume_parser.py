"""Safe PDF upload and text extraction utilities."""
from __future__ import annotations

import re
import uuid
from pathlib import Path

import fitz  # PyMuPDF

from config import MAX_UPLOAD_SIZE_MB, UPLOAD_DIR


def save_uploaded_resume(uploaded_file, user_id: int) -> Path:
    """Validate and persist a Streamlit UploadedFile with a collision-safe name."""
    if not uploaded_file.name.lower().endswith(".pdf"):
        raise ValueError("Please upload a PDF resume.")
    if uploaded_file.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise ValueError(f"Resume must be smaller than {MAX_UPLOAD_SIZE_MB} MB.")
    target_dir = UPLOAD_DIR / str(user_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    safe_stem = re.sub(r"[^A-Za-z0-9_-]", "_", Path(uploaded_file.name).stem)[:80] or "resume"
    target_path = target_dir / f"{safe_stem}_{uuid.uuid4().hex[:10]}.pdf"
    target_path.write_bytes(uploaded_file.getbuffer())
    return target_path


def extract_pdf_text(pdf_path: str | Path) -> str:
    """Extract readable text from every page of a PDF."""
    document = fitz.open(str(pdf_path))
    try:
        text = "\n".join(page.get_text("text") for page in document)
    finally:
        document.close()
    cleaned = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(cleaned) < 30:
        raise ValueError("No readable text was found. Please upload a text-based PDF resume.")
    return cleaned
