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

from exceptions.content_exceptions import AyatNotFoundError, SuraNotFoundError
from srv.ayats.fk_search_query import FkSearchQuery
from srv.ayats.validated_search_query import ValidatedSearchQuery


def test():
    query = ValidatedSearchQuery(FkSearchQuery(1, '1'))

    assert query.sura() == 1
    assert query.ayat() == '1'


@pytest.mark.parametrize('sura_id', [-1, 115])
def test_fail_sura(sura_id):
    query = ValidatedSearchQuery(FkSearchQuery(sura_id, '1'))
    with pytest.raises(SuraNotFoundError):
        query.sura()


@pytest.mark.parametrize('ayat_num', [
    '0',
    '1iw',
    '1,5',
    '1-5',
])
def test_fail(ayat_num):
    query = ValidatedSearchQuery(FkSearchQuery(1, ayat_num))
    with pytest.raises(AyatNotFoundError):
        query.ayat()
