import boto3
import json
import os
from .config import SUMMARY_BUCKET
from api.services.config import get_aws_session

bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

def summarize_with_claude(transcript_text: str) -> str:
    messages = [
        {
            "role": "user",
            "content": (
                "You are an AI assistant that formats meeting summaries into structured technical documentation.\n"
                "Based on the meeting transcript below, extract:\n"
                "- **Title** of the meeting (e.g., PWC PO Readout)\n"
                "- **Date** of the meeting\n"
                "- **Purpose** of the meeting\n"
                "- **Key Areas** discussed (as bullet points)\n"
                "- **Pain Points**, **Desired Functionality**, **Data Inputs/Outputs**, **Open Questions** (if mentioned)\n"
                "- **Process Flow** steps if any were discussed\n\n"
                "Format the entire response using markdown headings and indentation.\n\n"
                f"{transcript_text}"
            )
        }
    ]

    body = {
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.4,
        "top_p": 1,
        "anthropic_version": "bedrock-2023-05-31"
    }

    response = bedrock_runtime.invoke_model(
        body=json.dumps(body),
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(response["body"].read())
    return response_body.get("content", [{}])[0].get("text", "").strip()

    

def upload_summary_to_s3(summary: str, filename: str, key_prefix: str = "") -> str:
    s3 = get_aws_session().client("s3")
    filename = os.path.basename(filename)  # removes any subfolder path
    full_key = f"{key_prefix}/{filename}" if key_prefix else filename
    s3.put_object(Bucket=SUMMARY_BUCKET, Key=full_key, Body=summary.encode("utf-8"))
    return f"s3://{SUMMARY_BUCKET}/{full_key}"
