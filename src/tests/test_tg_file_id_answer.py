import httpx

from app_types.stringable import Stringable
from integrations.tg.tg_answers import TgAnswerInterface
from services.answers.answer import TelegramFileIdAnswer


class FakeAnswer(TgAnswerInterface):

    async def build(self, update):
        return [
            httpx.Request('GET', 'https://some.domain'),
        ]


class FakeString(Stringable):

    def __str__(self):
        return ''


async def test():
    got = await TelegramFileIdAnswer(FakeAnswer(), 'file_id').build(FakeString())

    assert got[0].url.query.decode('utf-8') == 'audio=file_id'
