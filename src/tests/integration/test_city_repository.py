import pytest

from repository.city import CityRepository, City


@pytest.fixture()
async def city(db_session):
    await db_session.execute(
        "INSERT INTO cities (city_id, name) VALUES ('70d3abfd-dec6-42d1-86d0-ef98da07e813', 'Kazan')",
    )


async def test(db_session, city):
    got = await CityRepository(db_session).search_by_name('Kazan')

    assert isinstance(got, list)
    assert len(got) == 1
    assert isinstance(got[0], City)
