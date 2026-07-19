# 실제 결과 피드백/개인화 (SFR-012)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.dbpool import DbPoolDep

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackEntry(BaseModel):
    username: str
    headache_actual: bool
    stomachache_actual: bool


class FeedbackResponse(BaseModel):
    feedback_id: int
    headache_actual: bool
    stomachache_actual: bool


@router.post("", response_model=FeedbackResponse)
async def create_feedback(body: FeedbackEntry, conn: DbPoolDep):
    user_row = await conn.fetchrow("SELECT user_id FROM app_user WHERE username = $1", body.username)
    if not user_row:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    prediction_row = await conn.fetchrow(
        "SELECT prediction_id FROM prediction_result WHERE user_id = $1 ORDER BY predicted_at DESC LIMIT 1",
        user_row["user_id"],
    )

    row = await conn.fetchrow(
        """
        INSERT INTO feedback_result (prediction_id, user_id, headache_actual, stomachache_actual)
        VALUES ($1, $2, $3, $4)
        RETURNING feedback_id, headache_actual, stomachache_actual
        """,
        prediction_row["prediction_id"] if prediction_row else None,
        user_row["user_id"],
        body.headache_actual,
        body.stomachache_actual,
    )
    return dict(row)
