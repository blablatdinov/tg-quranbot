from services.podcast import PodcastAnswer
from tests.mocks.bot import BotMock
from tests.mocks.podcast_repository import PodcastRepositoryMock


async def test():
    got = await PodcastAnswer(
        debug_mode=False,
        chat_id=38294723,
        bot=BotMock(),
        podcast_repository=PodcastRepositoryMock(),
    ).send()

    assert isinstance(got, list)
    assert got[0].audio.file_id == 'file_id'


async def test_debug():
    got = await PodcastAnswer(
        debug_mode=True,
        chat_id=38294723,
        bot=BotMock(),
        podcast_repository=PodcastRepositoryMock(),
    ).send()

    assert got[0].text == 'https://link.to.file'
