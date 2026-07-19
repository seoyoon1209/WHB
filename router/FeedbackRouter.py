# 실제 결과 피드백/개인화 (SFR-012)
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/feedback", tags=["feedback"])

_feedbacks: list[dict] = []


class FeedbackEntry(BaseModel):
    email: str
    headache_actual: bool
    stomachache_actual: bool


@router.post("", response_model=FeedbackEntry)
def create_feedback(body: FeedbackEntry):
    _feedbacks.append(body.model_dump())
    return body
