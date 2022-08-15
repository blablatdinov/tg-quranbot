import pytest

from repository.ayats.ayat import AyatRepository, Ayat


@pytest.fixture()
async def ayat(db_session, mixer):
    await db_session.execute("INSERT INTO suras (sura_id, link) VALUES (1, '/hello')")
    await db_session.execute("""
        INSERT INTO files 
        (file_id, telegram_file_id, created_at, link)
        VALUES
        ('8f6e2fa5-1a26-4e7a-bd58-7597385121fa', 'file_id', '2030-01-03', 'file/link')
        """)
    await db_session.execute_many(
        """
        INSERT INTO ayats
        (ayat_id, public_id, sura_id, day, ayat_number, content, arab_text, transliteration, audio_id) 
        VALUES
        (:ayat_id, :public_id, :sura_id, :day, :ayat_number, :content, :arab_text, :transliteration, :audio_id)
        """,
        [
            {
                'ayat_id': 1,
                'public_id': '96710161-75ab-483f-a9bb-e4d86e068936',
                'sura_id': 1,
                'day': 1,
                'ayat_number': '1',
                'content': 'content',
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
                'content': 'content',
                'arab_text': 'arab text',
                'transliteration': 'transliteration',
                'audio_id': '8f6e2fa5-1a26-4e7a-bd58-7597385121fa',
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
