# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final

from app_types.fk_update import FkUpdate
from app_types.update import Update
from integrations.tg.cached_tg_update import CachedTgUpdate


@final
# object with side effect for testing
class _SeUpdate(Update):  # noqa: PEO200

    def __init__(self, origin: Update):
        self._origin = origin
        self._flag = False

    def __str__(self):
        if self._flag:
            # Exception for test
            raise Exception  # noqa: TRY002
        self._flag = True
        return str(self._origin)

    def asdict(self):
        if self._flag:
            # Exception for test
            raise Exception  # noqa: TRY002
        self._flag = True
        return self._origin.asdict()


def test_str():
    cd_update = CachedTgUpdate(
        _SeUpdate(
            FkUpdate.empty_ctor(),
        ),
    )
    init_val = str(cd_update)
    cached_val = str(cd_update)
    assert init_val == cached_val


def test_dict():
    cd_update = CachedTgUpdate(
        _SeUpdate(
            FkUpdate('{"key":"val"}'),
        ),
    )
    init_val = cd_update.asdict()
    cached_val = cd_update.asdict()
    assert init_val == cached_val
