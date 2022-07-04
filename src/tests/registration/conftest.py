import pytest

from repository.ayats.ayat import Ayat
from repository.user import User
from tests.mocks.ayat_repository import AyatRepositoryMock
from tests.mocks.user_action_repository import UserActionRepositoryMock
from tests.mocks.user_repository import UserRepositoryMock


@pytest.fixture()
def user_repository_with_registered_active_user():
    user_repository = UserRepositoryMock()
    user_repository.storage = [
        User(id=1, is_active=True, day=15, chat_id=444, city_id=1),
    ]
    return user_repository


@pytest.fixture()
def user_repository_with_registered_inactive_user():
    user_repository = UserRepositoryMock()
    user_repository.storage = [
        User(id=1, is_active=False, day=15, chat_id=444, city_id=1),
    ]
    return user_repository


@pytest.fixture()
def user_action_repository():
    return UserActionRepositoryMock()


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
