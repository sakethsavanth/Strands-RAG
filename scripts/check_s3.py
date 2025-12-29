import sys
import os

# Add project root to PYTHONPATH
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

import boto3
import os as _os
from config.aws import AWS_REGION

print("=== AWS DIAGNOSTICS ===")
print("AWS_REGION:", AWS_REGION)
print("AWS_ACCESS_KEY_ID:", _os.getenv("AWS_ACCESS_KEY_ID"))
print("======================")

session = boto3.Session(region_name=AWS_REGION)

sts = session.client("sts")
identity = sts.get_caller_identity()

print("\nAuthenticated as:")
print("Account ID:", identity["Account"])
print("ARN:", identity["Arn"])

s3 = session.client("s3")

response = s3.list_buckets()
buckets = response.get("Buckets", [])

print("\nS3 Buckets visible to this account:")
if not buckets:
    print("⚠️  No buckets returned")
else:
    for b in buckets:
        print("-", b["Name"])
