# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime

import pytest

from app_types.fk_update import FkUpdate
from srv.prayers.pagination_per_day_date import PaginationPerDayDate


@pytest.mark.parametrize('date', [
    datetime.date(2024, 9, 2),
    datetime.date(2023, 5, 20),
])
async def test(callback_update_factory, date):
    got = await PaginationPerDayDate().parse(
        FkUpdate(
            callback_update_factory(
                callback_data='pagPrDay({0})'.format(date.strftime('%Y-%m-%d')),
            ),
        ),
    )

    assert got == date
