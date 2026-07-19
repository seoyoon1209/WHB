# 기초정보 입력(온보딩) (SFR-002)
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/onboard", tags=["onboard"])

_profiles: dict[str, dict] = {}


class OnboardRequest(BaseModel):
    age: int
    menarche_age: int
    cycle_length: int
    cycle_regular: bool
    pain_history: str | None = None


@router.put("/{email}", response_model=OnboardRequest)
def upsert_profile(email: str, body: OnboardRequest):
    _profiles[email] = body.model_dump()
    return body


@router.get("/{email}", response_model=OnboardRequest | None)
def get_profile(email: str):
    return _profiles.get(email)
