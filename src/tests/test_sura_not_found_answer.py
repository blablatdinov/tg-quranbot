import httpx

from app_types.stringable import Stringable, ThroughStringable
from exceptions.content_exceptions import SuraNotFoundError
from integrations.tg.tg_answers import TgAnswerInterface
from services.ayats.sura_not_found_safe_answer import SuraNotFoundSafeAnswer


class ThroughDomainAnswer(TgAnswerInterface):

    def __init__(self, domain: str):
        self._domain = domain

    async def build(self, update: Stringable) -> list[httpx.Request]:
        return [httpx.Request('GET', self._domain)]


class SuraNotFoundAnswer(TgAnswerInterface):

    async def build(self, update):
        raise SuraNotFoundError


async def test_normal_flow():
    got = await SuraNotFoundSafeAnswer(
        ThroughDomainAnswer('https://normal.flow'),
        ThroughDomainAnswer('https://error.flow'),
    ).build(ThroughStringable(''))

    assert got[0].url == 'https://normal.flow'


async def test_error_flow():
    got = await SuraNotFoundSafeAnswer(
        SuraNotFoundAnswer(),
        ThroughDomainAnswer('https://error.flow'),
    ).build(ThroughStringable(''))

    assert 'error.flow' in str(got[0].url)
