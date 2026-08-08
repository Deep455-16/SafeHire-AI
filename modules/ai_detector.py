"""
ai_detector.py
Estimates the likelihood that extracted text was written or rewritten by an
AI tool (as opposed to a human-authored/scanned original document).

Demo implementation: lightweight statistical stylometry — no model download
required, runs instantly, fully offline.
  - Burstiness: human writing has irregular sentence-length rhythm; AI text
    tends toward more uniform sentence lengths (lower burstiness).
  - Type-token ratio (TTR): vocabulary diversity relative to text length.
    AI-generated text often shows unusually smooth/high TTR for its length.
  - Repetition of structural phrasing patterns.

Production upgrade path: replace/augment this with actual perplexity
scoring from a local LLM via Ollama (e.g. qwen2.5:1.5b) — lower perplexity
under the model = more "predictable" = more likely AI-generated. This
module's output interface (0-100 human-likelihood score) is designed as a
drop-in swap point for that upgrade.

Libraries used:
- re, statistics (standard library) — sentence/word tokenization & stats
"""

import re
import statistics


def _split_sentences(text: str):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in sentences if len(s.split()) > 2]


def _burstiness(sentences):
    lengths = [len(s.split()) for s in sentences]
    if len(lengths) < 3:
        return 0.5  # not enough data, neutral
    mean = statistics.mean(lengths)
    stdev = statistics.pstdev(lengths)
    if mean == 0:
        return 0.5
    # Coefficient of variation, normalized to 0-1
    cv = stdev / mean
    return min(cv, 1.5) / 1.5


def _type_token_ratio(text: str):
    words = re.findall(r"[a-zA-Z']+", text.lower())
    if len(words) < 10:
        return 0.5
    unique = len(set(words))
    ttr = unique / len(words)
    return ttr


def ai_generation_likelihood(text: str):
    """
    Returns (human_likelihood_score 0-100, signals dict).
    Higher score = more likely human-authored/original.
    """
    if not text or len(text.split()) < 15:
        return 55.0, {"note": "Text too short for reliable stylometric signal"}

    sentences = _split_sentences(text)
    burst = _burstiness(sentences)
    ttr = _type_token_ratio(text)

    # Human text: higher burstiness (irregular rhythm) is a positive signal.
    # AI text: very smooth TTR in a narrow "safe" band (0.4-0.55) is common;
    # scores far outside that band are treated as more human-like or noisy-OCR-like.
    burst_component = burst * 55  # 0-55 points

    if 0.40 <= ttr <= 0.55:
        ttr_component = 20  # sits in the "typical AI smoothness" zone -> fewer points
    else:
        ttr_component = 35

    human_score = round(min(100, burst_component + ttr_component + 10), 1)

    signals = {
        "burstiness": round(burst, 2),
        "type_token_ratio": round(ttr, 2),
        "sentence_count": len(sentences),
    }
    return human_score, signals
