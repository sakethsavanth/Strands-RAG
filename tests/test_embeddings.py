import sys
import os

# ✅ Add project root to PYTHONPATH
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from rag.embeddings import TitanEmbeddingModel

embedder = TitanEmbeddingModel(region="us-west-2")

vectors = embedder.embed([
    "Model risk management ensures financial stability.",
    "BCBS 239 focuses on risk data aggregation."
])

print("Vector length:", len(vectors[0]))
print("Sample values:", vectors[0][:5])
