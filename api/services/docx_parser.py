from docx import Document
import re

def convert_docx_to_clean_text(file_stream) -> str:
    """
    Convert a .docx file stream to cleaned text (ready for summarization/embedding).
    """
    document = Document(file_stream)
    lines = []

    for para in document.paragraphs:
        text = para.text.strip()
        if text:
            # Clean extra whitespace and symbols
            text = re.sub(r"\s+", " ", text)
            lines.append(text)

    return "\n".join(lines)