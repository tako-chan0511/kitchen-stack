# backend/migrations/env.py
import os
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# --- .env の読込（backend/.env を最優先、見つからなければ親ディレクトリまで探索） ---
try:
    from dotenv import load_dotenv, find_dotenv

    # カレント（通常 backend/）の .env を優先して読む
    _env = os.path.join(os.getcwd(), ".env")
    load_dotenv(_env if os.path.exists(_env) else find_dotenv())
except Exception:
    # dotenv が無くても動作させる
    pass

# --- Alembic 基本設定 ---
config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

# --- メタデータ（モデル定義） ---
try:
    # 例: backend/api/models.py に Base がある想定
    from api.models import Base  # type: ignore

    target_metadata = Base.metadata
except Exception:
    target_metadata = None  # モデル未定義でもエラーにしない


# --- DB URL の解決 ---
def get_url() -> str:
    """
    優先順位:
      1) 環境変数 DATABASE_URL (.env を含む)
      2) alembic.ini の sqlalchemy.url
    どちらも無ければ例外。
    """
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    ini_url = config.get_main_option("sqlalchemy.url", default="")
    if ini_url:
        return ini_url

    raise RuntimeError("DATABASE_URL (or sqlalchemy.url) is not set")


# --- オフライン（SQLスクリプト生成など、接続なし） ---
def run_migrations_offline() -> None:
    """
    Alembic のオフラインモードは同期ドライバ前提。
    例: postgresql+asyncpg -> postgresql へ置換して実行。
    """
    url = get_url().replace("+asyncpg", "")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,  # 型変更も検知
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# --- オンライン（実接続してマイグレーション適用） ---
def _do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    url = get_url()

    # Alembic の async エンジン作成（明示的に url を渡す）
    connectable = async_engine_from_config(
        {"sqlalchemy.url": url},
        prefix="",
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(_do_run_migrations)

    await connectable.dispose()


# --- entry point ---
def run() -> None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())


run()
