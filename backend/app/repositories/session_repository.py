from datetime import datetime, timezone

from app.database import database


async def create_session(
    role: str,
    resume_filename: str,
    resume_text: str,
    candidate_profile: dict,
) -> str:
    session = {
        "role": role,
        "resume_filename": resume_filename,
        "resume_text": resume_text,
        "candidate_profile": candidate_profile,
        "status": "created",
        "current_question_index": 0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    result = await database.sessions.insert_one(session)

    return str(result.inserted_id)
