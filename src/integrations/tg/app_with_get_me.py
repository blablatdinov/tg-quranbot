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

from typing import final, override

import attrs
import httpx

from app_types.logger import LogSink
from app_types.runable import Runable
from exceptions.base_exception import InternalBotError


@final
@attrs.define(frozen=True)
class AppWithGetMe(Runable):
    """Объект для запуска с предварительным запросом getMe."""

    _origin: Runable
    _token: str
    _logger: LogSink

    @override
    async def run(self) -> None:
        """Запуск.

        :raises InternalBotError: в случае не успешного запроса к getMe
        """
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get('https://api.telegram.org/bot{0}/getMe'.format(self._token))
            if response.status_code != httpx.codes.OK:
                raise InternalBotError(response.text)
            self._logger.info(response.content)
        await self._origin.run()
