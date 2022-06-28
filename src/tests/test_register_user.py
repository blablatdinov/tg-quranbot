import random
from typing import Optional

import pytest

from repository.admin_message import AdminMessageRepositoryInterface
from repository.ayats import AyatRepositoryInterface
from repository.user import User, UserRepositoryInterface
from services.ayat import AyatServiceInterface
from services.register_user import RegisterUser
from services.start_message import StartMessageMeta
from services.answer import Answer

pytestmark = [pytest.mark.asyncio]


class AdminMessageRepositoryMock(AdminMessageRepositoryInterface):

    async def get(self, key: str) -> str:
        return {
            'start': 'start message',
        }[key]


class UserRepositoryMock(UserRepositoryInterface):
    # _storage = {
    #     444:
    #     333:
    # }
    _storage = [
        User(id=1, is_active=False, day=15, chat_id=444),
        User(id=2, is_active=True, day=30, chat_id=333),
        User(id=8945, is_active=True, day=30, chat_id=555),
    ]

    async def create(self, chat_id: int, referrer_id: Optional[int]):
        self._storage.append(User(id=random.randint(0, 100), is_active=True, day=2, referrer=referrer_id, chat_id=chat_id))

    async def get_by_id(self, user_id: int) -> User:
        return list(filter(lambda user: user.id == user_id, self._storage))[0]

    async def get_by_chat_id(self, chat_id: int) -> User:
        return list(filter(lambda user: user.chat_id == chat_id, self._storage))[0]

    async def exists(self, chat_id: int):
        return chat_id in map(lambda user: user.chat_id, self._storage)


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

    assert got == [
        Answer(chat_id=231, message='start message'),
        Answer(chat_id=231, message='some string'),
    ]
    assert await user_repository.get_by_chat_id(231)


async def test_already_registered_user():
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=UserRepositoryMock(),
        ayat_service=AyatServiceMock(AyatRepositoryMock()),
        chat_id=333,
        start_message_meta=StartMessageMeta(referrer=None),
    ).register()

    assert got == Answer(chat_id=333, message='Вы уже зарегистрированы')


async def test_inactive_user():
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=UserRepositoryMock(),
        ayat_service=AyatServiceMock(AyatRepositoryMock()),
        chat_id=444,
        start_message_meta=StartMessageMeta(referrer=None),
    ).register()

    assert got == Answer(chat_id=444, message='Рады видеть вас снова, вы продолжите с дня 15')


async def test_with_referrer():
    user_repository = UserRepositoryMock()
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=user_repository,
        ayat_service=AyatServiceMock(AyatRepositoryMock()),
        start_message_meta=StartMessageMeta(referrer=8945),
        chat_id=222,
    ).register()

    created_user = await user_repository.get_by_chat_id(222)

    assert created_user.referrer == 8945
    assert got == [
        Answer(chat_id=222, message='start message'),
        Answer(chat_id=222, message='some string'),
        Answer(chat_id=555, message='По вашей реферральной ссылке произошла регистрация'),
    ]
