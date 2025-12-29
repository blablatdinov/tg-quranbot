# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime

import pytest
import ujson

from app_types.fk_update import FkUpdate
from srv.prayers.prayers_request_date import PrayersRequestDate


async def test(time_machine):
    time_machine.move_to('2023-10-11')
    got = await PrayersRequestDate().parse(FkUpdate('{"message":{"text":"Время намаза"}}'))

    assert got == datetime.date(2023, 10, 11)


@pytest.mark.parametrize(('query', 'expected'), [
    ('Время намаза 10.10.2023', datetime.date(2023, 10, 10)),
    ('Время намаза 15-10-2023', datetime.date(2023, 10, 15)),
])
async def test_with_date(query, expected):
    got = await PrayersRequestDate().parse(FkUpdate(
        ujson.dumps({'message': {'text': query}}),
    ))

    assert got == expected
