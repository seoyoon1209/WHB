# 이력 조회/관리 (SFR-013)
from fastapi import APIRouter

from router.RecordRouter import _records
from router.DiaryRouter import _diaries

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{email}")
def get_history(email: str):
    return {
        "records": [r for r in _records if r["email"] == email],
        "diaries": [d for d in _diaries if d["email"] == email],
    }
