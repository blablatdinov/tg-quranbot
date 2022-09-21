import pytest

from repository.ayats.neighbor_ayats import FavoriteAyatsNeighborRepository
from repository.ayats.schemas import AyatShort


@pytest.fixture()
async def user_favorite_ayats(db_session, user: int, ayats: list[int]):
    insert_favorite_ayat_query = 'INSERT INTO favorite_ayats (ayat_id, user_id) VALUES (:ayat_id, :user_id)'
    await db_session.execute_many(insert_favorite_ayat_query, [
        {'ayat_id': ayats[0], 'user_id': user},
        {'ayat_id': ayats[1], 'user_id': user},
    ])


async def test(db_session, user: int, user_favorite_ayats, ayats: list[int]):
    got = await FavoriteAyatsNeighborRepository(db_session, user).get_ayat_neighbors(ayats[0])

    assert isinstance(got, list)
    assert len(got) == 2
    assert isinstance(got[0], AyatShort)
