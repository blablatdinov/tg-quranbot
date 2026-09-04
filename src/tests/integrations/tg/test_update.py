# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

from frozendict import frozendict

from app_types.update import Update
from integrations.tg.cached_tg_update import CachedTgUpdate


@final
# Class for testing
class SeUpdate(Update):  # noqa: PEO200

    def __init__(self) -> None:
        self._str_call_count = 0
        self._asdict_call_count = 0

    @override
    def __str__(self) -> str:
        if self._str_call_count == 0:
            self._str_call_count += 1
            return 'value'
        raise Exception  # noqa: TRY002, WPS454

    @override
    def asdict(self) -> frozendict:
        if self._asdict_call_count == 0:
            self._asdict_call_count += 1
            return frozendict({'key': 'value'})
        raise Exception  # noqa: TRY002, WPS454


def test():
    update = CachedTgUpdate(SeUpdate())

    assert str(update) == 'value'
    assert str(update) == 'value'
    assert update.asdict() == frozendict({'key': 'value'})
    assert update.asdict() == frozendict({'key': 'value'})
