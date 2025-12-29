# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import uuid

import pytest

from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat_id_by_public_id import AyatIdByPublicId
from srv.ayats.ayat_id_by_sura_ayat_num import AyatIdBySuraAyatNum
from srv.ayats.fk_search_query import FkSearchQuery

pytestmark = [pytest.mark.usefixtures('db_ayat')]


async def test_ayat_id_by_sura_ayat_num(pgsql):
    got = await AyatIdBySuraAyatNum(FkSearchQuery(1, '1'), pgsql).to_int()

    assert got == 1


async def test_ayat_id_by_sura_ayat_num_not_found(pgsql):
    with pytest.raises(AyatNotFoundError):
        await AyatIdBySuraAyatNum(FkSearchQuery(1, '15'), pgsql).to_int()


async def test_ayat_id_by_public_id(pgsql):
    got = await AyatIdByPublicId(uuid.UUID('3067bdc4-8dc0-456b-aa68-e38122b5f2f8'), pgsql).to_int()

    assert got == 1


async def test_ayat_id_by_public_id_not_found(pgsql):
    with pytest.raises(AyatNotFoundError):
        await AyatIdByPublicId(uuid.uuid4(), pgsql).to_int()
