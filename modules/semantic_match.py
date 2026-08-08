"""
semantic_match.py
Compares extracted document text against a bank of known-authentic reference
patterns for that document type (resume, offer letter, certificate, ID).

Demo implementation: TF-IDF + cosine similarity (scikit-learn) — fully
offline, no model download required, runs in milliseconds.

Production upgrade path: swap TfidfVectorizer for sentence embeddings via
Ollama (nomic-embed-text) or sentence-transformers (all-MiniLM-L6-v2),
stored in a local FAISS index for fast nearest-neighbor lookup at scale.
The scoring interface (0-100 similarity) stays identical either way, so this
module is a drop-in swap point.

Libraries used:
- scikit-learn (TfidfVectorizer, cosine_similarity)
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Lightweight reference templates per document type. In production these
# would be a curated corpus of hundreds of verified real documents per type,
# embedded once and cached locally.
REFERENCE_TEMPLATES = {
    "resume": [
        "professional experience education skills projects certifications "
        "work history employment dates responsibilities achievements references",
        "objective summary technical skills programming languages tools "
        "internship position company duration role contact email phone",
    ],
    "offer_letter": [
        "we are pleased to offer you the position of salary compensation "
        "joining date terms and conditions company name authorized signatory",
        "dear candidate congratulations offer letter designation ctc annual "
        "compensation benefits reporting manager start date acceptance",
    ],
    "certificate": [
        "this is to certify that has successfully completed the course "
        "duration institute grade percentage seal signature authorized",
        "certificate of completion awarded to for successfully finishing "
        "training program date issued registration number",
    ],
    "id_proof": [
        "government of india identity card name date of birth address "
        "photograph signature unique identification number issued",
        "permanent account number date of birth father name signature "
        "photo card number issuing authority",
    ],
}


def semantic_similarity_score(extracted_text: str, doc_type: str = "resume"):
    """
    Returns (score 0-100, closest_template_index).
    Higher score = extracted text semantically resembles verified templates
    of that document type.
    """
    templates = REFERENCE_TEMPLATES.get(doc_type, REFERENCE_TEMPLATES["resume"])
    corpus = templates + [extracted_text]

    if not extracted_text.strip():
        return 0.0, -1

    vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        # Extracted text had no usable vocabulary overlap
        return 20.0, -1

    doc_vector = tfidf_matrix[-1]
    template_vectors = tfidf_matrix[:-1]
    similarities = cosine_similarity(doc_vector, template_vectors)[0]

    best_idx = int(similarities.argmax())
    best_score = float(similarities[best_idx])

    # Scale cosine similarity (0-1, often low for short docs) into a more
    # usable 0-100 confidence band
    scaled_score = round(min(100, best_score * 140 + 15), 1)
    return scaled_score, best_idx
