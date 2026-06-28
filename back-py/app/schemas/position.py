from datetime import datetime
from pydantic import BaseModel, Field


class PositionCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, description="岗位名称")
    company: str | None = None
    salary_range: str | None = None
    experience: str | None = None
    education: str | None = None
    location: str | None = None
    responsibilities: str = Field(..., min_length=1, description="岗位职责")
    requirements: str = Field(..., min_length=1, description="岗位要求")
    skills: list[str] | None = None


class PositionUpdateRequest(BaseModel):
    title: str | None = None
    company: str | None = None
    salary_range: str | None = None
    experience: str | None = None
    education: str | None = None
    location: str | None = None
    responsibilities: str | None = None
    requirements: str | None = None
    skills: list[str] | None = None


class PositionDTO(BaseModel):
    id: int
    title: str
    company: str | None = None
    salary_range: str | None = None
    experience: str | None = None
    education: str | None = None
    location: str | None = None
    responsibilities: str | None = None
    requirements: str | None = None
    skills: list[str] | None = None
    created_by: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
