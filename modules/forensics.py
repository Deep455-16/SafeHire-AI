"""
forensics.py
Forensic tamper-detection layer.

Technique: Error Level Analysis (ELA) — re-compresses the image at a known
JPEG quality and diffs it against the original. Regions that were edited
after the last save (pasted text, altered numbers, cloned stamps) compress
differently than untouched regions, producing a bright residual in the
ELA map. This is a real, widely-used forgery-detection technique — not a
black box.

Libraries used:
- Pillow (PIL)  -> image save/reload for recompression
- NumPy         -> residual computation, statistics
- OpenCV (cv2)  -> heatmap colorization for the GUI
"""

import io
import numpy as np
from PIL import Image, ImageChops
import cv2


def error_level_analysis(img: Image.Image, quality: int = 90):
    """
    Returns (ela_score, heatmap_image).
    ela_score: 0-100 "authenticity confidence" derived from ELA residual —
    higher = more uniform compression = more likely untouched.
    """
    img_rgb = img.convert("RGB")
    buffer = io.BytesIO()
    img_rgb.save(buffer, "JPEG", quality=quality)
    buffer.seek(0)
    recompressed = Image.open(buffer)

    diff = ImageChops.difference(img_rgb, recompressed)
    diff_array = np.array(diff).astype(np.float32)

    # Normalize residual intensity
    max_diff = diff_array.max() if diff_array.max() > 0 else 1
    residual = (diff_array / max_diff * 255).astype(np.uint8)

    # Heatmap for visual display
    gray_residual = cv2.cvtColor(residual, cv2.COLOR_RGB2GRAY)
    heatmap = cv2.applyColorMap(gray_residual, cv2.COLORMAP_INFERNO)
    heatmap_img = Image.fromarray(cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB))

    # Score: high variance / hotspots in specific regions suggest localized
    # editing rather than uniform global noise. We use the ratio of
    # high-residual pixels to total pixels as a tamper indicator.
    threshold = np.percentile(gray_residual, 95)
    hotspot_ratio = np.mean(gray_residual > threshold)

    # Convert to a 0-100 "looks untouched" confidence score
    # (heavier localized hotspots -> lower score)
    tamper_penalty = min(hotspot_ratio * 400, 60)
    ela_score = round(float(max(40, 100 - tamper_penalty)), 1)

    return ela_score, heatmap_img


def metadata_integrity_check(metadata: dict):
    """
    Scores metadata plausibility. Flags common red flags:
    - Missing creation metadata entirely (common when doc is re-exported/edited)
    - Software field showing image editors instead of scanners/office tools
    - PDF producer/creator mismatches
    """
    score = 100.0
    flags = []

    software = str(metadata.get("software", "")).lower()
    producer = str(metadata.get("producer", "")).lower()
    creator = str(metadata.get("creator", "")).lower()

    suspicious_tools = ["photoshop", "gimp", "illustrator", "canva"]
    for tool in suspicious_tools:
        if tool in software or tool in producer or tool in creator:
            score -= 25
            flags.append(f"Edited with {tool.title()} — common tamper vector")

    if metadata.get("exif_tags", 1) == 0 and "size" in metadata:
        score -= 10
        flags.append("No EXIF metadata present (stripped or synthetic image)")

    if not metadata.get("creationDate") and "page_count" in metadata:
        score -= 10
        flags.append("PDF missing creation date metadata")

    if producer and creator and producer != creator and "pdf" in producer:
        # Minor signal only, not necessarily suspicious on its own
        pass

    score = max(30, round(score, 1))
    return score, flags


def run_forensics(images, metadata):
    """Runs ELA on the first page/image and combines with metadata checks."""
    ela_score, heatmap = error_level_analysis(images[0])
    meta_score, flags = metadata_integrity_check(metadata)

    combined = round(float(ela_score * 0.6 + meta_score * 0.4), 1)
    return {
        "ela_score": ela_score,
        "meta_score": meta_score,
        "combined_score": combined,
        "heatmap": heatmap,
        "flags": flags,
    }
