from sklearn.metrics.pairwise import cosine_similarity

def rank_sections(section_embs, meta, query_emb):
    similarities = cosine_similarity(section_embs, query_emb.reshape(1, -1)).flatten()
    ranked = sorted(zip(similarities, meta), key=lambda x: -x[0])
    return [
        {
            "document": s["document"],
            "page_number": s["page_number"],
            "section_title": s["text"].strip().rstrip('.'),
            "body": s["body"].strip(),
            "importance_rank": i + 1
        }
        for i, (sim, s) in enumerate(ranked[:10])
    ]
