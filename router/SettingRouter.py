# 모드 전환/개인정보·동의/비진단 고지 (SFR-014~016)
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/settings", tags=["settings"])

_settings: dict[str, dict] = {}


class ModeRequest(BaseModel):
    mode: str  # "precision" | "simple"


@router.put("/{email}/mode", response_model=ModeRequest)
def set_mode(email: str, body: ModeRequest):
    _settings.setdefault(email, {})["mode"] = body.mode
    return body


@router.get("/disclaimer")
def get_disclaimer():
    return {"text": "본 서비스는 진단 도구가 아니며 참고용입니다."}
