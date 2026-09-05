from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status, Query

from app.models.schemas import CreateSessionResponse
from app.repositories.session_repository import create_session
from app.services.resume_analyzer import analyze_resume
from app.services.resume_parser import extract_resume_text
from app.services.rag_service import retrieve_context

router = APIRouter(
    prefix="/api/sessions",
    tags=["Interview Sessions"]
)

ALLOWED_ROLES = {
    "AI/ML Engineer",
    "Backend Engineer",
}


@router.post(
    "",
    response_model=CreateSessionResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_interview_session(
    role: str = Form(...),
    resume: UploadFile = File(...),
):
    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported role. Choose one of: {', '.join(ALLOWED_ROLES)}"
        )

    if not resume.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume filename is missing."
        )

    allowed_extensions = (".pdf", ".txt")

    if not resume.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and TXT resume files are supported."
        )

    file_bytes = await resume.read()

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded resume file is empty."
        )

    try:
        resume_text = extract_resume_text(
            resume.filename,
            file_bytes
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not read the uploaded resume file."
        ) from error

    if not resume_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "No readable text was found in the resume. "
                "Please upload a text-based PDF or TXT resume."
            )
        )

    candidate_profile = analyze_resume(resume_text)

    session_id = await create_session(
        role=role,
        resume_filename=resume.filename,
        resume_text=resume_text,
        candidate_profile=candidate_profile,
    )

    return {
        "session_id": session_id,
        "role": role,
        "resume_filename": resume.filename,
        "candidate_profile": candidate_profile,
        "message": "Resume processed and interview session created successfully."
    }
@router.get("/rag-test")
async def test_rag_retrieval(
    role: str = Query(...),
    skills: str = Query(""),
    projects: str = Query(""),
    topic: str | None = Query(None),
):
    skill_list = [
        item.strip()
        for item in skills.split(",")
        if item.strip()
    ]

    project_list = [
        item.strip()
        for item in projects.split("|")
        if item.strip()
    ]

    try:
        return retrieve_context(
            role=role,
            skills=skill_list,
            projects=project_list,
            topic_hint=topic,
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"RAG retrieval failed: {str(error)}"
        )
