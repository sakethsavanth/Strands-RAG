import faiss
import numpy as np
from config.settings import VECTOR_DIM

class FaissStore:
    def __init__(self):
        self.index = faiss.IndexFlatL2(VECTOR_DIM)
        self.docs = []
        self.meta = []

    def add(self, embeddings, docs, metadata):
        self.index.add(np.array(embeddings).astype("float32"))
        self.docs.extend(docs)
        self.meta.extend(metadata)

    def search(self, q_emb, k):
        _, idx = self.index.search(
            np.array([q_emb]).astype("float32"), k
        )
        results = []
        for i in idx[0]:
            results.append({
                "text": self.docs[i],
                "meta": self.meta[i]
            })
        return results

faiss_store = FaissStore()
