import pytest

from repository.ayats.ayat import Ayat
from repository.user import User
from services.answer import Answer
from services.register_user import RegisterUser
from services.start_message import StartMessageMeta
from tests.mocks import AdminMessageRepositoryMock, AyatRepositoryMock, AyatServiceMock, UserRepositoryMock


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


async def test(ayat_repository_mock):
    user_repository = UserRepositoryMock()
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=user_repository,
        ayat_service=AyatServiceMock(ayat_repository_mock, 12090),
        chat_id=231,
        start_message_meta=StartMessageMeta(referrer=None),
    ).register()
    print(got)

    assert got == [
        Answer(chat_id=231, message='start message'),
        Answer(chat_id=231, message=str(ayat_repository_mock.storage[0])),
    ]
    assert await user_repository.get_by_chat_id(231)


async def test_already_registered_user(user_repository_with_registered_active_user):
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=user_repository_with_registered_active_user,
        ayat_service=AyatServiceMock(AyatRepositoryMock(), 1920),
        chat_id=444,
        start_message_meta=StartMessageMeta(referrer=None),
    ).register()

    assert got == Answer(chat_id=444, message='Вы уже зарегистрированы')


async def test_inactive_user(user_repository_with_registered_inactive_user):
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=user_repository_with_registered_inactive_user,
        ayat_service=AyatServiceMock(AyatRepositoryMock(), 123),
        chat_id=444,
        start_message_meta=StartMessageMeta(referrer=None),
    ).register()

    assert got == Answer(chat_id=444, message='Рады видеть вас снова, вы продолжите с дня 15')


async def test_with_referrer(user_repository_with_registered_active_user, ayat_repository_mock):
    got = await RegisterUser(
        admin_messages_repository=AdminMessageRepositoryMock(),
        user_repository=user_repository_with_registered_active_user,
        ayat_service=AyatServiceMock(ayat_repository_mock, 213),
        start_message_meta=StartMessageMeta(referrer=1),
        chat_id=222,
    ).register()

    created_user = await user_repository_with_registered_active_user.get_by_chat_id(222)

    assert created_user.referrer == 1
    assert got == [
        Answer(chat_id=222, message='start message'),
        Answer(chat_id=222, message=str(ayat_repository_mock.storage[0])),
        Answer(chat_id=444, message='По вашей реферральной ссылке произошла регистрация'),
    ]
