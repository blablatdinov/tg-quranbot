# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from services.intable_regex import IntableRegex


@pytest.mark.parametrize(('input_', 'expected'), [
    ('8923749', 8923749),
    ('around483759text', 483759),
    ('5347split832457', 5347),
])
def test(input_, expected):
    got = IntableRegex(input_)

    assert int(got) == expected
