import os
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BACKEND_DIR / ".env")

raw_chroma_path = os.getenv("CHROMA_PATH", "./chroma_data")
CHROMA_PATH = Path(raw_chroma_path)

if not CHROMA_PATH.is_absolute():
    CHROMA_PATH = BACKEND_DIR / CHROMA_PATH

COLLECTION_NAME = "role_knowledge_base"

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path=str(CHROMA_PATH))

collection = client.get_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_function,
)


def normalize_role(role: str) -> str:
    role_key = role.lower().strip()

    role_mapping = {
        "ai/ml engineer": "AI/ML ENGINEER",
        "ai ml engineer": "AI/ML ENGINEER",
        "backend engineer": "BACKEND ENGINEER",
        "data scientist": "DATA SCIENTIST",
    }

    return role_mapping.get(role_key, role.upper().strip())


def build_retrieval_query(
    role: str,
    skills: list[str],
    projects: list[str],
    topic_hint: str | None = None,
) -> str:
    skill_text = ", ".join(skills[:10]) if skills else "not specified"
    project_text = " ".join(projects[:3]) if projects else "not specified"
    hint_text = topic_hint or "core technical concepts"

    return (
        f"Technical interview for role: {role}. "
        f"Candidate skills: {skill_text}. "
        f"Candidate projects: {project_text}. "
        f"Topic to evaluate: {hint_text}."
    )


def retrieve_context(
    role: str,
    skills: list[str],
    projects: list[str],
    topic_hint: str | None = None,
    top_k: int = 3,
) -> dict:
    normalized_role = normalize_role(role)

    query = build_retrieval_query(
        role=role,
        skills=skills,
        projects=projects,
        topic_hint=topic_hint,
    )

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where={"role": normalized_role},
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    chunks = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        chunks.append(
            {
                "content": document,
                "source": metadata.get("source"),
                "role": metadata.get("role"),
                "chunk_index": metadata.get("chunk_index"),
                "distance": round(float(distance), 4),
            }
        )

    return {
        "query": query,
        "role_filter": normalized_role,
     
   "chunks": chunks,
    }
