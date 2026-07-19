import asyncpg
from settings.Settings import get_settings
from fastapi import Depends
from typing import Annotated, AsyncGenerator

dbpool = None


async def init():
    global dbpool
    if dbpool is not None:
        return

    settings = get_settings()

    dbpool = await asyncpg.create_pool(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_password or None,
        ssl="require" if settings.db_ssl else None,
        statement_cache_size=0,
        min_size=1,
        max_size=10,
    )


async def dispose():
    global dbpool
    if dbpool:
        await dbpool.close()
        dbpool = None


async def get_db_connection() -> AsyncGenerator:
    global dbpool
    if dbpool is None:
        raise Exception("Database pool is not initialized. Call init() first.")

    async with dbpool.acquire() as conn:
        yield conn


DbConnectionDep = Annotated[asyncpg.Connection, Depends(get_db_connection)]
DbPoolDep = DbConnectionDep
