import uuid

import pytest

from db.models.user import User
from repository.users.users import UsersRepository


@pytest.fixture()
async def city_id(db_session):
    city_uuid = uuid.uuid4()
    await db_session.execute("INSERT INTO cities (city_id, name) VALUES ('{0}', 'Казань') RETURNING city_id".format(city_uuid))
    return city_uuid


@pytest.fixture()
async def active_users(db_session, mixer, city_id):
    user_dicts = []
    users = mixer.cycle(5).blend('db.models.user.User', is_active=True, chat_id=(x for x in range(1, 6)), city_id=str(city_id))
    for user in users:
        user_dict = user.__dict__
        user_dict.pop('_sa_instance_state')
        user_dicts.append(user_dict)
    await db_session.execute_many(
        User.__table__.insert(),
        values=user_dicts,
    )
    return [x.chat_id for x in users]


@pytest.fixture()
async def inactive_users(db_session, mixer):
    user_dicts = []
    users = mixer.cycle(7).blend('db.models.user.User', is_active=False, chat_id=(x for x in range(6, 14)))
    for user in users:
        user_dict = user.__dict__
        user_dict.pop('_sa_instance_state')
        user_dicts.append(user_dict)
    await db_session.execute_many(
        User.__table__.insert(),
        values=user_dicts,
    )
    return [x.chat_id for x in users]


async def test_get_active_users(db_session, active_users, inactive_users):
    got = await UsersRepository(db_session).get_active_user_chat_ids()

    assert len(got) == 5


async def test_update_status_to_active(db_session, inactive_users: list[int]):
    await UsersRepository(db_session).update_status(inactive_users, to=True)

    chat_ids = await db_session.fetch_all("SELECT chat_id FROM users WHERE is_active='t'")

    assert [dict(x._mapping)['chat_id'] for x in chat_ids] == inactive_users


async def test_update_status_to_inactive(db_session, active_users: list[int]):
    await UsersRepository(db_session).update_status(active_users, to=False)

    chat_ids = await db_session.fetch_all("SELECT chat_id FROM users WHERE is_active='f'")

    assert [dict(x._mapping)['chat_id'] for x in chat_ids] == active_users


async def test_increment_user_days(db_session, active_users: list[int]):
    await UsersRepository(db_session).increment_user_days(active_users)

    chat_ids = await db_session.fetch_all("SELECT chat_id FROM users WHERE day=3")

    assert [dict(x._mapping)['chat_id'] for x in chat_ids] == active_users


async def test_get_active_users_with_city(db_session, active_users):
    got = await UsersRepository(db_session).active_users_with_city()

    assert got == active_users
