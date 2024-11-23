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

"""Generating default revive bot config."""

from typing import Protocol, final, override

import attrs

from main.services.revive_config.revive_config import ConfigDict, ReviveConfig


class HasRandint(Protocol):
    """Object has randint callable."""

    def randint(self, start: int, end: int) -> int:
        """Randint callable."""


@final
@attrs.define(frozen=True)
class DefaultReviveConfig(ReviveConfig):
    """Generating default revive bot config."""

    _rnd: HasRandint

    @override
    def parse(self) -> ConfigDict:
        """Generating default config."""
        return ConfigDict({
            'limit': 10,
            'cron': '{0} {1} {2} * *'.format(
                self._rnd.randint(0, 61),  # noqa: S311 . Not secure issue
                self._rnd.randint(0, 25),  # noqa: S311 . Not secure issue
                self._rnd.randint(0, 29),  # noqa: S311 . Not secure issue
            ),
            'glob': '**/*',
        })
