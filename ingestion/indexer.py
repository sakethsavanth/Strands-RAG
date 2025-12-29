from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import os
import pickle

DATA_DIR = "data/pdfs"
INDEX_PATH = "rag/faiss.index"
META_PATH = "rag/metadata.pkl"

def ingest_pdfs():
    texts = []
    metadata = []

    for file in os.listdir(DATA_DIR):
        if file.endswith(".pdf"):
            reader = PdfReader(os.path.join(DATA_DIR, file))
            full_text = " ".join(page.extract_text() or "" for page in reader.pages)

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            chunks = splitter.split_text(full_text)

            for chunk in chunks:
                texts.append(chunk)
                metadata.append({"source": file})

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "wb") as f:
        pickle.dump({"texts": texts, "metadata": metadata}, f)

    print("✅ PDFs ingested & indexed")

if __name__ == "__main__":
    ingest_pdfs()
