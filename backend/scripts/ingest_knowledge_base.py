import hashlib
import os
import shutil
import sys
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(BACKEND_DIR / ".env")

KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "data" / "knowledge_base"
CHROMA_PATH = Path(
    os.getenv("CHROMA_PATH", str(BACKEND_DIR / "chroma_data"))
)

COLLECTION_NAME = "role_knowledge_base"


def chunk_text(text: str, chunk_size: int = 120, overlap: int = 30) -> list[str]:
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end]).strip()

        if chunk:
            chunks.append(chunk)

        if end == len(words):
            break

        start = end - overlap

    return chunks


def role_from_path(file_path: Path) -> str:
    return file_path.parent.name.replace("_", " ").upper()


def load_chunks() -> tuple[list[str], list[dict], list[str]]:
    documents = []
    metadatas = []
    ids = []

    for file_path in KNOWLEDGE_BASE_DIR.rglob("*.txt"):
        raw_text = file_path.read_text(encoding="utf-8").strip()
        role = role_from_path(file_path)
        chunks = chunk_text(raw_text)

        for index, chunk in enumerate(chunks):
            stable_id = hashlib.sha256(
                f"{file_path}:{index}:{chunk}".encode("utf-8")
            ).hexdigest()

            documents.append(chunk)
            metadatas.append(
                {
                    "role": role,
                    "source": file_path.name,
                    "relative_path": str(file_path.relative_to(PROJECT_ROOT)),
                    "chunk_index": index,
                }
            )
            ids.append(stable_id)

    return documents, metadatas, ids


def main():
    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge-base directory not found: {KNOWLEDGE_BASE_DIR}"
        )

    documents, metadatas, ids = load_chunks()

    if not documents:
        raise ValueError("No .txt knowledge-base documents were found.")

    if CHROMA_PATH.exists():
        shutil.rmtree(CHROMA_PATH)

    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={"description": "Role-specific interview knowledge base"},
    )

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"Created ChromaDB at: {CHROMA_PATH}")
    print(f"Indexed {len(documents)} chunks into '{COLLECTION_NAME}'.")

    for metadata in metadatas:
        print(
            f"- role={metadata['role']} | "
            f"source={metadata['source']} | "
            f"chunk={metadata['chunk_index']}"
        )


if __name__ == "__main__":
    main()
