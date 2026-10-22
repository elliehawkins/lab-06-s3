#!/usr/bin/env python3
"""Upload a local file to S3."""
import logging
import os
import sys
import boto3
import json
import requests
import time
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)
#set a universal s3
s3 = boto3.client("s3", region_name="us-east-1")

def parse_args():
    if len(sys.argv) < 4:
        logging.error("Usage error")
        sys.exit(1)
    list_file = sys.argv[1]
    index_path = sys.argv[2]
    bucket = sys.argv[3]
    return(list_file, index_path, bucket)

def download_books(list_file, dest_dir):
    os.makedirs(dest_dir, exist_ok = True)
    file_paths = []
    try:
        with open(list_file, "r", encoding = "utf-8") as f:
            for line in f:
                urls = line.strip()
        for url in urls:
            filename = url.rstrip("/").split("/")[-1]
            path = os.path.join(dest_dir, filename)
            if os.path.exists(path):
                log.info(f"File exists arleady")
                file_paths.append(path)
                continue
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            log.error(f"Error downloading {url}: {e}")
        time.sleep(1)
        return file_paths

def create_bucket(bucket):
    try:
        s3.head_bucket(Bucket = bucket)
        log.info(f"Bucket already exists: {bucket}")
        return True
    except ClientError:
        pass
    try:
        s3.create_bucket(Bucket=bucket)
        log.info(f"Created bucket: {bucket}")
        return True
    except ClientError as e:
        log.error(f"Error creating bucket {bucket}: {e}")
        return False

def make_public(bucket):
    s3.put_public_access_block(
    Bucket=bucket,
    PublicAccessBlockConfiguration={
        "BlockPublicAcls": False,
        "IgnorePublicAcls": False,
        "BlockPublicPolicy": False,
        "RestrictPublicBuckets": False,
    },
)
    policy = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3::{bucket}/*"
    }
  ]
}
    s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps(policy))

def upload_files(bucket, file_paths):
    uploaded_files = 0
    for file_path in file_paths:
        key = os.path.basename(file_path)
        try:
            with open(file_paths, "rb") as f:
                s3.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=f,
                    ContentType="text/plain; charset=utf-8",
                )
            log.info(f"Uploaded {file_path} to s3://{bucket}/{key}")
            uploaded = uploaded + 1
        except FileNotFoundError:
            log.error(f"Local file not found: {file_path}")
        except ClientError as e:
            log.error(f"Error uploading object: {e}")
    return uploaded_files  
    
def upload_index(bucket, index_path):
    try:
        with open(index_path, "rb") as f:
            s3.put_object(
                Bucket=bucket,
                Key=index.html,
                Body=f,
                ContentType="text/html",
            )

def main():
    list_file, index_path, bucket = parse_args()
    if not create_bucket(bucket):
        sys.exit(1)
    if not make_public(bucket):
        sys.exit(1)
    file_paths = download_books(list_file, "books")
    uploaded = upload_files(bucket, file_paths)
    log.info(f"Successfully uploaded {uploaded} books.")
    if not upload_index(bucket, index_path):
        sys.exit(1)
    log.info("Finished staging books and index page.")

if __name__ == "__main__":
    main()