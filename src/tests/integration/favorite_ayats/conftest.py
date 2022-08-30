import pytest

from tests.factories.file_factory import factory


@pytest.fixture()
async def ayats(db_session, mixer):
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
    return [1, 2]


@pytest.fixture()
async def user(db_session):
    insert_user_query = "INSERT INTO users (chat_id, is_active, day) VALUES (389472, 't', 2) RETURNING chat_id"
    return await db_session.execute(insert_user_query)


@pytest.fixture()
async def user_favorite_ayat(db_session, ayats, user):
    insert_favorite_ayat_query = 'INSERT INTO favorite_ayats (ayat_id, user_id) VALUES (:ayat_id, :user_id)'
    await db_session.execute(insert_favorite_ayat_query, {'ayat_id': ayats[0], 'user_id': user})
