import os
from pathlib import Path
from ..core.config import settings

def save_pdf(invoice_number: str, content: bytes) -> str:
    if settings.storage_backend == "s3":
        import boto3
        key = f"invoices/{invoice_number}.pdf"
        boto3.client("s3", region_name=settings.s3_region).put_object(Bucket=settings.s3_bucket, Key=key, Body=content, ContentType="application/pdf")
        return f"s3://{settings.s3_bucket}/{key}"
    base = Path(settings.local_storage_path) / "pdfs"
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"{invoice_number}.pdf"
    path.write_bytes(content)
    return str(path)
