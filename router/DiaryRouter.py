# 증상/생활/호르몬 자가보고 (SFR-004~006)
from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.dbpool import DbPoolDep

router = APIRouter(prefix="/diaries", tags=["diaries"])


class DiaryEntry(BaseModel):
    entry_date: date
    headache: int | None = None
    stomachache: int | None = None
    mood: str | None = None
    fatigue: int | None = None
    sleep_quality: int | None = None
    stress: int | None = None
    lh: float | None = None
    e3g: float | None = None
    pdg: float | None = None


class DiaryEntryResponse(DiaryEntry):
    diary_id: int


class HormoneEntry(BaseModel):
    entry_date: date
    lh: float | None = None
    e3g: float | None = None
    pdg: float | None = None


async def _get_user_id(conn, username: str) -> int:
    row = await conn.fetchrow("SELECT user_id FROM app_user WHERE username = $1", username)
    if not row:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return row["user_id"]


@router.post("/{username}", response_model=DiaryEntryResponse)
async def create_entry(username: str, body: DiaryEntry, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    row = await conn.fetchrow(
        """
        INSERT INTO diary_entry
            (user_id, entry_date, headache, stomachache, mood, fatigue, sleep_quality, stress, lh, e3g, pdg)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        ON CONFLICT (user_id, entry_date) DO UPDATE SET
            headache = EXCLUDED.headache,
            stomachache = EXCLUDED.stomachache,
            mood = EXCLUDED.mood,
            fatigue = EXCLUDED.fatigue,
            sleep_quality = EXCLUDED.sleep_quality,
            stress = EXCLUDED.stress,
            lh = EXCLUDED.lh,
            e3g = EXCLUDED.e3g,
            pdg = EXCLUDED.pdg
        RETURNING diary_id, entry_date, headache, stomachache, mood, fatigue, sleep_quality, stress, lh, e3g, pdg
        """,
        user_id,
        body.entry_date,
        body.headache,
        body.stomachache,
        body.mood,
        body.fatigue,
        body.sleep_quality,
        body.stress,
        body.lh,
        body.e3g,
        body.pdg,
    )
    return dict(row)


@router.put("/{username}/hormone", response_model=DiaryEntryResponse)
async def upsert_hormone(username: str, body: HormoneEntry, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    row = await conn.fetchrow(
        """
        INSERT INTO diary_entry (user_id, entry_date, lh, e3g, pdg)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (user_id, entry_date) DO UPDATE SET
            lh = EXCLUDED.lh,
            e3g = EXCLUDED.e3g,
            pdg = EXCLUDED.pdg
        RETURNING diary_id, entry_date, headache, stomachache, mood, fatigue, sleep_quality, stress, lh, e3g, pdg
        """,
        user_id,
        body.entry_date,
        body.lh,
        body.e3g,
        body.pdg,
    )
    return dict(row)


@router.get("/{username}", response_model=list[DiaryEntryResponse])
async def list_entries(username: str, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    rows = await conn.fetch(
        """
        SELECT diary_id, entry_date, headache, stomachache, mood, fatigue, sleep_quality, stress, lh, e3g, pdg
        FROM diary_entry WHERE user_id = $1 ORDER BY entry_date DESC
        """,
        user_id,
    )
    return [dict(row) for row in rows]
