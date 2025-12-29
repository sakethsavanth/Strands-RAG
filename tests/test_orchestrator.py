import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from agents.orchestrator import answer_query

result = answer_query("Explain BCBS 239 in simple terms.")

print("ANSWER:")
print(result["answer"])
print("\nSOURCES:")
for s in result["sources"]:
    print("-", s)
