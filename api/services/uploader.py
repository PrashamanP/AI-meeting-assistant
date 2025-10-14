from api.services.config import get_aws_session
from api.services.docx_parser import convert_docx_to_clean_text
from .config import UPLOAD_BUCKET, AWS_REGION
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

session = get_aws_session()
s3_client = session.client("s3")

def upload_file_to_s3(file, filename: str, content_type: str) -> str:
    try:
        s3_client.upload_fileobj(
            file,
            UPLOAD_BUCKET,
            filename,
            ExtraArgs={"ContentType": content_type}
        )
        s3_uri = f"s3://{UPLOAD_BUCKET}/{filename}"
        print(f"[DEBUG] Uploaded to S3: {s3_uri}")
        return s3_uri
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        return False

def upload_docx_transcript_and_return_text(file_obj, kb_id: str, file_key: str) -> str:
    from api.services.kb_query import KB_CONFIG
    conf = KB_CONFIG[kb_id]
    transcripts_bucket = conf["buckets"]["transcripts"]
    prefix = conf["prefix"]

    # Read text and reset stream
    text = convert_docx_to_clean_text(file_obj)
    file_obj.seek(0)

    s3_key = f"{prefix}/{file_key}.txt"
    s3_client.put_object(
        Bucket=transcripts_bucket,
        Key=s3_key,
        Body=text.encode("utf-8"),
        ContentType="text/plain"
    )
    print(f"[DEBUG] Uploaded DOCX as transcript: s3://{transcripts_bucket}/{s3_key}")
    return text

def upload_txt_transcript_and_return_text(file_obj, kb_id: str, file_key: str) -> str:
    from api.services.kb_query import KB_CONFIG
    conf = KB_CONFIG[kb_id]
    transcripts_bucket = conf["buckets"]["transcripts"]
    prefix = conf["prefix"]

    file_obj.seek(0)
    text = file_obj.read().decode("utf-8")
    s3_key = f"{prefix}/{file_key}.txt"

    s3_client.put_object(
        Bucket=transcripts_bucket,
        Key=s3_key,
        Body=text.encode("utf-8"),
        ContentType="text/plain"
    )
    print(f"[DEBUG] Uploaded TXT as transcript: s3://{transcripts_bucket}/{s3_key}")
    return text
