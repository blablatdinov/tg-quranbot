# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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
from hypothesis import example, given, strategies

from exceptions.content_exceptions import AyatNotFoundError, SuraNotFoundError
from srv.ayats.fk_search_query import FkSearchQuery
from srv.ayats.validated_search_query import ValidatedSearchQuery


def _sura_num_valid(sura_id):
    num_greater = sura_id > 0
    return num_greater and sura_id < 115


def _sura_num_invalid(num):
    return num < 1 or num > 114


def _ayat_num_invalid(ayat_num):
    try:
        int(ayat_num)
    except ValueError:
        return True
    return ayat_num.isdigit() and int(ayat_num) < 1


@given(
    strategies.integers().filter(_sura_num_valid),
    strategies.integers().filter(lambda ayat_num: ayat_num > 0),
)
@example(1, '1')
@example(114, '1')
def test(sura_id, ayat_num):
    query = ValidatedSearchQuery(FkSearchQuery(sura_id, str(ayat_num)))

    assert query.sura() == sura_id
    assert query.ayat() == str(ayat_num)


@given(strategies.integers().filter(_sura_num_invalid))
@example(0)
@example(-1)
@example(115)
def test_fail_sura(sura_id):
    query = ValidatedSearchQuery(FkSearchQuery(sura_id, '1'))
    with pytest.raises(SuraNotFoundError):
        query.sura()


@given(
    strategies.text().filter(lambda ayat_num: not ayat_num.isdigit())
    | strategies.text().filter(_ayat_num_invalid),
)
@example('0')
@example('1iw')
@example('1,5')
@example('1-5')
@example('²')
def test_fail(ayat_num):  # noqa: WPS216. hypothesis examples
    query = ValidatedSearchQuery(FkSearchQuery(1, ayat_num))
    with pytest.raises(AyatNotFoundError):
        query.ayat()
