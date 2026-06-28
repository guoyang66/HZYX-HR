from datetime import datetime
from pydantic import BaseModel, Field


class BossResumeRequest(BaseModel):
    resumeContent: str = Field(..., min_length=1)
    candidateName: str | None = None
    candidatePhone: str | None = None
    candidateEmail: str | None = None
    desiredPosition: str | None = None
    desiredCity: str | None = None
    expectedSalary: str | None = None
    workYears: str | None = None
    education: str | None = None
    sourceResumeId: str | None = None
    sourceUrl: str | None = None


class PositionMatchItem(BaseModel):
    positionId: int
    positionTitle: str
    finalScore: float | None = None
    graphScore: float | None = None
    llmScore: float | None = None
    matchGrade: str | None = None
    matchedSkills: list[str] | None = None
    missingSkills: list[str] | None = None
    llmReport: str | None = None
    passedScreening: bool = False
    recommendLevel: int | None = None


class BossMatchResponse(BaseModel):
    sourceResumeId: str | None = None
    candidateName: str | None = None
    matchedPositionCount: int = 0
    positionMatches: list[PositionMatchItem] = []
    overallVerdict: str | None = None
    overallScore: float | None = None
    llmScreeningReport: str | None = None
    recommendInterview: bool = False
    processedAt: datetime | None = None
