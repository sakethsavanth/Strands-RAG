import os
import pickle
import time
from pypdf import PdfReader
import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from rag.embeddings import TitanEmbeddingModel
from rag.vector_store import FaissVectorStore

DATA_DIR = "data"
INDEX_DIM = 1024
BATCH_SIZE = 20  # Safe for Bedrock


def ingest_files(status_callback=None):
    """
    Ingest all PDFs from data/ directory.
    Can be called from Streamlit or CLI.
    """

    def status(msg):
        if status_callback:
            status_callback(msg)
        else:
            print(msg)

    embedder = TitanEmbeddingModel()
    store = FaissVectorStore(dim=INDEX_DIM)

    texts = []
    metadatas = []

    status("📄 Scanning data folder for PDFs...")

    pdfs = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf")]
    if not pdfs:
        status("⚠️ No PDFs found in data folder.")
        return

    for file in pdfs:
        status(f"📘 Reading {file}")
        path = os.path.join(DATA_DIR, file)

        reader = PdfReader(path)
        full_text = ""

        for page in reader.pages:
            full_text += page.extract_text() or ""

        # --- Chunking ---
        chunks = [
            full_text[i:i + 500]
            for i in range(0, len(full_text), 450)
        ]

        for chunk in chunks:
            texts.append(chunk)
            metadatas.append({
                "text": chunk,
                "source": file
            })

    total = len(texts)
    status(f"✂️ Created {total} chunks")

    # --- Embedding ---
    status("🧠 Starting Titan embeddings...")
    vectors = []

    start_time = time.time()

    for i in range(0, total, BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        batch_vectors = embedder.embed(batch)
        vectors.extend(batch_vectors)

        completed = min(i + BATCH_SIZE, total)
        elapsed = time.time() - start_time

        status(
            f"✔ Embedded {completed}/{total} chunks "
            f"({completed / total:.1%})"
        )

    # --- FAISS Index ---
    status("📦 Updating FAISS index...")
    store.add(vectors, metadatas)
    store.save()

    status("✅ Ingestion complete. Documents ready for querying.")


# CLI support (unchanged behavior)
if __name__ == "__main__":
    ingest_files()
