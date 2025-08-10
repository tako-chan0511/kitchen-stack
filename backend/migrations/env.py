# backend/migrations/env.py
import os, asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

from api.models import Base
target_metadata = Base.metadata
# .env を読む（python-dotenv があれば）
try:
    from dotenv import load_dotenv
    load_dotenv()  # backend/.env を読み込む想定
except Exception:
    pass

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

# モデルがあるなら Base.metadata を使う。無ければ None のままでOK
try:
    from api.models import Base
    target_metadata = Base.metadata
except Exception:
    target_metadata = None

def get_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url

def run_migrations_offline():
    context.configure(url=get_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    engine = create_async_engine(get_url(), pool_pre_ping=True)
    async with engine.connect() as conn:
        await conn.run_sync(do_run_migrations)

def run():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())

run()
