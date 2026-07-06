# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

from app_types.counter import Counter
from app_types.fk_update import FkUpdate
from integrations.tg.tg_answers.fk_answer import FkAnswer
from metrics.measured_answer import MeasuredAnswer


@final
class FkCounter(Counter):  # noqa: PEO200

    def __init__(self) -> None:
        self._counter_val = 0

    @override
    def inc(self) -> None:
        self._counter_val += 1

    def get(self) -> int:  # noqa: PEO601, OVR100
        return self._counter_val


async def test():
    cnt = FkCounter()
    await MeasuredAnswer(FkAnswer(), cnt).build(FkUpdate.empty_ctor())

    assert cnt.get() == 1
