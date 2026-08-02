import email
import io

from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
from docx import Document


async def extract_text_from_upload(file: UploadFile) -> str:
    """
    Extracts raw text from an uploaded complaint document. Supports PDF, DOCX, TXT, EML.
    Note: this is intentionally simple text extraction, not production-grade OCR —
    matches the assignment's 'production-grade OCR is not required' scope.
    """
    contents = await file.read()
    filename = (file.filename or "").lower()

    if filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(contents))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if filename.endswith(".docx"):
        doc = Document(io.BytesIO(contents))
        return "\n".join(p.text for p in doc.paragraphs)

    if filename.endswith(".eml"):
        msg = email.message_from_bytes(contents)
        if msg.is_multipart():
            parts = []
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    parts.append(part.get_payload(decode=True).decode(errors="ignore"))
            return "\n".join(parts)
        return msg.get_payload(decode=True).decode(errors="ignore")

    if filename.endswith(".txt"):
        return contents.decode(errors="ignore")

    raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, DOCX, TXT, or EML.")
