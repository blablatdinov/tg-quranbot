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

import re

import pytest

from main.exceptions import InvalidaCronError
from main.services.revive_config.str_config import StrReviveConfig


def test() -> None:
    got = StrReviveConfig('\n'.join([
        'limit: 10',
    ])).parse()

    # TODO: StrReviveConfig.parse return not valid ConfigDict
    assert got == {'limit': 10}  # type: ignore [comparison-overlap]


def test_invalid_cron() -> None:
    cron_expr = '*/61 * * * *'
    with pytest.raises(
        InvalidaCronError,
        match=re.escape('Cron expression: "{0}" has invalid format'.format(cron_expr)),
    ):
        StrReviveConfig('\n'.join([
            "cron: '{0}'".format(cron_expr),
        ])).parse()
