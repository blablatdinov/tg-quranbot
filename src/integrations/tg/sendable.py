import asyncio
import json
from urllib import parse as url_parse

import httpx
from loguru import logger

from exceptions.internal_exceptions import TelegramIntegrationsError
from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.update import Update


class SendableInterface(object):
    """Интерфейс объекта, отправляющего ответы в API."""

    async def send(self, update) -> list[dict]:
        """Отправка.

        :param update: Stringable
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class SendableAnswer(SendableInterface):
    """Объект, отправляющий ответы в API."""

    def __init__(self, answer: TgAnswerInterface):
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
                    raise TelegramIntegrationsError(resp.text, int(request.url.params['chat_id']))
            return [json.loads(response) for response in responses]


class UserNotSubscribedSafeSendable(SendableInterface):
    """Декоратор для обработки отписанных пользователей."""

    def __init__(self, sendable: SendableInterface):
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
                dict_response['chat_id'] = err.chat_id()
                return [dict_response]
            raise err
        return responses


class SliceIterator(object):
    """Итератор по срезам массива."""

    def __init__(self, origin: list, slize_size: int):
        self._origin = origin
        self._slice_size = slize_size
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
