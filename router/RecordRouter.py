# 월경 기록 (SFR-003)
from datetime import date

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/records", tags=["records"])

_records: list[dict] = []


class PeriodRecord(BaseModel):
    email: str
    start_date: date
    end_date: date | None = None


@router.post("", response_model=PeriodRecord)
def create_record(body: PeriodRecord):
    _records.append(body.model_dump())
    return body


@router.get("/{email}", response_model=list[PeriodRecord])
def list_records(email: str):
    return [r for r in _records if r["email"] == email]
