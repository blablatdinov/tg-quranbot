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

import textwrap
from pathlib import Path

import pytest

from settings import BASE_DIR
from srv.ayats.fk_ayat import FkAyat
from srv.ayats.fk_identifier import FkIdentifier
from srv.ayats.text_len_shorten_ayat import TextLenSafeAyat
from srv.files.fk_file import FkFile


async def test_text_len_safe_ayat():
    ayat_content = Path(BASE_DIR / 'tests/fixtures/2_282_ayat_rendered.txt').read_text(encoding='utf-8').strip()
    got = await TextLenSafeAyat(
        FkAyat(
            FkIdentifier(272, 2, '282'),
            ayat_content,
            FkFile('', ''),
        ),
    ).to_str()

    assert got == textwrap.shorten(ayat_content, width=4096, placeholder='...')


# TODO #1095 Исправить обрезку, учитывать теги, убрать маркер skip
@pytest.mark.skip()
async def test_tags_closed():
    ayat_content = Path(BASE_DIR / 'tests/fixtures/2_282_ayat_rendered.txt').read_text(encoding='utf-8').strip()
    got = await TextLenSafeAyat(
        FkAyat(
            FkIdentifier(272, 2, '282'),
            ayat_content,
            FkFile('', ''),
        ),
    ).to_str()

    assert '</i>' in got
