import abc
import time
from typing import TypeVar

import aiohttp
from pydantic import BaseModel
from loguru import logger

ParseModel = TypeVar('ParseModel', bound=BaseModel)


class IntegrationClientInterface(object):
    """Интерфейс HTTP клиента."""

    @abc.abstractmethod
    async def act(self, url: str, model_for_parse: type[ParseModel]) -> ParseModel:
        """Выполнить запрос.

        :param url: str
        :param model_for_parse: type(BaseModel)
        :raises NotImplementedError: if not implement
        """
        raise NotImplementedError


class IntegrationClient(IntegrationClientInterface):
    """Aiohttp клиент."""

    async def act(self, url: str, model_for_parse: type[ParseModel]) -> ParseModel:
        """Выполнить запрос.

        :param url: str
        :param model_for_parse: type(BaseModel)
        :returns: type(BaseModel)
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                text = await resp.text()

        return model_for_parse.parse_raw(text)


class LoggedIntegrationClient(IntegrationClientInterface):

    def __init__(self, integration_client: IntegrationClientInterface):
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
