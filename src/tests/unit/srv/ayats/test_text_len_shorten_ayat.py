# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from pathlib import Path

from settings import BASE_DIR
from srv.ayats.fk_ayat import FkAyat
from srv.ayats.fk_identifier import FkIdentifier
from srv.ayats.text_len_shorten_ayat import TextLenSafeAyat
from srv.files.fk_file import FkFile


async def test_text_len_safe_ayat():
    ayat_content = Path(  # noqa: ASYNC240
        BASE_DIR / 'tests/fixtures/2_282_ayat_rendered.txt',
    ).read_text(encoding='utf-8').strip()
    got = await TextLenSafeAyat(
        FkAyat(
            FkIdentifier(272, 2, '282'),
            ayat_content,
            FkFile.empty_ctor(),
        ),
    ).to_str()

    assert len(got) <= 4096
    assert got == Path(  # noqa: ASYNC240
        BASE_DIR / 'tests/fixtures/2_282_ayat_shorten.txt',
    ).read_text(encoding='utf-8').strip()
    assert '</i>' in got
