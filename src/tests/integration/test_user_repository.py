import uuid

import pytest

from repository.users.user import User, UserRepository


@pytest.fixture()
async def already_exists_user(db_session):
    return await UserRepository(db_session).create(4895)


@pytest.fixture()
async def user_without_referrer(db_session):
    return await UserRepository(db_session).create(879234)


@pytest.fixture()
async def city_id(db_session):
    city_uuid = uuid.uuid4()
    await db_session.execute("INSERT INTO cities (city_id, name) VALUES ('{0}', 'Казань') RETURNING city_id".format(city_uuid))
    return city_uuid


async def test_create(db_session):
    got = await UserRepository(db_session).create(123, None)

    assert isinstance(got, User)
    assert got.chat_id == 123
    assert got.referrer is None
    assert got.day == 2


async def test_create_with_referrer(db_session, already_exists_user: User):
    got = await UserRepository(db_session).create(123, already_exists_user.chat_id)

    assert isinstance(got, User)
    assert got.chat_id == 123
    assert got.referrer == already_exists_user.chat_id


async def test_get_by_chat_id(db_session, already_exists_user: User):
    got = await UserRepository(db_session).get_by_chat_id(already_exists_user.chat_id)

    assert isinstance(got, User)
    assert got.chat_id == already_exists_user.chat_id


async def test_check_exists(db_session, already_exists_user: User):
    got = await UserRepository(db_session).exists(already_exists_user.chat_id)

    assert got is True


async def test_check_not_exists(db_session):
    got = await UserRepository(db_session).exists(32784)

    assert got is False


async def test_update_city(db_session, already_exists_user: User, city_id: uuid.UUID):
    await UserRepository(db_session).update_city(already_exists_user.chat_id, city_id)

    updated_user = await UserRepository(db_session).get_by_chat_id(already_exists_user.chat_id)

    assert updated_user.city_id == city_id


async def test_update_referrer(db_session, already_exists_user: User, user_without_referrer: User):
    await UserRepository(db_session).update_referrer(user_without_referrer.chat_id, already_exists_user.chat_id)

    updated_user = await UserRepository(db_session).get_by_chat_id(user_without_referrer.chat_id)

    assert updated_user.referrer == already_exists_user.chat_id

