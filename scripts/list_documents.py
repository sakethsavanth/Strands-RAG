import sys
import os

# Add project root to PYTHONPATH
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

import boto3
from config.aws import AWS_REGION

BUCKET_NAME = "strands-rag-docs-sk"
PREFIX = "documents/pdfs/"

s3 = boto3.client("s3", region_name=AWS_REGION)

response = s3.list_objects_v2(
    Bucket=BUCKET_NAME,
    Prefix=PREFIX
)

print(f"Objects under s3://{BUCKET_NAME}/{PREFIX}")
for obj in response.get("Contents", []):
    print("-", obj["Key"])
