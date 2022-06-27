import pytest

from repository.user import UserRepositoryInterface, User
from services.register_user import RegisterUser

pytestmark = [pytest.mark.asyncio]


class UserRepositoryMock(UserRepositoryInterface):

    async def create(self, chat_id: int):
        return

    async def get(self, chat_id: int):
        active = {
            444: False
        }.get(chat_id, True)
        return User(is_active=active)

    async def exists(self, chat_id: int):
        active_users = (333, 444)
        return chat_id in active_users


async def test():
    got = await RegisterUser(
        repository=UserRepositoryMock(),
        chat_id=231,
    ).register()

    assert got == 'user created'


async def test_already_registered_user():
    got = await RegisterUser(
        repository=UserRepositoryMock(),
        chat_id=333,
    ).register()

    assert got == 'user already registered'


async def test_inactive_user():
    got = await RegisterUser(
        repository=UserRepositoryMock(),
        chat_id=444,
    ).register()

    assert got == 'user active again'
