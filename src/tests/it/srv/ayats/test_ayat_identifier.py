# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from app_types.fk_async_int import FkAsyncInt
from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.pg_ayat_identifier import PgAyatIdentifier


@pytest.mark.usefixtures('db_ayat')
async def test(pgsql):
    identifier = PgAyatIdentifier(FkAsyncInt(1), pgsql)

    assert await identifier.ayat_id() == 1
    assert await identifier.sura_num() == 1
    assert await identifier.ayat_num() == '1-7'


async def test_not_found(pgsql):
    identifier = PgAyatIdentifier(FkAsyncInt(1), pgsql)

    with pytest.raises(AyatNotFoundError):
        await identifier.sura_num()
    with pytest.raises(AyatNotFoundError):
        await identifier.ayat_num()
