# config/aws.py

import os
import boto3
from dotenv import load_dotenv

load_dotenv()

# Region must exist at module level for imports
AWS_REGION = os.getenv("AWS_REGION", "ca-central-1")


def get_bedrock_runtime():
    """
    Returns a Bedrock Runtime client
    """
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=AWS_REGION
    )
