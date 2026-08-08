"""
api.py — SafeHire AI backend API.

Serves two things:
  1. POST /api/verify — runs the full offline verification pipeline on an
     uploaded document and returns a JSON report.
  2. The static frontend (frontend/index.html) at "/".

Run with:  uvicorn api:app --reload
Then open: http://localhost:8000
"""

import base64
import io
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from modules.ocr_parser import load_document, run_ocr
from modules.forensics import run_forensics
from modules.semantic_match import semantic_similarity_score
from modules.ai_detector import ai_generation_likelihood
from modules.scorer import compute_validity_score, DEFAULT_WEIGHTS

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="SafeHire AI API")

# CORS left open for local development (e.g. running the frontend from a
# different dev server/port). Same-origin when served via this app directly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _image_to_base64(img) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


@app.post("/api/verify")
async def verify_document(
    file: UploadFile = File(...),
    doc_type: str = Form("resume"),
    w_ocr: float = Form(DEFAULT_WEIGHTS["ocr_confidence"]),
    w_forensics: float = Form(DEFAULT_WEIGHTS["forensics"]),
    w_semantic: float = Form(DEFAULT_WEIGHTS["semantic_match"]),
    w_ai: float = Form(DEFAULT_WEIGHTS["ai_detection"]),
):
    file_bytes = await file.read()

    images, metadata = load_document(file_bytes, file.filename)
    extracted_text, ocr_confidence = run_ocr(images)
    forensic_result = run_forensics(images, metadata)
    semantic_score, _ = semantic_similarity_score(extracted_text, doc_type)
    ai_human_score, ai_signals = ai_generation_likelihood(extracted_text)

    total_w = w_ocr + w_forensics + w_semantic + w_ai
    weights = (
        {
            "ocr_confidence": w_ocr / total_w,
            "forensics": w_forensics / total_w,
            "semantic_match": w_semantic / total_w,
            "ai_detection": w_ai / total_w,
        }
        if total_w > 0
        else DEFAULT_WEIGHTS
    )

    final_score, breakdown, verdict = compute_validity_score(
        ocr_confidence, forensic_result["combined_score"],
        semantic_score, ai_human_score, weights,
    )

    # Clean metadata for JSON (tuples -> lists, drop non-serializable keys)
    clean_metadata = {}
    for k, v in metadata.items():
        if isinstance(v, tuple):
            clean_metadata[k] = list(v)
        elif isinstance(v, (str, int, float, bool)) or v is None:
            clean_metadata[k] = v
        else:
            clean_metadata[k] = str(v)

    ai_modified_answer = (
        "Yes, attributes likely updated or generated using AI tools." 
        if ai_human_score < 65 
        else "No, appears human-authored and not significantly AI altered."
    )

    return JSONResponse({
        "final_score": final_score,
        "verdict": verdict,
        "breakdown": breakdown,
        "ocr": {
            "confidence": ocr_confidence,
            "extracted_text": extracted_text,
        },
        "forensics": {
            "ela_score": forensic_result["ela_score"],
            "meta_score": forensic_result["meta_score"],
            "combined_score": forensic_result["combined_score"],
            "flags": forensic_result["flags"],
            "heatmap_base64": _image_to_base64(forensic_result["heatmap"]),
        },
        "semantic": {
            "score": semantic_score, 
            "doc_type": doc_type,
            "relevance": f"{semantic_score}/100"
        },
        "ai_detection": {
            "human_likelihood": ai_human_score, 
            "ai_modified_answer": ai_modified_answer,
            "signals": ai_signals
        },
        "metadata": clean_metadata,
    })


@app.get("/")
async def index():
    return FileResponse(FRONTEND_DIR / "index.html")


# Serve any additional frontend assets (none required for the current
# single-file build, but kept for extensibility)
if (FRONTEND_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
