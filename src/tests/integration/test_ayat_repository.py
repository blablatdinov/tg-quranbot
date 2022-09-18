import pytest

from repository.ayats.ayat import AyatRepository
from repository.ayats.schemas import Ayat
from tests.factories.file_factory import factory


@pytest.fixture()
async def ayat(db_session, mixer):
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
                'content': 'content',
                'arab_text': 'arab text',
                'transliteration': 'transliteration',
                'audio_id': str(await factory(db_session)),
            },
            {
                'ayat_id': 2,
                'public_id': '96710161-75ab-483f-a9bb-e4d86e068936',
                'sura_id': 1,
                'ayat_number': '2',
                'content': 'content',
                'arab_text': 'arab text',
                'transliteration': 'transliteration',
                'audio_id': str(await factory(db_session)),
            },
        ],
    )


async def test_get(db_session, ayat):
    got = await AyatRepository(db_session).get(1)

    assert isinstance(got, Ayat)


async def test_get_ayats_by_sura_num(db_session, ayat):
    got = await AyatRepository(db_session).get_ayats_by_sura_num(1)

    assert isinstance(got, list)
    assert len(got) == 2
    assert isinstance(got[0], Ayat)


async def test_search_ayats_by_content(db_session, ayat):
    got = await AyatRepository(db_session).search_by_text('content')

    assert isinstance(got, list)
    assert len(got) == 2
    assert isinstance(got[0], Ayat)
