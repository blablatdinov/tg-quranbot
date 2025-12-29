# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override
from urllib import parse as url_parse

import attrs
import httpx
import ujson

from app_types.logger import LogSink
from app_types.update import Update
from exceptions.internal_exceptions import TelegramIntegrationsError
from integrations.tg.sendable import Sendable
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True)
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
