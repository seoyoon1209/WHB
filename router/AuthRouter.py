# 회원가입/로그인/로그아웃 (SFR-001)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

_users: dict[str, dict] = {}


class SignupRequest(BaseModel):
    email: str
    password: str
    name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    email: str
    name: str


@router.post("/signup", response_model=UserResponse)
def signup(body: SignupRequest):
    if body.email in _users:
        raise HTTPException(status_code=409, detail="이미 가입된 이메일입니다.")
    _users[body.email] = {"password": body.password, "name": body.name}
    return {"email": body.email, "name": body.name}


@router.post("/login", response_model=UserResponse)
def login(body: LoginRequest):
    user = _users.get(body.email)
    if not user or user["password"] != body.password:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    return {"email": body.email, "name": user["name"]}


@router.post("/logout")
def logout():
    return {"status": "ok"}
