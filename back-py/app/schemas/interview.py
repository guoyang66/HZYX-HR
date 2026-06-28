from datetime import datetime
from pydantic import BaseModel, Field


class InterviewQuestionDTO(BaseModel):
    question: str
    type: str
    difficulty: str
    skill: str
    answerPoints: str | None = None
    evaluationDimension: str | None = None


class GenerateQuestionsRequest(BaseModel):
    positionId: int | None = None
    skills: list[str] | None = None
    difficulty: str = "MIDDLE"
    count: int = Field(default=5, ge=1, le=20)
    questionType: str = "MIXED"
    includeAnswers: bool = True
    businessDomain: str = "企业金融/支付"


class InterviewRecordDTO(BaseModel):
    id: int
    positionId: int | None = None
    positionTitle: str | None = None
    userId: int
    difficulty: str | None = None
    questionType: str | None = None
    questions: list[InterviewQuestionDTO] | None = None
    createdAt: datetime | None = None
