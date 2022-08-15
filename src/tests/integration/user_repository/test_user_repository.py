import uuid

from repository.users.user import User


async def test_create(user_repository):
    got = await user_repository.create(123, None)

    assert isinstance(got, User)
    assert got.chat_id == 123
    assert got.referrer is None
    assert got.day == 2


async def test_create_with_referrer(already_exists_user: User, user_repository):
    got = await user_repository.create(123, already_exists_user.chat_id)

    assert isinstance(got, User)
    assert got.chat_id == 123
    assert got.referrer == already_exists_user.chat_id


async def test_get_by_chat_id(already_exists_user: User, user_repository):
    got = await user_repository.get_by_chat_id(already_exists_user.chat_id)

    assert isinstance(got, User)
    assert got.chat_id == already_exists_user.chat_id


async def test_check_exists(already_exists_user: User, user_repository):
    got = await user_repository.exists(already_exists_user.chat_id)

    assert got is True


async def test_check_not_exists(user_repository):
    got = await user_repository.exists(32784)

    assert got is False


async def test_update_city(already_exists_user: User, city_id: uuid.UUID, user_repository):
    await user_repository.update_city(already_exists_user.chat_id, city_id)

    updated_user = await user_repository.get_by_chat_id(already_exists_user.chat_id)

    assert updated_user.city_id == city_id


async def test_update_referrer(already_exists_user: User, user_without_referrer: User, user_repository):
    await user_repository.update_referrer(user_without_referrer.chat_id, already_exists_user.chat_id)

    updated_user = await user_repository.get_by_chat_id(user_without_referrer.chat_id)

    assert updated_user.referrer == already_exists_user.chat_id
