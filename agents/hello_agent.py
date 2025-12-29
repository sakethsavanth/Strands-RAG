import sys
import os

# Add project root to PYTHONPATH
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from strands import Agent
from strands.models.bedrock import BedrockModel
from config.settings import DEFAULT_MODEL_ID
from config.aws import AWS_REGION
import boto3


def create_hello_agent():
    session = boto3.Session(region_name=AWS_REGION)

    model = BedrockModel(
        model_id=DEFAULT_MODEL_ID,
        boto_session=session,
        streaming=False
    )

    agent = Agent(
        model=model,
        system_prompt="You are a helpful assistant."
    )

    return agent


if __name__ == "__main__":
    agent = create_hello_agent()
    response = agent("Explain what RAG is in one sentence.")
    print(response.message["content"][0]["text"])
