from datetime import datetime
from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    resumeId: int
    fileName: str
    parsedContent: str
    extractedSkills: list[str]
    message: str


class ResumeDTO(BaseModel):
    id: int
    userId: int
    fileName: str | None = None
    filePath: str | None = None
    content: str | None = None
    extractedSkills: list[str] | None = None
    createdAt: datetime | None = None
