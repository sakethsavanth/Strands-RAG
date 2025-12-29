from strands import Agent
from strands.models.bedrock import BedrockModel

model = BedrockModel(model_id="us.amazon.nova-lite-v1:0")

query_understanding_agent = Agent(
    model=model,
    system_prompt="""
You extract intent and key entities from the user query.
Return JSON with fields: intent, keywords.
"""
)
