from services.answer import Answer
from services.podcast import PodcastAnswer, PodcastService
from tests.mocks.podcast_repository import PodcastRepositoryMock


async def test():
    got = PodcastAnswer(
        await PodcastService(
            PodcastRepositoryMock(),
        ).get_random(),
    ).transform()

    assert isinstance(got, Answer)
    assert got.telegram_file_id == 'file_id'
    assert got.link_to_file == 'https://link.to.file'
