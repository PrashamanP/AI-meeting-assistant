import boto3
import os
import json
from typing import List
from langchain.embeddings import BedrockEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from api.services.config import get_aws_session 

s3 = get_aws_session().client("s3")

# Load KB config
kb_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "kb_config.json")
)

with open(kb_config_path) as f:
    KB_CONFIG = json.load(f)

def upload_text_to_s3(text: str, bucket: str, key: str):
    s3.put_object(Bucket=bucket, Key=key, Body=text.encode("utf-8"))

def get_kb_paths(kb_id: str, filename: str):
    conf = KB_CONFIG[kb_id]
    prefix = conf["prefix"]
    return {
        "transcript_key": f"{prefix}/{filename}.txt",
        "summary_key": f"{prefix}/{filename}.md",
        "embedding_key": f"{prefix}/{filename}.index"
    }

def build_and_store_embedding(text: str, kb_id: str, filename: str):
    conf = KB_CONFIG[kb_id]
    embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1")
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents([text])

    vectorstore = FAISS.from_documents(docs, embedding=embeddings)

    # Save index locally
    local_dir = f"/tmp/{filename}"
    os.makedirs(local_dir, exist_ok=True)
    vectorstore.save_local(local_dir)


    # Upload to S3
    embedding_bucket = conf["buckets"]["embeddings"]
    embedding_key = f"{conf['prefix']}/{filename}.index"
    for suffix in ["index.faiss", "index.pkl"]:
        s3.upload_file(
            f"{local_dir}/{suffix}",
            embedding_bucket,
            f"{embedding_key}.{suffix.split('.')[-1]}"
        )



def add_file_to_kb(kb_id: str, filename: str, transcript_text: str, summary_text: str):
    conf = KB_CONFIG[kb_id]

    paths = get_kb_paths(kb_id, filename)

    # Upload transcript and summary
    upload_text_to_s3(transcript_text, conf["buckets"]["transcripts"], paths["transcript_key"])
    upload_text_to_s3(summary_text, conf["buckets"]["summaries"], paths["summary_key"])

    # Build and upload embeddings
    build_and_store_embedding(transcript_text + "\n" + summary_text, kb_id, filename)

    # Debug statements
    print(f"[DEBUG] Uploading transcript to {conf['buckets']['transcripts']}, key: {paths['transcript_key']}")
    print(f"[DEBUG] Uploading summary to {conf['buckets']['summaries']}, key: {paths['summary_key']}")
    print(f"[DEBUG] Uploading embeddings to {conf['buckets']['embeddings']}, key: {paths['embedding_key']}")

