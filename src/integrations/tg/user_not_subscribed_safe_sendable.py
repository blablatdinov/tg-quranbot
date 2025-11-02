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
import ujson

from app_types.update import Update
from exceptions.internal_exceptions import TelegramIntegrationsError
from integrations.tg.sendable import Sendable


@final
@attrs.define(frozen=True)
class UserNotSubscribedSafeSendable(Sendable):
    """Декоратор для обработки отписанных пользователей."""

    _origin: Sendable

    @override
    async def send(self, update: Update) -> list[dict]:
        """Отправка.

        :param update: Update
        :return: list[dict]
        :raises TelegramIntegrationsError: если ошибка не связана с блокировкой бота
        """
        try:
            responses = await self._origin.send(update)
        except TelegramIntegrationsError as err:
            error_messages = {
                'chat not found',
                'bot was blocked by the user',
                'user is deactivated',
            }
            for error_message in error_messages:
                if error_message not in str(err):
                    continue
                dict_response = ujson.loads(str(err))
                return [dict_response]
            raise TelegramIntegrationsError(str(err)) from err
        return responses
