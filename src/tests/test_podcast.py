from services.podcast import PodcastAnswer
from tests.mocks.bot import BotMock
from tests.mocks.podcast_repository import PodcastRepositoryMock


async def test():
    got = await PodcastAnswer(
        False,
        38294723,
        BotMock(),
        PodcastRepositoryMock(),
    ).send()

    assert isinstance(got, list)
    assert got[0].audio.file_id == 'file_id'


async def test_debug():
    got = await PodcastAnswer(
        True,
        38294723,
        BotMock(),
        PodcastRepositoryMock(),
    ).send()

    assert got[0].text == 'https://link.to.file'
