import pymupdf


def extract_text_from_pdf(file_bytes: bytes) -> str:
    document = pymupdf.open(stream=file_bytes, filetype="pdf")

    try:
        return "\n".join(page.get_text() for page in document).strip()
    finally:
        document.close()


def extract_resume_text(filename: str, file_bytes: bytes) -> str:
    filename = filename.lower()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)

    if filename.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore").strip()

    raise ValueError("Only PDF and TXT resume files are supported.")
