from strands import tool
from rag.embeddings import TitanEmbeddingModel
from rag.vector_store import FaissVectorStore
from config.settings import MCP_URL

embedder = TitanEmbeddingModel()
store = FaissVectorStore(dim=1024)
store.load()

@tool
def retrieve_documents(query: str) -> list:
    """
    Retrieve relevant document chunks for a query.
    MCP is optional and disabled if MCP_URL is None.
    """
    query_vec = embedder.embed([query])
    results = store.search(query_vec)

    # MCP hook (optional, future-ready)
    if MCP_URL:
        pass  # MCP enrichment will be added later

    return results
