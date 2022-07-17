from repository.users.user_actions import UserActionEnum
from repository.users.user_registration_repository import UserRegistrationRepository
from services.answer import Answer
from services.register_user import RegisterUser
from services.start_message import StartMessageMeta
from tests.mocks.admin_messages_repository import AdminMessageRepositoryMock
from tests.mocks.ayat_repository import AyatRepositoryMock
from tests.mocks.user_repository import UserRepositoryMock
from tests.mocks.users_repository import UsersRepositoryMock


async def test(ayat_repository_mock, user_action_repository):
    user_repository = UserRepositoryMock()
    got = await RegisterUser(
        user_registration_repository=UserRegistrationRepository(
            user_repository,
            user_action_repository,
            AdminMessageRepositoryMock(),
            UsersRepositoryMock(),
        ),
        ayat_repository=ayat_repository_mock,
        chat_id=231,
        start_message_meta=StartMessageMeta(referrer=None),
    ).register()

    assert got == [
        Answer(chat_id=231, message='start message_handlers'),
        Answer(chat_id=231, message=str(ayat_repository_mock.storage[0])),
    ]
    assert await user_repository.get_by_chat_id(231)
    assert len(user_action_repository.storage) == 1
    assert user_action_repository.storage[0].action == UserActionEnum.SUBSCRIBED
    assert user_action_repository.storage[0].chat_id == 231


async def test_already_registered_user(user_repository_with_registered_active_user, user_action_repository):
    got = await RegisterUser(
        user_registration_repository=UserRegistrationRepository(
            user_repository_with_registered_active_user,
            user_action_repository,
            AdminMessageRepositoryMock(),
            UsersRepositoryMock(),
        ),
        ayat_repository=AyatRepositoryMock(),
        chat_id=444,
        start_message_meta=StartMessageMeta(referrer=None),
    ).register()

    assert got == Answer(chat_id=444, message='Вы уже зарегистрированы')
    assert len(user_action_repository.storage) == 0  # noqa: WPS507 Found useless `len()` compare
    # Показываем, что не было ничего добавлено


async def test_inactive_user(user_repository_with_registered_inactive_user, user_action_repository):
    got = await RegisterUser(
        user_registration_repository=UserRegistrationRepository(
            user_repository_with_registered_inactive_user,
            user_action_repository,
            AdminMessageRepositoryMock(),
            UsersRepositoryMock(),
        ),
        ayat_repository=AyatRepositoryMock(),
        chat_id=444,
        start_message_meta=StartMessageMeta(referrer=None),
    ).register()

    assert got == Answer(chat_id=444, message='Рады видеть вас снова, вы продолжите с дня 15')
    assert len(user_action_repository.storage) == 1
    assert user_action_repository.storage[0].action == UserActionEnum.REACTIVATED


async def test_with_referrer(user_repository_with_registered_active_user, ayat_repository_mock, user_action_repository):
    got = await RegisterUser(
        user_registration_repository=UserRegistrationRepository(
            user_repository_with_registered_active_user,
            user_action_repository,
            AdminMessageRepositoryMock(),
            UsersRepositoryMock(),
        ),
        ayat_repository=ayat_repository_mock,
        start_message_meta=StartMessageMeta(referrer=1),
        chat_id=222,
    ).register()

    created_user = await user_repository_with_registered_active_user.get_by_chat_id(222)

    assert len(user_repository_with_registered_active_user.storage) == 2
    assert created_user.referrer == 1
    assert got == [
        Answer(chat_id=222, message='start message_handlers'),
        Answer(chat_id=222, message=str(ayat_repository_mock.storage[0])),
        Answer(chat_id=444, message='По вашей реферральной ссылке произошла регистрация'),
    ]
    assert len(user_action_repository.storage) == 1
    assert user_action_repository.storage[0].action == UserActionEnum.SUBSCRIBED
