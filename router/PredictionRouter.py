# 주기 단계 판단 + 예측 실행/결과/근거 (SFR-007~010)
import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.dbpool import DbPoolDep

router = APIRouter(prefix="/predictions", tags=["predictions"])


class PhaseResponse(BaseModel):
    phase: str
    days_to_period: int | None = None


class Factor(BaseModel):
    label: str
    value: float


class PredictionResponse(BaseModel):
    headache_risk: str
    stomachache_risk: str
    confidence: float | None = None
    factors: list[Factor]


async def _get_user_id(conn, username: str) -> int:
    row = await conn.fetchrow("SELECT user_id FROM app_user WHERE username = $1", username)
    if not row:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return row["user_id"]


@router.get("/{username}/phase", response_model=PhaseResponse)
async def get_phase(username: str, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    row = await conn.fetchrow(
        "SELECT phase, days_to_period FROM prediction_result WHERE user_id = $1 ORDER BY predicted_at DESC LIMIT 1",
        user_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="예측 결과가 없습니다.")
    return dict(row)


@router.get("/{username}", response_model=PredictionResponse)
async def get_prediction(username: str, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    row = await conn.fetchrow(
        """
        SELECT headache_risk, stomachache_risk, confidence, factors
        FROM prediction_result WHERE user_id = $1 ORDER BY predicted_at DESC LIMIT 1
        """,
        user_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="예측 결과가 없습니다.")
    data = dict(row)
    data["factors"] = json.loads(data["factors"]) if data["factors"] else []
    return data
