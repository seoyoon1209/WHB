# Cycle phase detection + prediction run/result/rationale/guide (SFR-007~011)
import json
from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.dbpool import DbPoolDep
from ml.phase import compute_phase, PHASE_ORDER
from ml.predict import predict_risk
from ml.advisor import generate_guide

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


class GuideResponse(BaseModel):
    guide: str


async def _get_user_id(conn, username: str) -> int:
    row = await conn.fetchrow("SELECT user_id FROM app_user WHERE username = $1", username)
    if not row:
        raise HTTPException(status_code=404, detail="User not found.")
    return row["user_id"]


async def _resolve_phase(conn, user_id: int) -> tuple[str, int | None]:
    profile = await conn.fetchrow("SELECT cycle_length FROM onboard_profile WHERE user_id = $1", user_id)
    last_record = await conn.fetchrow(
        "SELECT start_date FROM period_record WHERE user_id = $1 ORDER BY start_date DESC LIMIT 1",
        user_id,
    )
    if not profile or not last_record:
        return "Luteal", None

    cycle_length = profile["cycle_length"] or 28
    phase, days_to_period = compute_phase(last_record["start_date"], cycle_length, date.today())
    return phase, days_to_period


async def _build_features(conn, user_id: int, phase: str) -> dict:
    diary = await conn.fetchrow(
        """
        SELECT headache, stomachache, mood_swing, fatigue, sleep_quality, stress,
               appetite, exercise_level, sore_breasts, food_cravings, indigestion, bloating, lh, e3g
        FROM diary_entry WHERE user_id = $1 ORDER BY entry_date DESC LIMIT 1
        """,
        user_id,
    )
    diary = dict(diary) if diary else {}

    def g(key):
        return diary.get(key) or 0

    return {
        "lh": float(g("lh")),
        "estrogen": float(g("e3g")),
        "phase_order": PHASE_ORDER.get(phase, 3),
        "appetite_ord": g("appetite"),
        "exerciselevel_ord": g("exercise_level"),
        "sorebreasts_ord": g("sore_breasts"),
        "fatigue_ord": g("fatigue"),
        "sleepissue_ord": g("sleep_quality"),
        "moodswing_ord": g("mood_swing"),
        "stress_ord": g("stress"),
        "foodcravings_ord": g("food_cravings"),
        "indigestion_ord": g("indigestion"),
        "bloating_ord": g("bloating"),
        "cramps_ord": g("stomachache"),
        "headaches_ord": g("headache"),
    }


@router.get("/{username}/phase", response_model=PhaseResponse)
async def get_phase(username: str, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    phase, days_to_period = await _resolve_phase(conn, user_id)
    return {"phase": phase, "days_to_period": days_to_period}


@router.get("/{username}", response_model=PredictionResponse)
async def get_prediction(username: str, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    phase, days_to_period = await _resolve_phase(conn, user_id)
    features = await _build_features(conn, user_id, phase)
    result = predict_risk(features)

    await conn.execute(
        """
        INSERT INTO prediction_result
            (user_id, phase, days_to_period, headache_risk, stomachache_risk, confidence, factors)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        user_id,
        phase,
        days_to_period,
        result["headache_risk"],
        result["stomachache_risk"],
        result["confidence"],
        json.dumps(result["factors"], ensure_ascii=False),
    )
    return result


@router.get("/{username}/guide", response_model=GuideResponse)
async def get_guide(username: str, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    row = await conn.fetchrow(
        "SELECT name FROM app_user WHERE user_id = $1",
        user_id,
    )
    latest = await conn.fetchrow(
        """
        SELECT headache_risk, stomachache_risk, factors
        FROM prediction_result WHERE user_id = $1 ORDER BY predicted_at DESC LIMIT 1
        """,
        user_id,
    )
    if not latest:
        raise HTTPException(status_code=404, detail="No prediction result found. Please run a prediction first.")

    factors = json.loads(latest["factors"]) if latest["factors"] else []
    try:
        guide = await generate_guide(row["name"], latest["headache_risk"], latest["stomachache_risk"], factors)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to generate AI guide: {exc}")
    return {"guide": guide}
