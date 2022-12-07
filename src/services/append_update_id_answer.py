import datetime

import httpx

from integrations.tg.tg_answers import TgAnswerInterface
from integrations.tg.tg_answers.update import Update


class DebugParamInterface(object):
    """Интерфейс отладочной информации."""

    async def debug_value(self, update) -> str:
        """Значение отладочной информации.

        :param update: Update
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class AppendDebugInfoAnswer(TgAnswerInterface):
    """Ответ с отладочной информацией."""

    def __init__(self, debug_mode: bool, answer: TgAnswerInterface, *debug_params: DebugParamInterface):
        self._debug = debug_mode
        self._origin = answer
        self._debug_params = debug_params

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        origin_requests = await self._origin.build(update)
        if not self._debug:
            return origin_requests
        return self._build_new_requests(
            origin_requests,
            [
                await debug_param.debug_value(update)
                for debug_param in self._debug_params
            ],
        )

    def _build_new_requests(self, origin_requests: list[httpx.Request], debug_params: list[str]):
        debug_str = '\n\n!----- DEBUG INFO -----!\n\n{0}\n\n!----- END DEBUG INFO -----!'.format(
            '\n'.join(debug_params),
        )
        new_requests = []
        for request in origin_requests:
            if 'sendMessage' in str(request.url):
                text = request.url.params['text']
                new_requests.append(httpx.Request(
                    method=request.method,
                    url=request.url.copy_set_param(
                        'text',
                        '{0}{1}'.format(text, debug_str),
                    ),
                    headers=request.headers,
                ))
            else:
                new_requests.append(request)
        return new_requests


class UpdateIdDebugParam(DebugParamInterface):
    """Отладочная информация с идентификатором обновления."""

    async def debug_value(self, update: Update) -> str:
        """Идентификатор обновления.

        :param update: Update
        :return: str
        """
        return 'Update id: {0}'.format(update.update_id)


class TimeDebugParam(DebugParamInterface):
    """Отладочная информация с временем."""

    async def debug_value(self, update: Update) -> str:
        """Время.

        :param update: Update
        :return: str
        """
        return 'Time: {0}'.format(datetime.datetime.now())


class ChatIdDebugParam(DebugParamInterface):
    """Отладочная информация с идентификатором чата."""

    async def debug_value(self, update: Update) -> str:
        """Идентификатор чата.

        :param update: Update
        :return: str
        """
        return 'Chat id: {0}'.format(update.chat_id())


class CommitHashDebugParam(DebugParamInterface):
    """Отладочная информация с хэшом коммита."""

    def __init__(self, commit_hash: str):
        self._commit_hash = commit_hash

    async def debug_value(self, update: Update) -> str:
        """Хэш коммита.

        :param update: Update
        :return: str
        """
        return 'Commit hash: {0}'.format(self._commit_hash)
