# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import Any, final

import pytest

from exceptions.internal_exceptions import CityNotFoundError
from srv.prayers.fk_city import FkCity
from srv.prayers.hg_prayers_url import HgPrayersUrl


@final
# Class for testing only
class _FkDbConn:  # noqa: PEO200
    _link: str | None

    def __init__(self, link: str | None) -> None:
        self._link = link

    async def __aenter__(self) -> _FkDbConn:
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        pass

    async def execute(self, query: str, query_params: dict[str, Any] | None = None) -> _FkDbConn:  # noqa: ARG001
        return self

    def fetchone(self) -> tuple | None:
        if self._link is None:
            return None
        return (self._link,)


@final
# Class for testing only
class _FkDb:  # noqa: PEO200
    _link: str | None

    def __init__(self, link: str | None) -> None:
        self._link = link

    # Class used for test only
    def connect(self) -> _FkDbConn:  # noqa: OVR100
        return _FkDbConn(self._link)


@pytest.mark.parametrize(('month_num', 'month_name'), [
    (1, 'january'),
    (2, 'february'),
    (3, 'march'),
    (4, 'april'),
    (5, 'may'),
    (6, 'june'),
    (7, 'july'),
    (8, 'august'),
    (9, 'september'),
    (10, 'october'),
    (11, 'november'),
    (12, 'december'),
])
async def test_month_names(month_num, month_name):
    got = await HgPrayersUrl(
        FkCity.name_ctor('Innopolis'),
        _FkDb('https://halalguide.me/innopolis/namaz-time/'),  # type: ignore[arg-type]
        datetime.datetime(2025, month_num, 1, tzinfo=datetime.UTC).date(),
    ).to_str()

    assert got == 'https://halalguide.me/innopolis/namaz-time/{0}-2025'.format(month_name)


async def test_without_link():
    with pytest.raises(CityNotFoundError):
        await HgPrayersUrl(
            FkCity.name_ctor('Innopolis'),
            _FkDb(None),  # type: ignore[arg-type]
            datetime.datetime(2025, 1, 1, tzinfo=datetime.UTC).date(),
        ).to_str()
