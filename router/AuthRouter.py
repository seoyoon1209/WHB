# 회원가입/로그인/로그아웃 (SFR-001)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.dbpool import DbPoolDep

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    username: str
    password: str
    name: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UpdateNameRequest(BaseModel):
    name: str


class UserResponse(BaseModel):
    username: str
    name: str


@router.post("/signup", response_model=UserResponse)
async def signup(body: SignupRequest, conn: DbPoolDep):
    existing = await conn.fetchrow("SELECT 1 FROM app_user WHERE username = $1", body.username)
    if existing:
        raise HTTPException(status_code=409, detail="이미 가입된 아이디입니다.")

    row = await conn.fetchrow(
        """
        INSERT INTO app_user (username, password_hash, name)
        VALUES ($1, crypt($2, gen_salt('bf')), $3)
        RETURNING user_id, username, name
        """,
        body.username,
        body.password,
        body.name,
    )
    await conn.execute(
        "INSERT INTO user_setting (user_id, mode, consent) VALUES ($1, 'simple', TRUE)",
        row["user_id"],
    )
    return dict(row)


@router.post("/login", response_model=UserResponse)
async def login(body: LoginRequest, conn: DbPoolDep):
    row = await conn.fetchrow(
        """
        SELECT username, name
        FROM app_user
        WHERE username = $1 AND password_hash = crypt($2, password_hash)
        """,
        body.username,
        body.password,
    )
    if not row:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
    return dict(row)


@router.put("/{username}", response_model=UserResponse)
async def update_name(username: str, body: UpdateNameRequest, conn: DbPoolDep):
    row = await conn.fetchrow(
        "UPDATE app_user SET name = $2 WHERE username = $1 RETURNING username, name",
        username,
        body.name,
    )
    if not row:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return dict(row)


@router.post("/logout")
def logout():
    return {"status": "ok"}
