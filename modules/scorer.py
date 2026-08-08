"""
scorer.py
Combines all upstream signal scores into a single fixed-scale Semantic
Validity Score (0-100%), which is SafeHire AI's headline output.

Design principle: explainable, not a black box. The final score is a
transparent weighted sum, and every sub-score plus any raised flags are
surfaced to the reviewer alongside it — never just a bare percentage.
"""

DEFAULT_WEIGHTS = {
    "ocr_confidence": 0.10,
    "forensics": 0.35,
    "semantic_match": 0.30,
    "ai_detection": 0.25,
}


def compute_validity_score(ocr_confidence, forensics_score, semantic_score,
                            ai_human_score, weights=None):
    """
    All inputs are 0-100. Returns (final_score, breakdown dict).
    """
    w = weights or DEFAULT_WEIGHTS

    final = (
        ocr_confidence * w["ocr_confidence"]
        + forensics_score * w["forensics"]
        + semantic_score * w["semantic_match"]
        + ai_human_score * w["ai_detection"]
    )
    final = round(min(100, max(0, final)), 1)

    breakdown = {
        "OCR confidence": round(ocr_confidence, 1),
        "Forensic integrity": round(forensics_score, 1),
        "Semantic match": round(semantic_score, 1),
        "Human-authorship likelihood": round(ai_human_score, 1),
    }

    if final >= 75:
        verdict = "Likely authentic"
    elif final >= 50:
        verdict = "Needs manual review"
    else:
        verdict = "High tamper/AI-generation risk"

    return final, breakdown, verdict
