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
from typing import final
import attrs

from integrations.tg.cached_tg_update import CachedTgUpdate
from app_types.fk_update import FkUpdate
from app_types.update import Update


@final
class _SeUpdate(Update):

    def __init__(self, origin: Update):
        self._origin = origin
        self._flag = False

    def __str__(self):
        if self._flag:
            raise Exception
        self._flag = True
        return str(self._origin)

    def asdict(self):
        if self._flag:
            raise Exception
        self._flag = True
        return self._origin.asdict()


def test_str():
    cd_update = CachedTgUpdate(
        _SeUpdate(
            FkUpdate.empty_ctor(),
        ),
    )
    assert str(cd_update) == str(cd_update)


def test_dict():
    cd_update = CachedTgUpdate(
        _SeUpdate(
            FkUpdate('{"key":"val"}'),
        ),
    )
    assert cd_update.asdict() == cd_update.asdict()