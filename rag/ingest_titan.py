import os
import pickle
import sys
import time
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from pypdf import PdfReader
from rag.embeddings import TitanEmbeddingModel
from rag.vector_store import FaissVectorStore

# ✅ Add project root to PYTHONPATH


DATA_DIR = "data"
INDEX_DIM = 1024
BATCH_SIZE = 20  # Safe for Bedrock

def ingest():
    embedder = TitanEmbeddingModel(region="us-west-2")
    store = FaissVectorStore(dim=INDEX_DIM)

    texts = []
    metadatas = []

    print("📄 Reading PDFs...")

    for file in os.listdir(DATA_DIR):
        if not file.lower().endswith(".pdf"):
            continue

        print(f"  → Processing {file}")
        path = os.path.join(DATA_DIR, file)
        reader = PdfReader(path)

        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() or ""

        chunks = [
            full_text[i:i+500]
            for i in range(0, len(full_text), 450)
        ]

        for chunk in chunks:
            texts.append(chunk)
            metadatas.append({
                "text": chunk,
                "source": file
            })

    total = len(texts)
    print(f"\n🧠 Total chunks to embed: {total}")
    print("🚀 Starting Titan embedding...\n")

    vectors = []

    start_time = time.time()

    for i in range(0, total, BATCH_SIZE):
        batch = texts[i:i+BATCH_SIZE]

        batch_vectors = embedder.embed(batch)
        vectors.extend(batch_vectors)

        completed = min(i + BATCH_SIZE, total)
        elapsed = time.time() - start_time
        rate = completed / elapsed if elapsed > 0 else 0
        remaining = (total - completed) / rate if rate > 0 else 0

        print(
            f"✔ Embedded {completed}/{total} chunks "
            f"({completed/total:.1%}) | "
            f"Elapsed: {elapsed:.1f}s | "
            f"ETA: {remaining/60:.1f} min"
        )

    store.add(vectors, metadatas)
    store.save()

    print("\n✅ Titan ingestion complete")
    print("📁 Files created:")
    print(" - rag/index.faiss")
    print(" - rag/meta.pkl")

if __name__ == "__main__":
    ingest()