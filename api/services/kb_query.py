import boto3
import os
import json
import tempfile
import shutil
from .rag_engine import answer_question_rag
from langchain.vectorstores import FAISS
from langchain.embeddings import BedrockEmbeddings
from langchain_community.chat_models import BedrockChat
from langchain.chains import RetrievalQA
from api.services.config import get_aws_session


s3 = get_aws_session().client("s3")


# Load KB config
kb_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "kb_config.json")
)

with open(kb_config_path) as f:
    KB_CONFIG = json.load(f)

def download_faiss_index(bucket: str, key_prefix: str, local_dir: str):
    for suffix in ["faiss", "pkl"]:
        # FIXED: match actual uploaded key naming convention with `.index` in filename
        s3_key = f"{key_prefix}.index.{suffix}"
        original_filename = f"{os.path.basename(key_prefix)}.index.{suffix}"
        original_path = os.path.join(local_dir, original_filename)
        target_path = os.path.join(local_dir, f"index.{suffix}")

        print(f"[DEBUG] Downloading from s3://{bucket}/{s3_key} to {original_path}")
        s3.download_file(bucket, s3_key, original_path)

        # Rename to index.faiss / index.pkl as FAISS expects
        shutil.move(original_path, target_path)




def load_kb_vectorstore(kb_id: str, filenames: list[str]):
    conf = KB_CONFIG[kb_id]
    embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1")
    summary_bucket = conf["buckets"]["summaries"]

    merged_store = None
    combined_summary = ""

    for filename in filenames:
        key_prefix = f"{conf['prefix']}/{filename}"

        # Download FAISS index
        with tempfile.TemporaryDirectory() as tmpdir:
            download_faiss_index(conf["buckets"]["embeddings"], key_prefix, tmpdir)
            vs = FAISS.load_local(tmpdir, embeddings, allow_dangerous_deserialization=True)
            merged_store = merged_store.merge_from(vs) if merged_store else vs

        # Download corresponding summary
        summary_key = f"{conf['prefix']}/{filename}.md"
        print(f"[DEBUG] Trying to fetch summary from: s3://{summary_bucket}/{summary_key}")

        try:
            s3_object = s3.get_object(Bucket=summary_bucket, Key=summary_key)
            summary_text = s3_object["Body"].read().decode("utf-8")
            combined_summary += f"\n\n--- Summary for {filename} ---\n{summary_text}"
        except Exception as e:
            print(f"[WARNING] Could not load summary for {filename}: {e}")
            combined_summary += f"\n\n--- Summary for {filename} ---\n(No summary available)"

    return merged_store, combined_summary
