import pytest

from repository.ayats.ayat_morning_content import AyatMorningContentRepository, ContentSpam


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
                'day': 2,
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
                'day': 3,
                'ayat_number': '2',
                'content': 'content',
                'arab_text': 'arab text',
                'transliteration': 'transliteration',
                'audio_id': '8f6e2fa5-1a26-4e7a-bd58-7597385121fa',
            },
        ],
    )


@pytest.fixture()
async def users(db_session):
    insert_users_query = """
        INSERT INTO users
        (chat_id, is_active, day) 
        VALUES
        (:chat_id, 't', :day)
    """
    await db_session.execute_many(insert_users_query, [
        {
            'chat_id': 7458397,
            'day': 2,
        },
        {
            'chat_id': 832749,
            'day': 3,
        },
    ])


async def test(db_session, ayats, users):
    got = await AyatMorningContentRepository(db_session).get_morning_content()

    assert isinstance(got, list)
    assert len(got) == 2
    assert isinstance(got[0], ContentSpam)
    assert got[0].content == '<b>1: 2)</b> content\n'
    assert got[0].link == '/hello'
    assert got[0].chat_id == 832749
