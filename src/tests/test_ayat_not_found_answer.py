import httpx
import pytest

from app_types.stringable import ThroughStringable
from exceptions.content_exceptions import AyatNotFoundError
from integrations.tg.tg_answers import FkAnswer, TgAnswerInterface
from services.ayats.ayat_not_found_safe_answer import AyatNotFoundSafeAnswer


class ThroughDomainAnswer(TgAnswerInterface):

    def __init__(self, domain):
        self._domain = domain

    async def build(self, update):
        return [httpx.Request('GET', self._domain)]


class AyatNotFoundAnswer(TgAnswerInterface):

    async def build(self, update):
        raise AyatNotFoundError


async def test_normal_flow():
    got = await AyatNotFoundSafeAnswer(
        ThroughDomainAnswer('https://normal.flow'),
        ThroughDomainAnswer('https://error.flow'),
    ).build(ThroughStringable(''))

    assert got[0].url == 'https://normal.flow'


async def test_error_flow():
    got = await AyatNotFoundSafeAnswer(
        AyatNotFoundAnswer(),
        ThroughDomainAnswer('https://error.flow'),
    ).build(ThroughStringable(''))

    assert 'error.flow' in str(got[0].url)
