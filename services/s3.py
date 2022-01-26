import boto3
from botocore.exceptions import ClientError
from decouple import config
from fastapi import HTTPException


class S3Service:
    def __init__(self):
        self.key = config("AWS_ACCESS_KEY")
        self.secret = config("AWS_SECRET")
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=self.key,
            aws_secret_access_key=self.secret
        )
        self.bucket = config("AWS_BUCKET")

    def upload(self, path, key, ext):
        try:
            self.s3.upload_file(path, self.bucket, key, ExtraArgs={
                "ACL": "public-read", "ContentType": f"image/{ext}"
            })
            return f"https://{config('AWS_BUCKET')}.s3.{config('AWS_REGION')}.amazonaws.com/{key}"
        except ClientError:
            raise HTTPException(500, "AWS s3 client is not available")
        except Exception:
            raise HTTPException(500, "AWS s3 client is not available")


