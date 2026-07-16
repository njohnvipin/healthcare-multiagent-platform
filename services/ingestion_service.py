import re
from pathlib import Path

from services.ocr_service import extract_text
from services.vector_store import ingest_folder


UPLOAD_ROOT = Path("data/uploads")
PROCESSED_ROOT = Path("data/processed")

DOMAIN_CONFIG = {
    "policies": {
        "collection": "policy_collection",
        "doc_type": "policy",
    },
    "claims": {
        "collection": "claims_collection",
        "doc_type": "claims",
    },
    "authorizations": {
        "collection": "authorization_collection",
        "doc_type": "authorization",
    },
    "billing": {
        "collection": "billing_collection",
        "doc_type": "billing",
    },
}


def clean_ocr_text(text: str) -> str:
    """Clean common OCR whitespace issues."""
    text = text.replace("\x0c", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def process_uploaded_documents() -> dict:
    """
    Read files from data/uploads, run OCR, and save TXT files
    into matching data/processed folders.
    """
    processed_files = []
    failed_files = []

    for domain in DOMAIN_CONFIG:
        upload_folder = UPLOAD_ROOT / domain
        processed_folder = PROCESSED_ROOT / domain

        upload_folder.mkdir(parents=True, exist_ok=True)
        processed_folder.mkdir(parents=True, exist_ok=True)

        for file_path in upload_folder.iterdir():
            if not file_path.is_file():
                continue

            try:
                extracted_text = extract_text(str(file_path))
                cleaned_text = clean_ocr_text(extracted_text)

                if not cleaned_text:
                    raise ValueError("OCR returned empty text")

                output_path = (
                    processed_folder / f"{file_path.stem}.txt"
                )

                output_path.write_text(
                    cleaned_text,
                    encoding="utf-8",
                )

                processed_files.append({
                    "domain": domain,
                    "source": file_path.name,
                    "output": str(output_path),
                    "characters": len(cleaned_text),
                })

            except Exception as exc:
                failed_files.append({
                    "domain": domain,
                    "source": file_path.name,
                    "error": str(exc),
                })

    return {
        "status": (
            "success"
            if not failed_files
            else "partial_success"
        ),
        "processed_count": len(processed_files),
        "failed_count": len(failed_files),
        "processed_files": processed_files,
        "failed_files": failed_files,
    }


def ingest_all_documents() -> dict:
    """
    Read OCR-generated TXT files from data/processed and ingest
    them into separate ChromaDB collections.
    """
    counts = {
        "policy_chunks": ingest_folder(
            "policy_collection",
            "data/processed/policies",
            "policy",
        ),
        "claims_chunks": ingest_folder(
            "claims_collection",
            "data/processed/claims",
            "claims",
        ),
        "authorization_chunks": ingest_folder(
            "authorization_collection",
            "data/processed/authorizations",
            "authorization",
        ),
        "billing_chunks": ingest_folder(
            "billing_collection",
            "data/processed/billing",
            "billing",
        ),
    }

    return {
        "status": "success",
        "message": (
            "Processed documents ingested into "
            "separate agent collections"
        ),
        "counts": counts,
    }


def process_and_ingest_documents() -> dict:
    """Run OCR first, then vector ingestion."""
    processing_result = process_uploaded_documents()
    ingestion_result = ingest_all_documents()

    return {
        "processing": processing_result,
        "ingestion": ingestion_result,
    }