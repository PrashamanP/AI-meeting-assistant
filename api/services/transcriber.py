import boto3
import time
import uuid
import json
import logging
import re
from .summarizer import summarize_with_claude, upload_summary_to_s3
from api.services.config import get_aws_session

from .config import SUMMARY_BUCKET
 
boto3.set_stream_logger('boto3.resources', logging.INFO)

def sanitize_job_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]", "-", name)
 
def transcribe_amazon(audio_s3_uri, output_bucket, output_key=None, key_prefix="", media_format="mp4", language_code="en-US"):
    transcribe = boto3.client("transcribe")
    s3 = get_aws_session().client("s3")

    if output_key is None:
        job_name = f"transcription-job-{uuid.uuid4()}"
    else:
        base_name = sanitize_job_name(output_key.rsplit(".", 1)[0])
        job_name = f"{base_name}-{uuid.uuid4().hex[:8]}"

    result_key = f"{job_name}.json"

    print(f"Starting transcription job: {job_name}")

    try:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": audio_s3_uri},
            MediaFormat=media_format,
            LanguageCode=language_code,
            OutputBucketName=output_bucket
        )
    except Exception as e:
        print(f"Failed to start transcription job: {e}")
        raise

    max_wait_time = 600  # seconds (10 minutes max)
    poll_interval = 5    # seconds
    max_attempts = max_wait_time // poll_interval

    for attempt in range(max_attempts):
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        job_status = status["TranscriptionJob"]["TranscriptionJobStatus"]
        print(f"[Attempt {attempt+1}] Transcription job status: {job_status}")

        if job_status == "COMPLETED":
            break
        elif job_status == "FAILED":
            raise Exception("Transcription job failed.")

        time.sleep(poll_interval)
    else:
        # Loop finished without breaking (i.e., timeout)
        raise TimeoutError(f"Transcription job timed out after {max_wait_time} seconds.")


    if job_status == "FAILED":
        raise Exception("Transcription job failed.")

    print("Transcription job completed. Fetching transcript from S3...")

    try:
        obj = s3.get_object(Bucket=output_bucket, Key= result_key)
        transcript_json = json.load(obj["Body"])
        transcript_text = transcript_json["results"]["transcripts"][0]["transcript"]
    except Exception as e:
        print(f"Error reading transcript from S3: {e}")
        raise

    print("Generating summary...")

    # DELETE raw .json to avoid clutter
    try:
        s3.delete_object(Bucket=output_bucket, Key=result_key)
        print(f"[CLEANUP] Deleted raw transcript JSON: {result_key}")
    except Exception as e:
        print(f"[WARNING] Could not delete raw JSON: {e}")

    return transcript_text # Or return both transcript_text, summary_s3_uri