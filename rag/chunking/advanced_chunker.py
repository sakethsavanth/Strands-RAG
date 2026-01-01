from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
import uuid

class AdvancedChunker:
    def __init__(self, embedder):
        self.recursive = RecursiveCharacterTextSplitter(
            chunk_size=900,
            chunk_overlap=150
        )
        self.fixed = CharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        self.semantic = SemanticChunker(embedder)

    def chunk_document(self, text: str, metadata: dict):
        chunks = []

        # Paragraph chunking
        for para in text.split("\n\n"):
            if len(para) > 200:
                chunks.append(self._wrap(para, "paragraph", metadata))

        # Recursive
        for c in self.recursive.split_text(text):
            chunks.append(self._wrap(c, "recursive", metadata))

        # Fixed
        for c in self.fixed.split_text(text):
            chunks.append(self._wrap(c, "fixed", metadata))

        # Semantic (highest signal)
        for c in self.semantic.split_text(text):
            chunks.append(self._wrap(c, "semantic", metadata))

        return chunks

    def _wrap(self, text, chunk_type, metadata):
        return {
            "id": str(uuid.uuid4()),
            "text": text,
            "chunk_type": chunk_type,
            **metadata
        }
