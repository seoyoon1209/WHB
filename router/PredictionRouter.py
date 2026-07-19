# 주기 단계 판단 + 예측 실행/결과/근거 (SFR-007~010)
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/predictions", tags=["predictions"])


class PhaseResponse(BaseModel):
    phase: str
    days_to_period: int


class PredictionResponse(BaseModel):
    headache_risk: str
    stomachache_risk: str
    confidence: float
    factors: list[str]


@router.get("/{email}/phase", response_model=PhaseResponse)
def get_phase(email: str):
    return {"phase": "luteal", "days_to_period": 3}


@router.get("/{email}", response_model=PredictionResponse)
def get_prediction(email: str):
    return {
        "headache_risk": "moderate",
        "stomachache_risk": "high",
        "confidence": 0.7,
        "factors": ["에스트로겐 급락", "수면 부족"],
    }
