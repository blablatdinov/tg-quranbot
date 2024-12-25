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
