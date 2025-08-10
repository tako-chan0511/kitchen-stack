from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .routers import health

def create_app(mount_static: bool = False) -> FastAPI:
    app = FastAPI(title="kitchen-stack API")
    app.include_router(health.router, prefix="/api", tags=["health"])
    if mount_static:
        dist = Path(__file__).resolve().parents[1] / "dist"
        if dist.exists():
            app.mount("/", StaticFiles(directory=dist, html=True), name="static")
    return app

app = create_app()
