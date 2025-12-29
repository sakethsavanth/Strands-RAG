def compute_citation_confidence(chunks):
    """
    Returns per-source confidence score (0–100)
    """
    source_scores = {}

    for c in chunks:
        source = c["source"]
        score = c.get("score", 0.5)

        if source not in source_scores:
            source_scores[source] = []

        source_scores[source].append(score)

    confidence = {}
    for src, scores in source_scores.items():
        confidence[src] = round(
            (sum(scores) / len(scores)) * 100, 2
        )

    return confidence
