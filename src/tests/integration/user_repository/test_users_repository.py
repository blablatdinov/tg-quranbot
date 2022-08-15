from repository.users.users import UsersRepository


async def test_get_active_users(db_session, active_users, inactive_users):
    got = await UsersRepository(db_session).get_active_user_chat_ids()

    assert len(got) == 5


async def test_update_status_to_active(db_session, inactive_users: list[int]):
    await UsersRepository(db_session).update_status(inactive_users, to=True)

    chat_ids = await db_session.fetch_all("SELECT chat_id FROM users WHERE is_active='t'")

    assert inactive_users == [dict(chat_id._mapping)['chat_id'] for chat_id in chat_ids]  # noqa: WPS437


async def test_update_status_to_inactive(db_session, active_users: list[int]):
    await UsersRepository(db_session).update_status(active_users, to=False)

    chat_ids = await db_session.fetch_all("SELECT chat_id FROM users WHERE is_active='f'")

    assert active_users == [dict(chat_id._mapping)['chat_id'] for chat_id in chat_ids]  # noqa: WPS437


async def test_increment_user_days(db_session, active_users: list[int]):
    await UsersRepository(db_session).increment_user_days(active_users)

    chat_ids = await db_session.fetch_all('SELECT chat_id FROM users WHERE day=3')

    assert active_users == [dict(chat_id._mapping)['chat_id'] for chat_id in chat_ids]  # noqa: WPS437


async def test_get_active_users_with_city(db_session, active_users):
    got = await UsersRepository(db_session).active_users_with_city()

    assert got == active_users
