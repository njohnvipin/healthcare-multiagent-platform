from pathlib import Path

import fitz
import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


SUPPORTED_IMAGE_TYPES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
    ".bmp",
}


def extract_text_from_image(file_path: str) -> str:
    """Extract text from an image using Tesseract OCR."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with Image.open(path) as image:
        image = image.convert("RGB")

        text = pytesseract.image_to_string(
            image,
            lang="eng",
            config="--oem 3 --psm 6",
        )

    return text.strip()


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a digital or scanned PDF.

    Digital PDF:
        Uses native PDF text extraction.

    Scanned PDF:
        Converts pages to images and runs OCR.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    extracted_pages = []

    with fitz.open(path) as document:
        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text("text").strip()

            if not page_text:
                pixmap = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2),
                    alpha=False,
                )

                image = Image.frombytes(
                    "RGB",
                    [pixmap.width, pixmap.height],
                    pixmap.samples,
                )

                page_text = pytesseract.image_to_string(
                    image,
                    lang="eng",
                    config="--oem 3 --psm 6",
                ).strip()

            extracted_pages.append(
                f"--- Page {page_number} ---\n{page_text}"
            )

    return "\n\n".join(extracted_pages).strip()


def extract_text(file_path: str) -> str:
    """Select the correct extraction method by extension."""
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension in SUPPORTED_IMAGE_TYPES:
        return extract_text_from_image(file_path)

    if extension == ".txt":
        return path.read_text(
            encoding="utf-8",
            errors="ignore",
        ).strip()

    raise ValueError(f"Unsupported document type: {extension}")