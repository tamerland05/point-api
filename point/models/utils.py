from point.config import settings


def hash_to_link(file_hash: str) -> str:
    return f"{settings.aws_endpoint_url}{settings.aws_bucket_name}/{file_hash}"
