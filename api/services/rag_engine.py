import os
import io
import json
import boto3
import tempfile
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_aws import BedrockEmbeddings
from api.services.config import get_aws_session

# AWS Clients
s3 = get_aws_session().client("s3")

bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

# Embeddings
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", region_name="us-east-1")

# Constants 
VECTOR_S3_BUCKET = "aima-meeting-embeddings"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
CLAUDE_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

PROMPT_TEMPLATE = """
You are a world-class meeting assistant AI. Based on the following meeting summary and transcript context, provide a detailed, insightful answer to the user’s question.

Focus on accuracy, clarity, and completeness. Your response should:
- Directly address the question
- Cite key points from the transcript if relevant
- Provide structured insights, not just summaries
- Be a few paragraphs long and include bullet points or numbered steps where appropriate

If the user is asking for a flowchart, decision tree, diagram, or visual representation, generate the response in valid **Mermaid.js** format inside a code block (```mermaid). Do not explain Mermaid itself—just generate the appropriate diagram using it.

<summary>
{summary}
</summary>

<context>
{context}
</context>

Question: {question}
Answer:
"""

# Chunking 
def chunk_transcript(text: str) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.create_documents([text])

def save_faiss_to_s3(faiss_index: FAISS, key_prefix: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        faiss_index.save_local(tmpdir)
        for file_name in os.listdir(tmpdir):
            local_path = os.path.join(tmpdir, file_name)
            s3_key = f"{key_prefix}.index.{file_name.split('.')[-1]}"  # Match download naming
            s3.upload_file(local_path, VECTOR_S3_BUCKET, s3_key)


def load_faiss_from_s3(key_prefix: str) -> FAISS:
    with tempfile.TemporaryDirectory() as tmpdir:
        for suffix in ["faiss", "pkl"]:
            s3_key = f"{key_prefix}.index.{suffix}"  # ✅ Use .index
            print(f"[DEBUG] Downloading FAISS file from: s3://{VECTOR_S3_BUCKET}/{s3_key}")
            s3.download_file(
                VECTOR_S3_BUCKET,
                s3_key,
                os.path.join(tmpdir, f"index.{suffix}")
            )
        return FAISS.load_local(tmpdir, bedrock_embeddings, allow_dangerous_deserialization=True)


# Embedding 
def embed_transcript_and_upload(docs: List[Document], key_prefix: str):
    vectorstore = FAISS.from_documents(docs, bedrock_embeddings)
    save_faiss_to_s3(vectorstore, key_prefix)

# RAG Answering 
def retrieve_context(key_prefix: str, question: str, k=5):
    vectorstore = load_faiss_from_s3(key_prefix)
    return vectorstore.similarity_search(question, k=k)

def answer_question_rag(summary: str, docs: List[Document], question: str) -> str:
    context_text = "\n\n".join([doc.page_content for doc in docs])
    messages = [
        {
            "role": "user",
            "content": PROMPT_TEMPLATE.format(summary=summary, context=context_text, question=question)
        }
    ]

    body = {
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.5,
        "top_p": 1,
        "anthropic_version": "bedrock-2023-05-31"
    }

    try:
        response = bedrock_runtime.invoke_model(
            body=json.dumps(body),
            modelId=CLAUDE_MODEL_ID,
            contentType="application/json",
            accept="application/json"
        )
        response_body = json.loads(response["body"].read())
        return response_body.get("content", [{}])[0].get("text", "").strip()

    except bedrock_runtime.exceptions.ThrottlingException as e:
        return " Claude API is currently rate-limited. Please wait a few seconds and try again."
    except Exception as e:
        return f" An unexpected error occurred: {e}"
