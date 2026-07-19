# 모드 전환/개인정보·동의/비진단 고지 (SFR-014~016)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.dbpool import DbPoolDep

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingResponse(BaseModel):
    mode: str
    consent: bool


class ModeRequest(BaseModel):
    mode: str  # "precision" | "simple"


class ConsentRequest(BaseModel):
    consent: bool


async def _get_user_id(conn, username: str) -> int:
    row = await conn.fetchrow("SELECT user_id FROM app_user WHERE username = $1", username)
    if not row:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return row["user_id"]


@router.get("/disclaimer")
def get_disclaimer():
    return {"text": "본 서비스는 진단 도구가 아니며 참고용입니다."}


@router.get("/{username}", response_model=SettingResponse)
async def get_setting(username: str, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    row = await conn.fetchrow("SELECT mode, consent FROM user_setting WHERE user_id = $1", user_id)
    if not row:
        raise HTTPException(status_code=404, detail="설정이 없습니다.")
    return dict(row)


@router.put("/{username}/mode", response_model=SettingResponse)
async def set_mode(username: str, body: ModeRequest, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    row = await conn.fetchrow(
        """
        UPDATE user_setting SET mode = $2, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = $1
        RETURNING mode, consent
        """,
        user_id,
        body.mode,
    )
    return dict(row)


@router.put("/{username}/consent", response_model=SettingResponse)
async def set_consent(username: str, body: ConsentRequest, conn: DbPoolDep):
    user_id = await _get_user_id(conn, username)
    row = await conn.fetchrow(
        """
        UPDATE user_setting SET consent = $2, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = $1
        RETURNING mode, consent
        """,
        user_id,
        body.consent,
    )
    return dict(row)
