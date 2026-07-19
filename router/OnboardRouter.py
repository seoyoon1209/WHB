# Onboarding basic info input (SFR-002)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.dbpool import DbPoolDep

router = APIRouter(prefix="/onboard", tags=["onboard"])


class OnboardRequest(BaseModel):
    age: int
    menarche_age: int
    cycle_length: int
    cycle_regular: bool
    pain_history: str | None = None


async def _get_user_id(conn, username: str) -> int:
    row = await conn.fetchrow("SELECT user_id FROM app_user WHERE username = $1", username)
    if not row:
        raise HTTPException(status_code=404, detail="User not found.")
    return row["user_id"]


@router.put("/{username}", response_model=OnboardRequest)
async def upsert_profile(username: str, body: OnboardRequest, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    row = await conn.fetchrow(
        """
        INSERT INTO onboard_profile (user_id, age, menarche_age, cycle_length, cycle_regular, pain_history)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (user_id) DO UPDATE SET
            age = EXCLUDED.age,
            menarche_age = EXCLUDED.menarche_age,
            cycle_length = EXCLUDED.cycle_length,
            cycle_regular = EXCLUDED.cycle_regular,
            pain_history = EXCLUDED.pain_history,
            updated_at = CURRENT_TIMESTAMP
        RETURNING age, menarche_age, cycle_length, cycle_regular, pain_history
        """,
        user_id,
        body.age,
        body.menarche_age,
        body.cycle_length,
        body.cycle_regular,
        body.pain_history,
    )
    return dict(row)


@router.get("/{username}", response_model=OnboardRequest | None)
async def get_profile(username: str, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    row = await conn.fetchrow(
        "SELECT age, menarche_age, cycle_length, cycle_regular, pain_history FROM onboard_profile WHERE user_id = $1",
        user_id,
    )
    return dict(row) if row else None
