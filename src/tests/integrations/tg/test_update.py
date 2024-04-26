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
from typing import final, override

from app_types.update import Update
from integrations.tg.update import CachedTgUpdate


@final
class SeUpdate(Update):

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
    def asdict(self) -> dict:
        if self._asdict_call_count == 0:
            self._asdict_call_count += 1
            return {'key': 'value'}
        raise Exception  # noqa: TRY002, WPS454


def test():
    update = CachedTgUpdate(SeUpdate())

    assert str(update) == 'value'
    assert str(update) == 'value'
    assert update.asdict() == {'key': 'value'}
    assert update.asdict() == {'key': 'value'}
