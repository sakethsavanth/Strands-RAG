import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from rag.embeddings import TitanEmbeddingModel
from rag.vector_store import FaissVectorStore

class VectorRetriever:
    def __init__(self):
        self.embedder = TitanEmbeddingModel()
        self.store = FaissVectorStore(dim=1024)
        self.store.load()

    def retrieve(self, query, k=10):
        query_vec = self.embedder.embed([query])
        return self.store.search(query_vec, k=k)
