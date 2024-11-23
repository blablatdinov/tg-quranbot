# The MIT License (MIT).
#
# Copyright (c) 2023-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

import random
from typing import Self, final

import attrs
import pytest

from main.services.revive_config.default_revive_config import DefaultReviveConfig
from main.services.revive_config.gh_revive_config import GhReviveConfig

pytestmark = [pytest.mark.django_db]


@final
@attrs.define(frozen=True)
class FkContent:

    decoded_content: bytes

    @classmethod
    def str_ctor(cls, str_input: str) -> Self:
        return cls(str_input.encode('utf-8'))


@final
@attrs.define(frozen=True)
class FkRepo:

    _origin: str

    def get_contents(self, filepath: str) -> FkContent:
        return FkContent.str_ctor(self._origin)


def test() -> None:
    got = GhReviveConfig(
        # Too hard create Protocol for github.Repository.Repository
        FkRepo(  # type: ignore [arg-type]
            '\n'.join([
                'cron: 3 4 * * *',
            ]),
        ),
        DefaultReviveConfig(random.Random(0)),  # noqa: S311. Not secure issue
    ).parse()

    assert got == {'cron': '3 4 * * *', 'glob': '**/*', 'limit': 10}
