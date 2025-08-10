# backend/api/routers/health.py
from fastapi import APIRouter

# ★ 参照先を core.db に変更
from ..core.db import ping_db

router = APIRouter()

@router.get("/healthz")
async def healthz():
    return {"status": "ok"}

@router.get("/healthz/db")
async def healthz_db():
    ok = await ping_db()
    return {"db": "ok" if ok else "ng"}
