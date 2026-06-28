from datetime import datetime
from pydantic import BaseModel, Field


class MatchRequestDTO(BaseModel):
    resumeId: int = Field(..., description="简历ID")
    positionId: int = Field(..., description="岗位ID")


class MatchResultDTO(BaseModel):
    id: int
    resumeId: int
    positionId: int
    resumeName: str | None = None
    positionTitle: str | None = None
    finalScore: float | None = None
    ragScore: float | None = None
    graphScore: float | None = None
    llmScore: float | None = None
    matchedSkills: list[str] | None = None
    missingSkills: list[str] | None = None
    extraSkills: list[str] | None = None
    llmReport: str | None = None
    matchGrade: str | None = None
    recommendLevel: int | None = None
    scoreDetails: dict | None = None
    createdAt: datetime | None = None
