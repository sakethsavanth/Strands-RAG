def compute_confidence(chunks, validation):
    score = 0.4

    if chunks:
        score += min(len(chunks) * 0.1, 0.3)

    if validation["approved"]:
        score += 0.2

    return round(min(score, 0.95), 2)
