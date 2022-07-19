from services.answers.answer import Answer
from services.podcast import PodcastAnswer
from tests.mocks.podcast_repository import PodcastRepositoryMock


async def test():
    got = await PodcastAnswer(
        PodcastRepositoryMock(),
    ).to_answer()

    assert isinstance(got, Answer)
    assert got.telegram_file_id == 'file_id'
    assert got.link_to_file == 'https://link.to.file'
