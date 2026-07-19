# 증상/생활/호르몬 자가보고 (SFR-004~006)
from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.dbpool import DbPoolDep

router = APIRouter(prefix="/diaries", tags=["diaries"])

# data.csv의 *_ord 피처와 1:1 대응. cramps_severe(=cramps_ord>=4)처럼 데이터셋에만 있는
# 파생 라벨은 사용자 입력이 아니라 예측 시점에 계산하는 값이라 여기 포함하지 않는다.
_ENTRY_COLUMNS = (
    "headache",       # headaches_ord
    "stomachache",    # cramps_ord
    "mood",
    "mood_swing",     # moodswing_ord
    "fatigue",        # fatigue_ord
    "sleep_quality",  # sleepissue_ord
    "stress",         # stress_ord
    "appetite",       # appetite_ord
    "exercise_level", # exerciselevel_ord
    "sore_breasts",   # sorebreasts_ord
    "food_cravings",  # foodcravings_ord
    "indigestion",    # indigestion_ord
    "bloating",       # bloating_ord
    "lh",             # lh
    "e3g",            # estrogen
    "pdg",
)


class DiaryEntry(BaseModel):
    entry_date: date
    headache: int | None = None
    stomachache: int | None = None
    mood: str | None = None
    mood_swing: int | None = None
    fatigue: int | None = None
    sleep_quality: int | None = None
    stress: int | None = None
    appetite: int | None = None
    exercise_level: int | None = None
    sore_breasts: int | None = None
    food_cravings: int | None = None
    indigestion: int | None = None
    bloating: int | None = None
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
    columns = ", ".join(_ENTRY_COLUMNS)
    placeholders = ", ".join(f"${i + 3}" for i in range(len(_ENTRY_COLUMNS)))
    update_set = ", ".join(f"{c} = EXCLUDED.{c}" for c in _ENTRY_COLUMNS)
    row = await conn.fetchrow(
        f"""
        INSERT INTO diary_entry (user_id, entry_date, {columns})
        VALUES ($1, $2, {placeholders})
        ON CONFLICT (user_id, entry_date) DO UPDATE SET
            {update_set}
        RETURNING diary_id, entry_date, {columns}
        """,
        user_id,
        body.entry_date,
        *(getattr(body, c) for c in _ENTRY_COLUMNS),
    )
    return dict(row)


@router.put("/{username}/hormone", response_model=DiaryEntryResponse)
async def upsert_hormone(username: str, body: HormoneEntry, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    columns = ", ".join(_ENTRY_COLUMNS)
    row = await conn.fetchrow(
        f"""
        INSERT INTO diary_entry (user_id, entry_date, lh, e3g, pdg)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (user_id, entry_date) DO UPDATE SET
            lh = EXCLUDED.lh,
            e3g = EXCLUDED.e3g,
            pdg = EXCLUDED.pdg
        RETURNING diary_id, entry_date, {columns}
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
    columns = ", ".join(_ENTRY_COLUMNS)
    rows = await conn.fetch(
        f"""
        SELECT diary_id, entry_date, {columns}
        FROM diary_entry WHERE user_id = $1 ORDER BY entry_date DESC
        """,
        user_id,
    )
    return [dict(row) for row in rows]
