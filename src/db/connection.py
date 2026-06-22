# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from sqlalchemy.ext.asyncio import create_async_engine

from settings import settings

pgsql = create_async_engine(
    str(settings.DATABASE_URL).replace('postgres://', 'postgresql+asyncpg://'),
    pool_size=settings.DATABASE_POOL_MIN_SIZE,
    max_overflow=settings.DATABASE_POOL_MAX_SIZE - settings.DATABASE_POOL_MIN_SIZE,
)
