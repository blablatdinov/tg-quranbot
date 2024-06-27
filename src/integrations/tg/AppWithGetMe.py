from app_types.logger import LogSink
from app_types.runable import Runable
from exceptions.base_exception import InternalBotError


import attrs
import httpx


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
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
        async with httpx.AsyncClient() as client:
            response = await client.get('https://api.telegram.org/bot{0}/getMe'.format(self._token))
            if response.status_code != httpx.codes.OK:
                raise InternalBotError(response.text)
            self._logger.info(response.content)
        await self._origin.run()