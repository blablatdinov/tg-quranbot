# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from databases import Database

from settings import settings

pgsql = Database(
    str(settings.DATABASE_URL),
    min_size=settings.DATABASE_POOL_MIN_SIZE,
    max_size=settings.DATABASE_POOL_MAX_SIZE,
)
