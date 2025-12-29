# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import re

import pytest

from app_types.fk_update import FkUpdate
from integrations.tg.message_text import MessageText
from srv.prayers.parsed_date import ParsedDate


async def test_fail_format():
    error_text = re.escape(
        ' '.join([
            "time data 'invalid-date' does not match",
            "formats ('%d.%m.%Y', '%d-%m-%Y')",  # noqa: WPS323 not string formatting
        ]),
    )
    with pytest.raises(ValueError, match=error_text):
        await ParsedDate(
            MessageText(
                FkUpdate('{"message":{"text":"Время намаза invalid-date"}}'),
            ),
        ).date()
