import pytest

from repository.ayats.neighbor_ayats import TextSearchNeighborAyatsRepository
from repository.ayats.schemas import AyatShort
from tests.factories.file_factory import factory


@pytest.fixture()
async def ayats(db_session):
    await db_session.execute("INSERT INTO suras (sura_id, link) VALUES (1, '/hello')")
    ayats_insert_query = """
        INSERT INTO ayats
        (ayat_id, public_id, sura_id, ayat_number, content, arab_text, transliteration, audio_id)
        VALUES
        (:ayat_id, :public_id, :sura_id, :ayat_number, :content, :arab_text, :transliteration, :audio_id)
        """
    await db_session.execute_many(
        ayats_insert_query,
        [
            {
                'ayat_id': 1,
                'public_id': '96710161-75ab-483f-a9bb-e4d86e068936',
                'sura_id': 1,
                'ayat_number': '1',
                'content': 'first ayat content',
                'arab_text': 'arab text',
                'transliteration': 'transliteration',
                'audio_id': str(await factory(db_session)),
            },
            {
                'ayat_id': 2,
                'public_id': '96710161-75ab-483f-a9bb-e4d86e068936',
                'sura_id': 1,
                'ayat_number': '2',
                'content': 'second ayat content',
                'arab_text': 'arab text',
                'transliteration': 'transliteration',
                'audio_id': str(await factory(db_session)),
            },
        ],
    )
    return [1, 2]


async def test(db_session, ayats):
    got = await TextSearchNeighborAyatsRepository(db_session, 'content').get_ayat_neighbors(1)

    assert isinstance(got, list)
    assert len(got) == 2
    assert isinstance(got[0], AyatShort)
