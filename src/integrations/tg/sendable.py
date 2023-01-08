"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import asyncio
import json
from typing import final
from typing import Protocol
from urllib import parse as url_parse

import httpx
from loguru import logger

from app_types.stringable import Stringable
from exceptions.internal_exceptions import TelegramIntegrationsError
from integrations.tg.tg_answers.interface import TgAnswerInterface


class SendableInterface(Protocol):
    """Интерфейс объекта, отправляющего ответы в API."""

    async def send(self, update) -> list[dict]:
        """Отправка.

        :param update: Stringable
        """


class SendableAnswer(SendableInterface):
    """Объект, отправляющий ответы в API."""

    def __init__(self, answer: TgAnswerInterface):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        """
        self._answer = answer

    async def send(self, update: Stringable) -> list[dict]:
        """Отправка.

        :param update: Stringable
        :return: list[str]
        :raises TelegramIntegrationsError: при невалидном ответе от API телеграмма
        """
        responses = []
        success_status = 200
        async with httpx.AsyncClient() as client:
            for request in await self._answer.build(update):
                logger.debug('Try send request to: {0}'.format(url_parse.unquote(str(request.url))))
                resp = await client.send(request)
                responses.append(resp.text)
                if resp.status_code != success_status:
                    raise TelegramIntegrationsError(resp.text)
            return [json.loads(response) for response in responses]


class UserNotSubscribedSafeSendable(SendableInterface):
    """Декоратор для обработки отписанных пользователей."""

    def __init__(self, sendable: SendableInterface):
        """Конструктор класса.

        :param sendable: SendableInterface
        """
        self._origin = sendable

    async def send(self, update) -> list[dict]:
        """Отправка.

        :param update: Stringable
        :return: list[dict]
        :raises TelegramIntegrationsError: если ошибка не связана с блокировкой бота
        """
        try:
            responses = await self._origin.send(update)
        except TelegramIntegrationsError as err:
            error_messages = [
                'chat not found',
                'bot was blocked by the user',
                'user is deactivated',
            ]
            for error_message in error_messages:
                if error_message not in str(err):
                    continue
                dict_response = json.loads(str(err))
                return [dict_response]
            raise err
        return responses


class SliceIterator(object):
    """Итератор по срезам массива."""

    def __init__(self, origin: list, slice_size: int):
        """Конструктор класса.

        :param origin: list
        :param slice_size: int
        """
        self._origin = origin
        self._slice_size = slice_size
        self._shift = 0

    def __iter__(self):
        """Точка входа в итератор.

        :return: SliceIterator
        """
        return self

    def __next__(self):
        """Вернуть следующий элемент итерации.

        :return: list
        :raises StopIteration: при конце итерации
        """
        if len(self._origin) <= self._shift:
            raise StopIteration
        res = self._origin[self._shift:self._shift + self._slice_size]
        self._shift += self._slice_size
        return res


class BulkSendableAnswer(SendableInterface):
    """Массовая отправка."""

    def __init__(self, answers: list[TgAnswerInterface]):
        """Конструктор класса.

        :param answers: list[TgAnswerInterface]
        """
        self._answers = answers

    async def send(self, update) -> list[dict]:
        """Отправка.

        :param update: Stringable
        :return: list[dict]
        """
        tasks = [
            UserNotSubscribedSafeSendable(
                SendableAnswer(answer),
            ).send(update)
            for answer in self._answers
        ]
        responses = []
        for sendable_slice in SliceIterator(tasks, 10):
            res_list = await asyncio.gather(*sendable_slice)
            for res in res_list:
                responses.append(res)
        return responses
