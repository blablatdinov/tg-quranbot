# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
