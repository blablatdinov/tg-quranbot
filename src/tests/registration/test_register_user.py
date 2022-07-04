import pytest

from repository.ayats.ayat import Ayat
from repository.user import User
from repository.user_actions import UserAction, UserActionEnum
from services.answer import Answer
from services.register_user import RegisterUser
from services.start_message import StartMessageMeta
from tests.mocks import AdminMessageRepositoryMock, AyatRepositoryMock, AyatServiceMock, UserRepositoryMock, UserActionRepositoryMock


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


async def test(ayat_repository_mock, user_action_repository):
    user_repository = UserRepositoryMock()
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=user_repository,
        ayat_service=AyatServiceMock(ayat_repository_mock, 12090),
        user_action_repository=user_action_repository,
        chat_id=231,
        start_message_meta=StartMessageMeta(referrer=None),
    ).register()

    assert got == [
        Answer(chat_id=231, message='start message'),
        Answer(chat_id=231, message=str(ayat_repository_mock.storage[0])),
    ]
    assert await user_repository.get_by_chat_id(231)
    assert len(user_action_repository.storage) == 1
    assert user_action_repository.storage[0].action == UserActionEnum.SUBSCRIBED
    assert user_action_repository.storage[0].chat_id == 231


async def test_already_registered_user(user_repository_with_registered_active_user, user_action_repository):
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=user_repository_with_registered_active_user,
        ayat_service=AyatServiceMock(AyatRepositoryMock(), 1920),
        user_action_repository=user_action_repository,
        chat_id=444,
        start_message_meta=StartMessageMeta(referrer=None),
    ).register()

    assert got == Answer(chat_id=444, message='Вы уже зарегистрированы')
    assert len(user_action_repository.storage) == 0


async def test_inactive_user(user_repository_with_registered_inactive_user, user_action_repository):
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=user_repository_with_registered_inactive_user,
        ayat_service=AyatServiceMock(AyatRepositoryMock(), 123),
        user_action_repository=user_action_repository,
        chat_id=444,
        start_message_meta=StartMessageMeta(referrer=None),
    ).register()

    assert got == Answer(chat_id=444, message='Рады видеть вас снова, вы продолжите с дня 15')
    assert len(user_action_repository.storage) == 1
    assert user_action_repository.storage[0].action == UserActionEnum.REACTIVATED


async def test_with_referrer(user_repository_with_registered_active_user, ayat_repository_mock, user_action_repository):
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=user_repository_with_registered_active_user,
        ayat_service=AyatServiceMock(ayat_repository_mock, 213),
        user_action_repository=user_action_repository,
        start_message_meta=StartMessageMeta(referrer=1),
        chat_id=222,
    ).register()

    created_user = await user_repository_with_registered_active_user.get_by_chat_id(222)

    assert len(user_repository_with_registered_active_user.storage) == 2
    assert created_user.referrer == 1
    assert got == [
        Answer(chat_id=222, message='start message'),
        Answer(chat_id=222, message=str(ayat_repository_mock.storage[0])),
        Answer(chat_id=444, message='По вашей реферральной ссылке произошла регистрация'),
    ]
    assert len(user_action_repository.storage) == 1
    assert user_action_repository.storage[0].action == UserActionEnum.SUBSCRIBED
