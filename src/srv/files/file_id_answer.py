# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from furl import furl

from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer
from srv.files.tg_file import TgFile


@final
@attrs.define(frozen=True)
class TelegramFileIdAnswer(TgAnswer):
    """Класс ответа с файлом."""

    _origin: TgAnswer
    _tg_file: TgFile

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Отправка.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                request.method,
                furl(request.url).add({'audio': await self._tg_file.tg_file_id()}).url,
            )
            for request in await self._origin.build(update)
        ]
