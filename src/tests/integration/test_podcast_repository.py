import pytest

from repository.podcast import PodcastRepository, Podcast


@pytest.fixture()
async def podcast(db_session):
    file_insert_query = """
        INSERT INTO files (file_id, telegram_file_id, created_at, link) VALUES ('561a3e46-1ef1-45f2-93ee-fb60e8dfc809', 'file_id', '2040-01-01', '/link')
    """
    await db_session.execute(file_insert_query)
    await db_session.execute("INSERT INTO podcasts (podcast_id, file_id) VALUES ('1908dba3-a679-4ec6-8881-0b03f5865f8d', '561a3e46-1ef1-45f2-93ee-fb60e8dfc809')")


async def test(db_session, podcast):
    got = await PodcastRepository(db_session).get_random()

    assert isinstance(got, Podcast)
