"""
ocr_parser.py
Handles document ingestion: PDF/image upload, OCR text extraction, and layout parsing.

Libraries used:
- PyMuPDF (fitz)  -> PDF text/layout/metadata extraction, page rasterization
- pytesseract     -> OCR engine (Tesseract) for scanned images and rasterized PDF pages
- Pillow (PIL)    -> image handling
"""

import io
import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

# Fallback for Windows Tesseract installation path
if os.name == 'nt':
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path


def load_document(file_bytes: bytes, filename: str):
    """
    Loads a PDF or image file and returns a list of PIL Images (one per page)
    plus raw PyMuPDF metadata if it's a PDF.
    """
    ext = filename.lower().split(".")[-1]
    metadata = {}
    images = []

    if ext == "pdf":
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        metadata = dict(doc.metadata)
        metadata["page_count"] = doc.page_count
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            images.append(img)
        doc.close()
    else:
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        images.append(img)
        metadata = extract_image_metadata(img, file_bytes)

    return images, metadata


def extract_image_metadata(img: Image.Image, file_bytes: bytes):
    """Pulls EXIF metadata from an image (used in forensic analysis too)."""
    meta = {"format": img.format or "unknown", "size": img.size, "mode": img.mode}
    try:
        exif = img.getexif()
        if exif:
            meta["exif_tags"] = len(exif)
            meta["software"] = exif.get(305, "not present")  # Tag 305 = Software
    except Exception:
        meta["exif_tags"] = 0
    meta["file_size_kb"] = round(len(file_bytes) / 1024, 1)
    return meta


def run_ocr(images):
    """
    Runs Tesseract OCR across all pages/images and returns combined text
    plus per-page confidence scores.
    """
    full_text = []
    confidences = []

    for img in images:
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        page_text = " ".join([w for w in data["text"] if w.strip()])
        full_text.append(page_text)

        confs = [int(c) for c in data["conf"] if c != "-1"]
        if confs:
            confidences.append(sum(confs) / len(confs))

    avg_confidence = round(sum(confidences) / len(confidences), 1) if confidences else 0.0
    return "\n".join(full_text), avg_confidence
