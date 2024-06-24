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


import pytest

from app_types.intable import FkAsyncIntable
from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat_identifier import PgAyatIdentifier


@pytest.mark.usefixtures('_db_ayat')
async def test(pgsql):
    identifier = PgAyatIdentifier(FkAsyncIntable(1), pgsql)

    assert await identifier.ayat_id() == 1
    assert await identifier.sura_num() == 1
    assert await identifier.ayat_num() == '1-7'


async def test_not_found(pgsql):
    identifier = PgAyatIdentifier(FkAsyncIntable(1), pgsql)

    with pytest.raises(AyatNotFoundError):
        await identifier.sura_num()
    with pytest.raises(AyatNotFoundError):
        await identifier.ayat_num()
