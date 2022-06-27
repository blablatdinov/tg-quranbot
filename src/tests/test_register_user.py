import pytest

from repository.admin_message import AdminMessageRepositoryInterface
from repository.user import User, UserRepositoryInterface
from repository.ayats import AyatRepositoryInterface
from services.ayat import AyatServiceInterface
from services.register_user import RegisterUser

pytestmark = [pytest.mark.asyncio]


class AdminMessageRepositoryMock(AdminMessageRepositoryInterface):

    async def get(self, key: str) -> str:
        return {
            'start': 'start message',
        }[key]


class UserRepositoryMock(UserRepositoryInterface):

    async def create(self, chat_id: int):
        return

    async def get(self, chat_id: int):
        return {
            444: User(is_active=False, day=15),
            333: User(is_active=True, day=30),
        }[chat_id]

    async def exists(self, chat_id: int):
        active_users = (333, 444)
        return chat_id in active_users



class AyatRepositoryMock(AyatRepositoryInterface):

    pass


class AyatServiceMock(AyatServiceInterface):

    async def get_formatted_first_ayat(self):
        return 'some string'


async def test():
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=UserRepositoryMock(),
        ayat_service=AyatServiceMock(AyatRepositoryMock()),
        chat_id=231,
    ).register()

    assert got == ('start message', 'some string')


async def test_already_registered_user():
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=UserRepositoryMock(),
        ayat_service=AyatServiceMock(AyatRepositoryMock()),
        chat_id=333,
    ).register()

    assert got == ('Вы уже зарегистрированы',)


async def test_inactive_user():
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=UserRepositoryMock(),
        ayat_service=AyatServiceMock(AyatRepositoryMock()),
        chat_id=444,
    ).register()

    assert got == ('Рады видеть вас снова, вы продолжите с дня 15',)
