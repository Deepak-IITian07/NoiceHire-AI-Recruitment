
import hashlib
import logging
import os
import shutil
import zipfile

from io import BytesIO
from pathlib import Path

import pymupdf
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

from PIL import Image
from docx import Document

from rest_framework.exceptions import ValidationError


logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 5 * 1024 * 1024

def validate_file(uploaded_file):

    filename = uploaded_file.name
    extension = Path(filename).suffix.lower()

    if extension not in [".pdf", ".docx"]:
        raise ValidationError("Only PDF and DOCX files are supported.")

    content = uploaded_file.read()
    uploaded_file.seek(0)

    if not content:
        raise ValidationError("Uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE:
        raise ValidationError("File size exceeds 5 MB.")

    # Validate actual PDF format
    if extension == ".pdf":

        if not content.startswith(b"%PDF-"):
            raise ValidationError("Invalid PDF file.")

    # Validate actual DOCX format
    elif extension == ".docx":

        try:
            with zipfile.ZipFile(BytesIO(content)) as archive:

                required = [
                    "[Content_Types].xml",
                    "word/document.xml"
                ]

                if not all(
                    item in archive.namelist()
                    for item in required
                ):
                    raise ValidationError("Invalid DOCX file.")

        except zipfile.BadZipFile:
            raise ValidationError("Corrupted DOCX file.")

    file_hash = hashlib.sha256(content).hexdigest()

    return content, file_hash, extension


def extract_pdf_text(content):

    doc = pymupdf.open(
        stream=content,
        filetype="pdf"
    )

    pages = []
    ocr_used = False
    ocr_unavailable = False

    try:

        if doc.needs_pass:
            raise ValueError("Password-protected PDF.")

        for index, page in enumerate(doc):

            # First attempt: normal text extraction
            text = page.get_text("text").strip()

            # Detect pages with very little selectable text
            if len(text) < 30:

                logger.info(
                    "Possible scanned PDF page detected: %s",
                    index + 1
                )

                # Second attempt: OCR
                try:

                    if not shutil.which("tesseract") and not os.path.exists(
                        getattr(
                            pytesseract.pytesseract,
                            "tesseract_cmd",
                            ""
                        )
                    ):
                        raise pytesseract.TesseractNotFoundError()

                    pix = page.get_pixmap(
                        dpi=250,
                        alpha=False
                    )

                    image = Image.open(
                        BytesIO(pix.tobytes("png"))
                    )

                    ocr_text = pytesseract.image_to_string(
                        image,
                        lang="eng"
                    ).strip()

                    if ocr_text:
                        text = ocr_text

                    ocr_used = True

                except pytesseract.TesseractNotFoundError:

                    logger.warning(
                        "Tesseract unavailable for page %s",
                        index + 1
                    )

                    ocr_unavailable = True

                except Exception:

                    logger.exception(
                        "OCR failed on PDF page %s",
                        index + 1
                    )

            pages.append({
                "page_number": index + 1,
                "text": text
            })

    finally:
        doc.close()

    full_text = "\n".join(
        page["text"] for page in pages
    )

    if full_text.strip():
        status = "success"
    elif ocr_unavailable:
        status = "ocr_unavailable"
    else:
        status = "empty_text"

    return {
        "text": full_text,
        "pages": pages,
        "page_count": len(pages),
        "status": status,
        "ocr_used": ocr_used,
        "error": ""
    }


def extract_docx_text(content):

    document = Document(BytesIO(content))

    paragraphs = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    # Extract table content
    for table in document.tables:

        for row in table.rows:

            row_text = [
                cell.text.strip()
                for cell in row.cells
                if cell.text.strip()
            ]

            if row_text:
                paragraphs.append(" | ".join(row_text))

    # Extract headers and footers
    for section in document.sections:

        for paragraph in section.header.paragraphs:
            if paragraph.text.strip():
                paragraphs.append(paragraph.text.strip())

        for paragraph in section.footer.paragraphs:
            if paragraph.text.strip():
                paragraphs.append(paragraph.text.strip())

    full_text = "\n".join(paragraphs)

    return {
        "text": full_text,
        "pages": [],
        "page_count": None,
        "status": "success" if full_text.strip() else "empty_text",
        "ocr_used": False,
        "error": ""
    }


def extract_document(content, extension):

    try:

        if extension == ".pdf":
            return extract_pdf_text(content)

        if extension == ".docx":
            return extract_docx_text(content)

        raise ValueError("Unsupported document format.")

    except Exception as error:

        logger.exception("Document extraction failed")

        return {
            "text": "",
            "pages": [],
            "page_count": None,
            "status": "failed",
            "ocr_used": False,
            "error": str(error)
        }
