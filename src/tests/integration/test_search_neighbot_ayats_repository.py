import pytest

from repository.ayats.neighbor_ayats import AyatShort, TextSearchNeighborAyatsRepository


@pytest.fixture()
async def ayats(db_session):
    await db_session.execute("INSERT INTO suras (sura_id, link) VALUES (1, '/hello')")
    insert_file_query = """
        INSERT INTO files
        (file_id, telegram_file_id, created_at, link)
        VALUES
        ('8f6e2fa5-1a26-4e7a-bd58-7597385121fa', 'file_id', '2030-01-03', 'file/link')
    """
    await db_session.execute(insert_file_query)
    ayats_insert_query = """
        INSERT INTO ayats
        (ayat_id, public_id, sura_id, day, ayat_number, content, arab_text, transliteration, audio_id)
        VALUES
        (:ayat_id, :public_id, :sura_id, :day, :ayat_number, :content, :arab_text, :transliteration, :audio_id)
        """
    await db_session.execute_many(
        ayats_insert_query,
        [
            {
                'ayat_id': 1,
                'public_id': '96710161-75ab-483f-a9bb-e4d86e068936',
                'sura_id': 1,
                'day': 1,
                'ayat_number': '1',
                'content': 'first ayat content',
                'arab_text': 'arab text',
                'transliteration': 'transliteration',
                'audio_id': '8f6e2fa5-1a26-4e7a-bd58-7597385121fa',
            },
            {
                'ayat_id': 2,
                'public_id': '96710161-75ab-483f-a9bb-e4d86e068936',
                'sura_id': 1,
                'day': 2,
                'ayat_number': '2',
                'content': 'second ayat content',
                'arab_text': 'arab text',
                'transliteration': 'transliteration',
                'audio_id': '8f6e2fa5-1a26-4e7a-bd58-7597385121fa',
            },
        ],
    )
    return [1, 2]


async def test(db_session, ayats):
    got = await TextSearchNeighborAyatsRepository(db_session, 'content').get_ayat_neighbors(1)

    assert isinstance(got, list)
    assert len(got) == 2
    assert isinstance(got[0], AyatShort)
