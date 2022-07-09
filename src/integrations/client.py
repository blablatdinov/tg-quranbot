import abc

import aiohttp
from pydantic import BaseModel


class IntegrationClientInterface(object):

    @abc.abstractmethod
    async def act(self, url: str, model_for_parse: type(BaseModel)) -> type(BaseModel):
        raise NotImplementedError


class IntegrationClient(IntegrationClientInterface):

    async def act(self, url: str, model_for_parse: type(BaseModel)) -> type(BaseModel):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                print(resp.status)
                text = await resp.text()
                print(text)

        return model_for_parse.parse_raw(text)
