from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate
from .services.uploader import upload_file_to_s3, upload_docx_transcript_and_return_text, upload_txt_transcript_and_return_text
from .services.transcriber import transcribe_amazon
from .services.summarizer import summarize_with_claude
from .services.rag_engine import chunk_transcript, embed_transcript_and_upload, retrieve_context, answer_question_rag
from .services.utils import get_file_type
from .services.kb_query import load_kb_vectorstore
from .services.kb_builder import add_file_to_kb
from api.services.config import get_aws_session
from api.services.kb_query import KB_CONFIG
import re
import logging
from io import BytesIO


logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(["POST"])
def api_login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)

    if user:
        return Response({"success": True, "username": user.username})
    else:
        return Response({"success": False}, status=401)


@api_view(["POST"])
def upload_file(request):
    file = request.FILES.get("file")
    kb_id = request.data.get("kb_id")

    if not file:
        return Response({"error": "No file uploaded"}, status=400)

    try:
        safe_filename = re.sub(r"[^a-zA-Z0-9._-]", "-", file.name)
        file_type = get_file_type(file.name)
        file_key = safe_filename.rsplit(".", 1)[0]
        s3_prefix = kb_id if kb_id else "single-uploads"
        s3_filename = f"{s3_prefix}/{safe_filename}"
        

        # Read file into memory
        file_bytes = file.read()
        file.seek(0)  # reset for S3 upload

        # Upload original file to S3
        s3_uri = upload_file_to_s3(file, s3_filename, file.content_type)
        if not s3_uri:
            return Response({"error": "Failed to upload to S3"}, status=500)

        # Handle different types
        if file_type == "video":
            transcript_text = transcribe_amazon(
                s3_uri,
                output_bucket="aima-meeting-transcripts",
                key_prefix=file_key,
            )
            
        elif file_type == "docx":
            if kb_id:
                transcript_text = upload_docx_transcript_and_return_text(BytesIO(file_bytes), kb_id, file_key)
            else:
                from api.services.docx_parser import convert_docx_to_clean_text
                transcript_text = convert_docx_to_clean_text(BytesIO(file_bytes))
                from api.services.config import get_aws_session
                s3 = get_aws_session().client("s3")
                s3.put_object(
                    Bucket="aima-meeting-transcripts",
                    Key=f"{s3_prefix}/{file_key}.txt",
                    Body=transcript_text.encode("utf-8"),
                    ContentType="text/plain"
                )
        elif file_type == "text":
            transcript_text = file_bytes.decode("utf-8")
            from api.services.config import get_aws_session
            s3 = get_aws_session().client("s3")
            s3.put_object(
                Bucket="aima-meeting-transcripts",
                Key=f"{s3_prefix}/{file_key}.txt",
                Body=transcript_text.encode("utf-8"),
                ContentType="text/plain"
            )
        else:
            return Response({"error": f"Unsupported file type: {file_type}"}, status=400)

        if not transcript_text:
            return Response({"error": "Transcript extraction failed."}, status=500)

        summary = summarize_with_claude(transcript_text)
        docs = chunk_transcript(transcript_text)

        if kb_id:
            add_file_to_kb(kb_id, file_key, transcript_text, summary)
        else:
            embed_transcript_and_upload(docs, key_prefix=f"single-uploads/{file_key}")

        return Response({"summary": summary}, status=200)

    except Exception as e:
        logger.exception("Upload failed.")
        return Response({"error": f"Unexpected error: {str(e)}"}, status=500)



@api_view(["POST"])
def ask_question(request):
    question = request.data.get("question")
    kb_id = request.data.get("kb_id")
    files = request.data.get("files", [])
    summary_text = request.data.get("summary")

    if kb_id and files:
        vectorstore, summary = load_kb_vectorstore(kb_id, files)
        context_docs = vectorstore.similarity_search(question)
        answer = answer_question_rag(summary, context_docs, question)
        return Response({"answer": answer})

    if summary_text:
        context_docs = retrieve_context(request.data.get("file_key"), question)
        answer = answer_question_rag(summary_text, context_docs, question)
        return Response({"answer": answer})

    return Response({"error": "Missing parameters"}, status=400)


@api_view(["GET"])
def list_kb_files(request, kb_id):
    if not kb_id or kb_id not in KB_CONFIG:
        return Response({"error": "Invalid KB ID"}, status=400)

    session = get_aws_session()
    s3 = session.client("s3")

    prefix = f"{KB_CONFIG[kb_id]['prefix']}/"

    # Get .index.faiss files (videos + docx, embedded)
    embedding_bucket = KB_CONFIG[kb_id]['buckets']['embeddings']
    transcript_bucket = KB_CONFIG[kb_id]['buckets']['transcripts']
    all_files = set()

    try:
        embedding_response = s3.list_objects_v2(Bucket=embedding_bucket, Prefix=prefix)
        if 'Contents' in embedding_response:
            for obj in embedding_response['Contents']:
                key = obj['Key']
                if key.endswith(".index.faiss"):
                    filename = key.replace(".index.faiss", "").split("/")[-1]
                    all_files.add(filename)

        transcript_response = s3.list_objects_v2(Bucket=transcript_bucket, Prefix=prefix)
        if 'Contents' in transcript_response:
            for obj in transcript_response['Contents']:
                key = obj['Key']
                if key.endswith(".txt"):
                    filename = key.replace(".txt", "").split("/")[-1]
                    all_files.add(filename)

        return Response({"files": sorted(all_files)})

    except Exception as e:
        return Response({"error": f"S3 error: {str(e)}"}, status=500)


@api_view(["POST"])
def kb_ask_question(request):
    kb_id = request.POST.get("kb_id")
    files = request.POST.getlist("files")
    question = request.POST.get("question")

    if not (kb_id and files and question):
        return JsonResponse({"error": "Missing inputs"}, status=400)

    vectorstore, summary = load_kb_vectorstore(kb_id, files)
    context_docs = vectorstore.similarity_search(question)
    answer = answer_question_rag(summary, context_docs, question)

    if "```mermaid" in answer:
        match = re.search(r"```mermaid\s+(.*?)```", answer, re.DOTALL)
        if match:
            mermaid_code = match.group(1).strip()
            html = f"""
                <div class="chat-message assistant">
                    <pre class="mermaid">{mermaid_code}</pre>
                </div>
                <script>mermaid.init()</script>
            """
            return HttpResponse(html)

    return HttpResponse(f"<div class='chat-message assistant'>{answer}</div>")


@api_view(["GET"])
def list_kb_summaries(request, kb_id):
    session = get_aws_session()
    s3 = session.client("s3")
    if not kb_id or kb_id not in KB_CONFIG:
        return Response({"error": "Invalid KB ID"}, status=400)
 
    prefix = KB_CONFIG[kb_id]["prefix"]
    bucket = KB_CONFIG[kb_id]["buckets"]["summaries"]
 
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        summaries = []
       
        for obj in response.get("Contents", []):
            key = obj["Key"]
            # Check for both .txt and .md files
            if not (key.endswith(".txt") or key.endswith(".md")):
                continue
               
            summary_resp = s3.get_object(Bucket=bucket, Key=key)
            summary_text = summary_resp["Body"].read().decode("utf-8")
           
            # Extract file_id by removing extension
            file_id = key.split("/")[-1]
            if file_id.endswith(".txt"):
                file_id = file_id[:-4]
            elif file_id.endswith(".md"):
                file_id = file_id[:-3]
           
            # Extract recording_id and title
            if "_" in file_id:
                recording_id = file_id.split("_")[0]
                title = " ".join(file_id.split("_")[1:])
            else:
                recording_id = file_id
                title = file_id
           
            summaries.append({
                "recording_id": recording_id,
                "title": title,
                "summary_markdown": summary_text,
                "transcript_url": f"https://{KB_CONFIG[kb_id]['buckets']['transcripts']}.s3.amazonaws.com/{prefix}/{file_id}.txt",
                "video_url": f"https://{KB_CONFIG[kb_id]['buckets']['uploads']}.s3.amazonaws.com/{prefix}/{file_id}.mp4"
            })
       
        return Response(summaries)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


