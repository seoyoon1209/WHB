# 증상/생활/호르몬 자가보고 (SFR-004~006)
from datetime import date

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/diaries", tags=["diaries"])

_diaries: list[dict] = []


class DiaryEntry(BaseModel):
    email: str
    entry_date: date
    headache: int | None = None
    stomachache: int | None = None
    mood: str | None = None
    sleep_quality: int | None = None
    stress: int | None = None
    lh: float | None = None
    e3g: float | None = None
    pdg: float | None = None


@router.post("", response_model=DiaryEntry)
def create_entry(body: DiaryEntry):
    _diaries.append(body.model_dump())
    return body


@router.get("/{email}", response_model=list[DiaryEntry])
def list_entries(email: str):
    return [d for d in _diaries if d["email"] == email]
