from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from integrations.client import IntegrationClientInterface

ParseModel = TypeVar('ParseModel', bound=BaseModel)


class IntegrationClientMock(IntegrationClientInterface):

    def __init__(self, path_to_fixture: Path):
        self._path_to_fixture = path_to_fixture

    async def act(self, url: str, model_for_parse: type[ParseModel]) -> ParseModel:
        with open(self._path_to_fixture, 'r') as response_fixture_file:
            return model_for_parse.parse_raw(response_fixture_file.read())
