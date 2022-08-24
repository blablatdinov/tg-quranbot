from aiogram import types

from services.answers.answer import TextAnswer


async def test_register_new_user(register_service, ayat_repository_mock, user_repository_mock):
    got = await register_service(user_repository_mock, 231, '/start')

    assert isinstance(got, list)
    assert len(got) == 2
    assert {type(elem) for elem in got} == {types.Message}
    assert got[0].text == 'start message_handlers'
    assert got[0].chat.id == got[1].chat.id == 231
    assert got[1].text == str(ayat_repository_mock.storage[0])
    assert await user_repository_mock.get_by_chat_id(231)
    # TODO: check, that event about user action sended in queue


async def test_already_registered_user(
    register_service,
    ayat_repository_mock,
    user_repository_with_registered_active_user,
):
    got = await register_service(user_repository_with_registered_active_user, 444, '/start')

    assert got[0].text == 'Вы уже зарегистрированы'
    assert got[0].chat.id == 444
    # TODO: check, that event about user action sended in queue


async def test_inactive_user(register_service, user_repository_with_registered_inactive_user):
    got = await register_service(user_repository_with_registered_inactive_user, 444, '/start')

    assert got[0].text == 'Рады видеть вас снова, вы продолжите с дня 15'
    # TODO: check, that event about user action sended in queue


async def test_with_referrer(
    register_service,
    user_repository_with_registered_inactive_user,
    ayat_repository_mock,
):
    got = await register_service(user_repository_with_registered_inactive_user, 222, '/start 1')

    created_user = await user_repository_with_registered_inactive_user.get_by_chat_id(222)

    assert len(user_repository_with_registered_inactive_user.storage) == 2
    assert created_user.referrer == 444
    assert len(got) == 3
    assert got[0].text == 'start message_handlers'
    assert 'a href' in got[1].text
    assert got[2].text == 'По вашей реферральной ссылке произошла регистрация'
    assert got[0].chat.id == got[1].chat.id == 222
    assert got[2].chat.id == 444
    # TODO: check, that event about user action sended in queue
