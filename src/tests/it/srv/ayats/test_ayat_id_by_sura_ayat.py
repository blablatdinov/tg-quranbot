# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import uuid

import pytest

from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat_id_by_sura_ayat import AyatIdByPublicId, AyatIdBySuraAyatNum
from srv.ayats.search_query import FkSearchQuery

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
