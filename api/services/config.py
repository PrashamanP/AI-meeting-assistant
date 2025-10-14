import os
import boto3

# Static Bucket Config 
UPLOAD_BUCKET = os.getenv("MEETING_UPLOADS_BUCKET", "aima-meeting-uploads")
TRANSCRIPT_BUCKET = os.getenv("MEETING_TRANSCRIPTS_BUCKET", "aima-meeting-transcripts")
SUMMARY_BUCKET = os.getenv("MEETING_SUMMARIES_BUCKET", "aima-meeting-summaries")
VECTOR_S3_BUCKET = os.getenv("MEETING_EMBEDDINGS_BUCKET", "aima-meeting-embeddings")
AWS_REGION = "us-east-1"

boto3.setup_default_session(region_name=AWS_REGION)

def get_aws_session():
    # PRODUCTION: On EC2, use STS to assume the sandbox role
    if os.getenv("ENV") == "production":
        return get_sandbox_session()
    
    # DEV/LOCAL: Use DynamoDB-stored credentials
    return get_aws_session_from_dynamodb_user()

def get_sandbox_session():
    sts = boto3.client("sts")
    response = sts.assume_role(
        RoleArn="arn:aws:iam::610495549807:role/CrossAccountSandboxAccess",
        RoleSessionName="sandbox-access-session"
    )

    creds = response["Credentials"]
    return boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name="us-east-1"
    )

def get_aws_session_from_dynamodb_user():
    """
    Fetch permanent AWS credentials for SyncScribe from DynamoDB and return a boto3 session.
    """
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table("aima-aws-credentials")
    response = table.get_item(Key={"id": "default"})
    item = response.get("Item", {})

    access_key = item.get("access_key")
    secret_key = item.get("secret_key")

    if not access_key or not secret_key:
        raise Exception("Missing access_key or secret_key in DynamoDB")

    return boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="us-east-1"
    )
