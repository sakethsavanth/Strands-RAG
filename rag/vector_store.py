import faiss
import pickle
import numpy as np

class FaissVectorStore:
    def __init__(self, dim: int, index_path="rag/index.faiss", meta_path="rag/meta.pkl"):
        self.index_path = index_path
        self.meta_path = meta_path
        self.index = faiss.IndexFlatL2(dim)
        self.metadata = []

    def add(self, vectors, metadatas):
        # ✅ Convert list → numpy array (float32)
        vectors_np = np.array(vectors).astype("float32")

        self.index.add(vectors_np)
        self.metadata.extend(metadatas)

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self):
        self.index = faiss.read_index(self.index_path)
        with open(self.meta_path, "rb") as f:
            self.metadata = pickle.load(f)

    def search(self, vector, k=5):
        vector_np = np.array(vector).astype("float32")
        scores, ids = self.index.search(vector_np, k)
        return [self.metadata[i] for i in ids[0]]
