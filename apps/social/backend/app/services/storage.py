"""Cloudflare R2 storage abstraction using boto3."""

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings

# R2 path conventions:
# brands/{brand_id}/kit/logo_light.{ext}
# brands/{brand_id}/kit/logo_dark.{ext}
# brands/{brand_id}/kit/intro.mp4
# brands/{brand_id}/documents/{doc_id}_{filename}.{ext}
# brands/{brand_id}/media/{media_id}_{filename}.{ext}
# brands/{brand_id}/posts/generated/{post_id}.{ext}
# brands/{brand_id}/posts/thumbnails/{post_id}_thumb.jpg


class R2Storage:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                region_name="auto",
            )
        return self._client

    def upload(self, file_bytes: bytes, path: str, content_type: str) -> str:
        """Upload bytes to R2, return the public URL."""
        self.client.put_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=path,
            Body=file_bytes,
            ContentType=content_type,
        )
        return f"{settings.R2_PUBLIC_URL}/{path}"

    def get_presigned_upload_url(self, path: str, content_type: str, expires: int = 3600) -> str:
        """Return a presigned PUT URL for direct browser upload."""
        return self.client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.R2_BUCKET_NAME,
                "Key": path,
                "ContentType": content_type,
            },
            ExpiresIn=expires,
        )

    def delete(self, path: str) -> bool:
        """Delete an object from R2."""
        try:
            self.client.delete_object(Bucket=settings.R2_BUCKET_NAME, Key=path)
            return True
        except ClientError:
            return False

    def copy(self, source_path: str, dest_path: str) -> str:
        """Copy an object within the same bucket, return new public URL."""
        self.client.copy_object(
            Bucket=settings.R2_BUCKET_NAME,
            CopySource={"Bucket": settings.R2_BUCKET_NAME, "Key": source_path},
            Key=dest_path,
        )
        return f"{settings.R2_PUBLIC_URL}/{dest_path}"

    async def download_and_upload(self, source_url: str, dest_path: str, content_type: str) -> str:
        """Download a file from a URL and upload it to R2 (used for fal.ai → R2).

        fal.ai CDN bazen yavaş cevap veriyor — httpx default 5sn timeout yetersiz
        kalıyor (carousel slide'larda ReadTimeout → tüm post fail). 30sn read
        timeout + transient hata/timeout'larda 2 retry (1sn, 3sn backoff). 4xx
        hataları (kalıcı) retry edilmez, anında fırlatılır.
        """
        import asyncio
        import httpx

        timeout = httpx.Timeout(30.0, connect=10.0)
        backoffs = [0, 1, 3]
        last_exc: Exception | None = None
        for backoff in backoffs:
            if backoff:
                await asyncio.sleep(backoff)
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    resp = await client.get(source_url)
                    resp.raise_for_status()
                return self.upload(resp.content, dest_path, content_type)
            except httpx.TimeoutException as exc:
                last_exc = exc
            except httpx.HTTPStatusError as exc:
                if 500 <= exc.response.status_code < 600:
                    last_exc = exc
                else:
                    raise
        assert last_exc is not None
        raise last_exc


r2 = R2Storage()
