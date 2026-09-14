import io
from email import message_from_bytes
from pypdf import PdfReader
from docx import Document

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract raw text from PDF, DOCX, TXT, or EML files without OCR."""
    ext = filename.split(".")[-1].lower()

    if ext == "pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages_text).strip()

    elif ext == "docx":
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join([p.text for p in doc.paragraphs if p.text]).strip()

    elif ext == "eml":
        msg = message_from_bytes(file_bytes)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body += part.get_payload(decode=True).decode("utf-8", errors="ignore")
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
        return body.strip()

    elif ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore").strip()

    return ""