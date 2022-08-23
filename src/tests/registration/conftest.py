import uuid

import pytest

from repository.ayats.ayat import Ayat
from repository.users.user import User
from services.register_user import RegisterAlreadyExistsUser, RegisterNewUser, RegisterUser, RegisterUserWithReferrer
from services.start_message import get_start_message_query
from tests.mocks.admin_messages_repository import AdminMessageRepositoryMock
from tests.mocks.ayat_repository import AyatRepositoryMock
from tests.mocks.user_repository import UserRepositoryMock
from tests.mocks.users_repository import UsersRepositoryMock


@pytest.fixture
def user_repository_mock():
    return UserRepositoryMock()


@pytest.fixture
def user_repository_with_registered_active_user(user_repository_mock):
    user_repository_mock.storage = [
        User(legacy_id=1, is_active=True, day=15, chat_id=444, city_id=uuid.uuid4()),
    ]
    return user_repository_mock


@pytest.fixture
def user_repository_with_registered_inactive_user(user_repository_mock):
    user_repository_mock.storage = [
        User(legacy_id=1, is_active=False, day=15, chat_id=444, city_id=uuid.uuid4()),
    ]
    return user_repository_mock


@pytest.fixture
def register_service(ayat_repository_mock):
    async def _register_service(  # noqa: WPS430
        user_repository_mock: UserRepositoryMock,
        chat_id: int,
        message_text: str,
    ):
        register_new_user = RegisterNewUser(
            user_repository_mock,
            AdminMessageRepositoryMock(),
            ayat_repository_mock,
        )
        return await RegisterUser(
            register_new_user,
            RegisterUserWithReferrer(
                register_new_user,
                user_repository_mock,
                get_start_message_query(message_text),
            ),
            RegisterAlreadyExistsUser(
                user_repository_mock,
                UsersRepositoryMock(),
            ),
            chat_id,
        ).register()

    return _register_service


@pytest.fixture()
def ayat_repository_mock(fake_text):
    mock = AyatRepositoryMock()
    mock.storage = [Ayat(
        id=1,
        sura_num=1,
        ayat_num='1',
        arab_text=fake_text(),
        content=fake_text(),
        transliteration=fake_text(),
        sura_link=fake_text(),
        audio_telegram_id=fake_text(),
        link_to_audio_file=fake_text(),
    )]
    return mock
