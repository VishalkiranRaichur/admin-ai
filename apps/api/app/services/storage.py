import io

import boto3
from botocore.client import BaseClient

from app.config import settings


def get_s3_client() -> BaseClient:
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
    )


def upload_file(
    file_bytes: bytes,
    storage_key: str,
    content_type: str,
) -> str:
    client = get_s3_client()

    client.upload_fileobj(
        io.BytesIO(file_bytes),
        settings.s3_bucket,
        storage_key,
        ExtraArgs={"ContentType": content_type},
    )

    return storage_key

def download_file(storage_key: str) -> bytes:
    client = get_s3_client()

    response = client.get_object(
        Bucket=settings.s3_bucket,
        Key=storage_key,
    )

    try:
        return response["Body"].read()
    finally:
        response["Body"].close()