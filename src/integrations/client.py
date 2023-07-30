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
from pyeo import elegant
import time
from typing import Protocol, TypeVar, final

import attrs
import httpx
from loguru import logger
from pydantic import BaseModel

ParseModel = TypeVar('ParseModel', bound=BaseModel)


@elegant
class IntegrationClientInterface(Protocol):
    """Интерфейс HTTP клиента."""

    async def act(self, url: str, model_for_parse: type[ParseModel]) -> ParseModel:
        """Выполнить запрос.

        :param url: str
        :param model_for_parse: type(BaseModel)
        """


@final
@attrs.define(frozen=True)
@elegant
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


@final
@attrs.define(frozen=True)
@elegant
class LoggedIntegrationClient(IntegrationClientInterface):
    """Декоратор логирующий http запрос."""

    _origin: IntegrationClientInterface

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
