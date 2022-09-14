import json

import httpx
from loguru import logger

from exceptions.internal_exceptions import TelegramIntegrationsError
from integrations.tg.tg_answers.interface import TgAnswerInterface


class SendableInterface(object):
    """Интерфейс объекта, отправляющего ответы в API."""

    async def send(self, update):
        """Отправка.

        :param update: Update
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class SendableAnswer(SendableInterface):
    """Объект, отправляющий ответы в API."""

    def __init__(self, answer: TgAnswerInterface):
        self._answer = answer

    async def send(self, update) -> list[str]:
        """Отправка.

        :param update: Update
        :return: list[str]
        :raises TelegramIntegrationsError: при невалидном ответе от API телеграмма
        """
        responses = []
        success_status = 200
        async with httpx.AsyncClient() as client:
            for request in await self._answer.build(update):
                logger.debug('Try send request to: {0}'.format(request.url))
                resp = await client.send(request)
                responses.append(resp.text)
                if resp.status_code != success_status:
                    if 'new message content and reply markup are exactly' in resp.json()['description']:
                        return []
                    raise TelegramIntegrationsError(resp.text)
            return [json.loads(response) for response in responses]
