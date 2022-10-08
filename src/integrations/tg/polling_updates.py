import json

import httpx

from app_types.intable import Intable
from app_types.stringable import Stringable
from integrations.tg.tg_answers.update import Update


class UpdatesTimeout(Intable):
    """Таймаут для обновлений."""

    def __int__(self):
        """Числовое представление.

        :return: int
        """
        return 5


class UpdatesURLInterface(object):
    """Интерфейс URL запроса для получения уведомлений."""

    def generate(self, update_id: int) -> str:
        """Генерация.

        :param update_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class UpdatesURL(Stringable):
    """Базовый URL обновлений из телеграма."""

    def __init__(self, token: str):
        self._token = token

    def __str__(self):
        """Строчное представление.

        :return: str
        """
        return 'https://api.telegram.org/bot{0}/getUpdates'.format(self._token)


class UpdatesWithOffsetURL(UpdatesURLInterface):
    """URL для получения только новых обновлений."""

    def __init__(self, updates_url: Stringable):
        self._updates_url = updates_url

    def generate(self, update_id: int):
        """Генерация.

        :param update_id: int
        :return: str
        """
        return '{0}?offset={1}'.format(self._updates_url, update_id)


class UpdatesLongPollingURL(UpdatesURLInterface):
    """URL обновлений с таймаутом."""

    def __init__(self, updates_url: UpdatesURLInterface, long_polling_timeout: Intable):
        self._origin = updates_url
        self._long_polling_timeout = long_polling_timeout

    def generate(self, update_id: int):
        """Генерация.

        :param update_id: int
        :return: str
        """
        return httpx.URL(self._origin.generate(update_id)).copy_add_param(
            'timeout',
            int(self._long_polling_timeout),
        )


class UpdatesIteratorInterface(object):
    """Интерфейс итератора по обновлениям."""

    def __aiter__(self):
        """Точка входа в итератор.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def __anext__(self) -> list[str]:
        """Вернуть следующий элемент.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class PollingUpdatesIterator(UpdatesIteratorInterface):
    """Итератор по обновлениям."""

    def __init__(self, updates_url: UpdatesURLInterface, updates_timeout: Intable):
        self._updates_url = updates_url
        self._offset = 0
        self._updates_timeout = updates_timeout

    def __aiter__(self):
        """Точка входа в итератор.

        :return: PollingUpdatesIterator
        """
        return self

    async def __anext__(self) -> list[str]:
        """Вернуть следующий элемент.

        :return: list[Update]
        """
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    self._updates_url.generate(self._offset),
                    timeout=int(self._updates_timeout),
                )
            except httpx.ReadTimeout:
                return []
            resp_content = resp.text
            parsed_result = json.loads(resp_content)['result']
            if not parsed_result:
                return []
            self._offset = parsed_result[-1]['update_id'] + 1
            return [json.dumps(elem, ensure_ascii=False) for elem in parsed_result]
