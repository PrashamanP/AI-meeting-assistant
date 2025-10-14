from pathlib import Path
from io import BytesIO
from docx import Document as DocxDocument

def get_file_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext in ["mp4", "mov", "avi"]:
        return "video"
    elif ext in ["docx"]:
        return "docx"
    elif ext in ["txt", "vtt"]:
        return "text"
    return "unknown"


def extract_text_from_docx(file_buffer: BytesIO) -> str:
    doc = DocxDocument(file_buffer)
    return "\n".join([para.text for para in doc.paragraphs])
