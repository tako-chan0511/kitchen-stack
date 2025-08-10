# backend/api/core/db.py
import os
from sqlalchemy.ext.asyncio import create_async_engine

# .env を読みたい場合（既にアプリ側で読み込んでいれば不要）
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        url = os.getenv("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL is not set")
        _engine = create_async_engine(url, pool_pre_ping=True)
    return _engine

async def ping_db() -> bool:
    engine = get_engine()
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False
