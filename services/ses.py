import boto3
from decouple import config


class SESService:
    """Simple Email Service"""

    def __init__(self):
        self.key = config("AWS_ACCESS_KEY")
        self.secret = config("AWS_SECRET")
        self.ses = boto3.client(
            "ses",
            aws_access_key_id=self.key,
            aws_secret_access_key=self.secret,
            region_name=config("SES_REGION"),
        )

    def send_email(self, subject, to_address, text_data):
        body = {
            "Text": {
                "Data": text_data,
                "Charset": "UTF-8"
            }
        }
        self.ses.send_email(
            Source="yoursource@email.com",
            Destination={
                "ToAddresses": to_address,
                "CcAddresses": [],
                "BccAddresses": [],
            },
            Message={
                "Subject": {
                    "Data": subject,
                    "Charset": "UTF-8"
                },
                "Body": body
            }
        )

