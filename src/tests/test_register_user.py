from typing import Optional

import pytest

from repository.admin_message import AdminMessageRepositoryInterface
from repository.ayats import AyatRepositoryInterface
from repository.user import User, UserRepositoryInterface
from services.ayat import AyatServiceInterface
from services.register_user import RegisterUser
from services.start_message import StartMessageMeta

pytestmark = [pytest.mark.asyncio]


class AdminMessageRepositoryMock(AdminMessageRepositoryInterface):

    async def get(self, key: str) -> str:
        return {
            'start': 'start message',
        }[key]


class UserRepositoryMock(UserRepositoryInterface):
    _storage = {
        444: User(is_active=False, day=15, chat_id=444),
        333: User(is_active=True, day=30, chat_id=333),
    }

    async def create(self, chat_id: int, referrer_id: Optional[int]):
        self._storage[chat_id] = User(is_active=True, day=2, referrer=referrer_id)

    async def get_by_id(self, user_id: int) -> User:
        raise NotImplementedError

    async def get(self, chat_id: int) -> User:
        return self._storage[chat_id]

    async def exists(self, chat_id: int):
        active_users = filter(lambda dict_item: dict_item[1].is_active, self._storage.items())
        return chat_id in active_users


class AyatRepositoryMock(AyatRepositoryInterface):

    pass


class AyatServiceMock(AyatServiceInterface):

    async def get_formatted_first_ayat(self):
        return 'some string'


async def test():
    user_repository = UserRepositoryMock()
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=user_repository,
        ayat_service=AyatServiceMock(AyatRepositoryMock()),
        chat_id=231,
        start_message_meta=StartMessageMeta(referrer=None),
    ).register()

    assert got == ('start message', 'some string')
    assert user_repository.get(231)


async def test_already_registered_user():
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=UserRepositoryMock(),
        ayat_service=AyatServiceMock(AyatRepositoryMock()),
        chat_id=333,
        start_message_meta=StartMessageMeta(referrer=None),
    ).register()

    assert got == ('Вы уже зарегистрированы',)


async def test_inactive_user():
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=UserRepositoryMock(),
        ayat_service=AyatServiceMock(AyatRepositoryMock()),
        chat_id=444,
        start_message_meta=StartMessageMeta(referrer=None),
    ).register()

    assert got == ('Рады видеть вас снова, вы продолжите с дня 15',)


async def test_with_referrer():
    user_repository = UserRepositoryMock()
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=user_repository,
        ayat_service=AyatServiceMock(AyatRepositoryMock()),
        start_message_meta=StartMessageMeta(referrer=8945),
        chat_id=444,
    ).register()

    created_user = await user_repository.get(444)

    assert created_user.referrer == 8945
    assert ('start message', 'some string', '') == got
