import faiss
import pickle
import numpy as np
import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from rag.embeddings import TitanEmbeddingModel

INDEX_FILE = "rag/index.faiss"
META_FILE = "rag/meta.pkl"

class VectorRetriever:
    def __init__(self):
        self.embedder = TitanEmbeddingModel()
        self.index = faiss.read_index(INDEX_FILE)

        with open(META_FILE, "rb") as f:
            self.metadata = pickle.load(f)

    def retrieve(self, query: str, k: int = 4):
        # 1️⃣ Embed query
        query_vector = self.embedder.embed([query])

        # 2️⃣ Convert to numpy float32 with correct shape
        query_vector = np.array(query_vector).astype("float32")

        # 3️⃣ FAISS search
        _, indices = self.index.search(query_vector, k)

        results = []
        for idx in indices[0]:
            results.append(self.metadata[idx])

        return results
