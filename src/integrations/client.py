import time
from typing import Protocol, TypeVar

import httpx
from loguru import logger
from pydantic import BaseModel

ParseModel = TypeVar('ParseModel', bound=BaseModel)


class IntegrationClientInterface(Protocol):
    """Интерфейс HTTP клиента."""

    async def act(self, url: str, model_for_parse: type[ParseModel]) -> ParseModel:
        """Выполнить запрос.

        :param url: str
        :param model_for_parse: type(BaseModel)
        """


class IntegrationClient(IntegrationClientInterface):
    """Httpx клиент."""

    async def act(self, url: str, model_for_parse: type[ParseModel]) -> ParseModel:
        """Выполнить запрос.

        :param url: str
        :param model_for_parse: type(BaseModel)
        :returns: type(BaseModel)
        """
        async with httpx.AsyncClient() as session:
            response = await session.get(url)
            text = response.text
        return model_for_parse.parse_raw(text)


class LoggedIntegrationClient(IntegrationClientInterface):
    """Декоратор логирующий http запрос."""

    def __init__(self, integration_client: IntegrationClientInterface):
        """Конструктор класса.

        :param integration_client: IntegrationClientInterface
        """
        self._origin = integration_client

    async def act(self, url: str, model_for_parse: type[ParseModel]) -> ParseModel:
        """Выполнить запрос.

        :param url: str
        :param model_for_parse: type(BaseModel)
        :returns: type(BaseModel)
        """
        logger.info('Try make request to {0}...'.format(url))
        start_time = time.time()
        request_result = await self._origin.act(url, model_for_parse)
        logger.info('Request to {0} end successful: time: {1} s'.format(url, time.time() - start_time))
        return request_result
