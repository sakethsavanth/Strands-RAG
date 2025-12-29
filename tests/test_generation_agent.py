import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from agents.generation_agent import generate_answer

fake_context = [
    {
        "source": "bcbs239.pdf",
        "text": "BCBS 239 establishes principles for effective risk data aggregation and reporting."
    }
]

answer = generate_answer(
    "What is BCBS 239 about?",
    fake_context
)

print(answer)
