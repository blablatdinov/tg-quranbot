import pytest

from repository.ayats.ayat import Ayat
from repository.ayats.favorite_ayats import FavoriteAyatsRepository


@pytest.fixture()
async def ayats(db_session, mixer):
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
    return [1, 2]


@pytest.fixture()
async def user(db_session):
    insert_user_query = "INSERT INTO users (chat_id, is_active, day) VALUES (389472, 't', 2) RETURNING chat_id"
    return await db_session.execute(insert_user_query)


@pytest.fixture()
async def user_favorite_ayat(db_session, ayats, user):
    insert_favorite_ayat_query = "INSERT INTO favorite_ayats (ayat_id, user_id) VALUES (:ayat_id, :user_id)"
    await db_session.execute(insert_favorite_ayat_query, {'ayat_id': ayats[0], 'user_id': user})


async def test_get_favorites(db_session, user_favorite_ayat, user: int):
    got = await FavoriteAyatsRepository(db_session).get_favorites(user)

    assert isinstance(got, list)
    assert len(got) == 1
    assert isinstance(got[0], Ayat)


async def test_check_ayat_is_favorite(db_session, user_favorite_ayat, user: int, ayats: list[int]):
    got = await FavoriteAyatsRepository(db_session).check_ayat_is_favorite_for_user(ayats[0], user)

    assert got is True


async def test_check_ayat_not_is_favorite(db_session, user_favorite_ayat, user: int, ayats: list[int]):
    got = await FavoriteAyatsRepository(db_session).check_ayat_is_favorite_for_user(ayats[1], user)

    assert got is False


async def test_add_to_favorite(db_session, user: int, ayats: list[int]):
    await FavoriteAyatsRepository(db_session).add_to_favorite(user, ayats[0])

    ayat_is_favorite = await FavoriteAyatsRepository(db_session).check_ayat_is_favorite_for_user(ayats[0], user)

    assert ayat_is_favorite is True


async def test_remove_from_favorite(db_session, user: int, ayats: list[int], user_favorite_ayat):
    await FavoriteAyatsRepository(db_session).remove_from_favorite(user, ayats[0])

    ayat_is_favorite = await FavoriteAyatsRepository(db_session).check_ayat_is_favorite_for_user(ayats[0], user)

    assert ayat_is_favorite is False
