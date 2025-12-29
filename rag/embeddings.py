import boto3
import json
import sys
import os   
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from config.settings import AWS_REGION

class TitanEmbeddingModel:
    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=AWS_REGION
        )
        self.model_id = "amazon.titan-embed-text-v2:0"

    def embed(self, texts):
        vectors = []

        for text in texts:
            body = json.dumps({"inputText": text})
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body
            )
            result = json.loads(response["body"].read())
            vectors.append(result["embedding"])

        return vectors
