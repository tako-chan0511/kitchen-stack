# backend/api/main.py
import os
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .routers import health

log = logging.getLogger("kitchen-stack")


def create_app(*, mount_static: bool | None = None) -> FastAPI:
    """FastAPI App Factory.

    Args:
        mount_static: True なら / に backend/dist をマウント。
                      None の場合は .env の MOUNT_STATIC を参照。
    """
    # .env を読む（DATABASE_URL などもここで読み込まれる）
    load_dotenv()

    app = FastAPI(title="kitchen-stack API", version="0.1.0")

    # ルーター
    app.include_router(health.router, prefix="/api", tags=["health"])

    # CORS（必要に応じて絞り込み）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 環境変数から静的配信の有効/無効を決定
    if mount_static is None:
        mount_static = os.getenv("MOUNT_STATIC", "0").lower() in ("1", "true", "yes", "on")

    if mount_static:
        dist = Path(__file__).resolve().parents[1] / "dist"
        if dist.exists():
            app.mount("/", StaticFiles(directory=dist, html=True), name="static")
            log.info("Static files mounted at '/' from %s", dist)
        else:
            log.warning("MOUNT_STATIC is true but dist not found: %s", dist)

    # 静的配信をしないときの疎通確認（静的配信中は StaticFiles が優先される）
    @app.get("/")
    async def root():
        return {"service": "kitchen-stack", "status": "ok"}

    return app


# Uvicorn エントリポイント
# .env で MOUNT_STATIC=1 を指定すれば、Render/Docker 本番でもそのまま動きます。
app = create_app()
