from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import os
import pickle
# ⚠️ Deprecated: Not used by current Titan-based RAG pipeline
DATA_DIR = "data"
INDEX_FILE = "rag/index.faiss"
STORE_FILE = "rag/store.pkl"

def ingest():
    texts = []
    sources = []

    for file in os.listdir(DATA_DIR):
        if file.endswith(".pdf"):
            reader = PdfReader(os.path.join(DATA_DIR, file))
            full_text = " ".join(page.extract_text() or "" for page in reader.pages)

            chunks = [
                full_text[i:i+500]
                for i in range(0, len(full_text), 450)
            ]

            for chunk in chunks:
                texts.append(chunk)
                sources.append(file)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, INDEX_FILE)

    with open(STORE_FILE, "wb") as f:
        pickle.dump({"texts": texts, "sources": sources}, f)

    print("✅ PDFs ingested and indexed")

if __name__ == "__main__":
    ingest()
