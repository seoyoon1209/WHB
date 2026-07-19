# History view/manage (SFR-013)
from fastapi import APIRouter, HTTPException
from db.dbpool import DbPoolDep

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{username}")
async def get_history(username: str, conn: DbPoolDep):
    user_row = await conn.fetchrow("SELECT user_id FROM app_user WHERE username = $1", username)
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found.")
    user_id = user_row["user_id"]

    records = await conn.fetch(
        "SELECT record_id, start_date, end_date FROM period_record WHERE user_id = $1 ORDER BY start_date DESC",
        user_id,
    )
    diaries = await conn.fetch(
        """
        SELECT diary_id, entry_date, headache, stomachache, mood, mood_swing, fatigue, sleep_quality, stress,
               appetite, exercise_level, sore_breasts, food_cravings, indigestion, bloating
        FROM diary_entry WHERE user_id = $1 ORDER BY entry_date DESC
        """,
        user_id,
    )

    return {
        "records": [dict(r) for r in records],
        "diaries": [dict(d) for d in diaries],
    }
