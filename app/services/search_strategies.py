import re
from collections import Counter


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\sçğıöşüÇĞİÖŞÜ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize(text: str) -> list[str]:
    normalized = normalize_text(text)
    return [token for token in normalized.split() if token]


def lexical_overlap_score(query: str, document: str) -> float:
    query_tokens = tokenize(query)
    doc_tokens = tokenize(document)

    if not query_tokens or not doc_tokens:
        return 0.0

    query_counter = Counter(query_tokens)
    doc_counter = Counter(doc_tokens)

    overlap = 0
    for token, q_count in query_counter.items():
        overlap += min(q_count, doc_counter.get(token, 0))

    return overlap / max(len(query_tokens), 1)


def distance_to_similarity(distance: float | None) -> float:
    if distance is None:
        return 0.0
    # Mesafe düştükçe benzerlik artsın
    return 1 / (1 + max(distance, 0))


def hybrid_score(
    vector_similarity: float,
    lexical_score: float,
    vector_weight: float,
    lexical_weight: float,
) -> float:
    return (vector_similarity * vector_weight) + (lexical_score * lexical_weight)


def rerank_score(
    question: str,
    document_text: str,
    vector_distance: float | None,
) -> float:
    lexical = lexical_overlap_score(question, document_text)
    semantic = distance_to_similarity(vector_distance)
    # Rerank için lexical ağırlığı biraz artırıyoruz
    return (semantic * 0.55) + (lexical * 0.45)