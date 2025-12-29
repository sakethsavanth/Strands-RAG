import sys
import os   
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from agents.retrieval_agent import retrieve_documents

query = "What is model risk management?"
results = retrieve_documents(query)

print("Chunks retrieved:", len(results))
for r in results[:2]:
    print(r["source"])
    print(r["text"][:200])
    print("----")
