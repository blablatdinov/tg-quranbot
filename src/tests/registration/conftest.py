import uuid

import pytest

from repository.ayats.ayat import Ayat
from repository.users.registration import RegistrationRepository
from repository.users.user import User
from services.register.register_already_exists_user import RegisterAlreadyExistsUser
from services.register.register_answer import RegisterAnswer
from services.register.register_new_user import RegisterNewUser
from services.register.register_user_with_referrer import RegisterUserWithReferrer
from services.start_message import StartMessage
from tests.mocks.admin_messages_repository import AdminMessageRepositoryMock
from tests.mocks.ayat_repository import AyatRepositoryMock
from tests.mocks.bot import BotMock
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
        return await RegisterAnswer(
            RegisterNewUser(
                BotMock(),
                RegistrationRepository(
                    user_repository_mock,
                    AdminMessageRepositoryMock(),
                    ayat_repository_mock,
                ),
            ),
            RegisterUserWithReferrer(
                BotMock(),
                RegisterNewUser(
                    BotMock(),
                    RegistrationRepository(
                        user_repository_mock,
                        AdminMessageRepositoryMock(),
                        ayat_repository_mock,
                    ),
                ),
                user_repository_mock,
                StartMessage(message_text, user_repository_mock),
            ),
            RegisterAlreadyExistsUser(
                BotMock(),
                user_repository_mock,
                UsersRepositoryMock(),
            ),
            chat_id,
        ).send()

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
