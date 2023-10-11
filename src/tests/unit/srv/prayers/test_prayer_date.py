"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import datetime
import re

import pytest

from srv.prayers.prayer_date import PrayersRequestDate


def test(freezer):
    freezer.move_to('2023-10-11')
    got = PrayersRequestDate().parse('Время намаза')

    assert got == datetime.date(2023, 10, 11)


@pytest.mark.parametrize(('query', 'expected'), [
    ('Время намаза 10.10.2023', datetime.date(2023, 10, 10)),
    ('Время намаза 15-10-2023', datetime.date(2023, 10, 15)),
])
def test_with_date(query, expected):
    got = PrayersRequestDate().parse(query)

    assert got == expected


def test_fail_format():
    error_text = re.escape(
        ' '.join([
            "time data 'invalid-date' does not match",
            "formats ('%d.%m.%Y', '%d-%m-%Y')",  # noqa: WPS323 not string formatting
        ]),
    )
    with pytest.raises(ValueError, match=error_text):
        PrayersRequestDate().parse('Время намаза invalid-date')