import fitz
from core.exceptions import PDFExtractionError


def extract_text_from_pdf(pdf_file_content):
    try:
        text = ""

        pdf_document = fitz.open(
            stream=pdf_file_content,
            filetype="pdf"
        )

        for page in pdf_document:
            text += page.get_text()

        if not text.strip():
            raise ValueError("PDF appears to be empty or contains no extractable text.")
        return text

    except ValueError :
        raise

    except Exception as e:
        raise PDFExtractionError(f"PDF Extraction Failed {e}") from e