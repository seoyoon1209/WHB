# Period tracking (SFR-003)
from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.dbpool import DbPoolDep

router = APIRouter(prefix="/records", tags=["records"])


class PeriodRecord(BaseModel):
    start_date: date
    end_date: date | None = None


class PeriodRecordResponse(PeriodRecord):
    record_id: int


class EndDateRequest(BaseModel):
    end_date: date


async def _get_user_id(conn, username: str) -> int:
    row = await conn.fetchrow("SELECT user_id FROM app_user WHERE username = $1", username)
    if not row:
        raise HTTPException(status_code=404, detail="User not found.")
    return row["user_id"]


@router.post("/{username}", response_model=PeriodRecordResponse)
async def create_record(username: str, body: PeriodRecord, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    row = await conn.fetchrow(
        """
        INSERT INTO period_record (user_id, start_date, end_date)
        VALUES ($1, $2, $3)
        RETURNING record_id, start_date, end_date
        """,
        user_id,
        body.start_date,
        body.end_date,
    )
    return dict(row)


@router.get("/{username}", response_model=list[PeriodRecordResponse])
async def list_records(username: str, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    rows = await conn.fetch(
        "SELECT record_id, start_date, end_date FROM period_record WHERE user_id = $1 ORDER BY start_date DESC",
        user_id,
    )
    return [dict(row) for row in rows]


@router.delete("/{username}/{record_id}", status_code=204)
async def delete_record(username: str, record_id: int, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    result = await conn.execute(
        "DELETE FROM period_record WHERE record_id = $1 AND user_id = $2",
        record_id,
        user_id,
    )
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Record not found.")


@router.patch("/{username}/latest", response_model=PeriodRecordResponse)
async def set_latest_end_date(username: str, body: EndDateRequest, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    row = await conn.fetchrow(
        """
        UPDATE period_record SET end_date = $2
        WHERE record_id = (
            SELECT record_id FROM period_record
            WHERE user_id = $1 AND end_date IS NULL
            ORDER BY start_date DESC LIMIT 1
        )
        RETURNING record_id, start_date, end_date
        """,
        user_id,
        body.end_date,
    )
    if not row:
        raise HTTPException(status_code=404, detail="No ongoing record to end.")
    return dict(row)
