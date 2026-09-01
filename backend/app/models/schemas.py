from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    skills: list[str] = Field(default_factory=list)
    experience_level: str
    projects: list[str] = Field(default_factory=list)
    resume_length: int


class CreateSessionResponse(BaseModel):
    session_id: str
    role: str
    resume_filename: str
    candidate_profile: CandidateProfile
    message: str
