from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.schemas import Ayat


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
