# ✅ Add project root to PYTHONPATH
import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from rag.vector_store import FaissVectorStore

store = FaissVectorStore(dim=1024)
store.load()

dummy_vector = [[0.0] * 1024]
results = store.search(dummy_vector, k=3)

print("Retrieved entries:", len(results))
print("Sample metadata:", results[0])
