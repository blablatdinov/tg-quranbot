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
from urllib import parse as url_parse

import attrs
import httpx
import ujson
from pyeo import elegant

from app_types.logger import LogSink
from app_types.update import Update
from exceptions.internal_exceptions import TelegramIntegrationsError
from integrations.tg.sendable import Sendable
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True)
@elegant
class SendableAnswer(Sendable):
    """Объект, отправляющий ответы в API."""

    _answer: TgAnswer
    _logger: LogSink

    @override
    async def send(self, update: Update) -> list[dict]:
        """Отправка.

        :param update: Update
        :return: list[str]
        :raises TelegramIntegrationsError: при невалидном ответе от API телеграмма
        """
        responses = []
        success_status = 200
        async with httpx.AsyncClient(timeout=5) as client:
            for request in await self._answer.build(update):
                self._logger.debug('Try send request to: {0}'.format(
                    url_parse.unquote(str(request.url)),
                ))
                resp = await client.send(request)
                responses.append(resp.text)
                if resp.status_code != success_status:
                    raise TelegramIntegrationsError(resp.text)
            return [ujson.loads(response) for response in responses]
