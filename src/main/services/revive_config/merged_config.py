# The MIT License (MIT).
#
# Copyright (c) 2023-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

"""Merged Config."""

from collections.abc import Iterable
from typing import final

import attrs

from main.services.revive_config.revive_config import ConfigDict, ReviveConfig


@final
@attrs.define(frozen=True)
class MergedConfig(ReviveConfig):
    """Merged Config."""

    _origins: Iterable[ReviveConfig]

    @classmethod
    def ctor(cls, *origins: ReviveConfig) -> ReviveConfig:
        """Ctor."""
        return cls(origins)

    def parse(self) -> ConfigDict:
        """Merge configs."""
        result_config = ConfigDict({'limit': 0, 'cron': '', 'glob': ''})
        for config in self._origins:
            result_config |= config.parse()
        return result_config
