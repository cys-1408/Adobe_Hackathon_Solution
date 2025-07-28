from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/e5-small-v2")

def get_embedding(text):
    return model.encode(text, normalize_embeddings=True)

def embed_all(texts):
    return model.encode(texts, normalize_embeddings=True)
