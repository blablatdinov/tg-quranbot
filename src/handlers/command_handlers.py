import random

from aiogram import types

from db import DBConnection
from repository.admin_message import AdminMessageRepository
from repository.ayats.ayat import AyatRepository
from repository.users.user import UserRepository
from repository.users.user_actions import UserActionRepository
from repository.users.users import UsersRepository
from services.register_user import RegisterNewUser, RegisterUserWithReferrer, RegisterAlreadyExistsUser, RegisterUser
from services.start_message import get_start_message_query


async def start_handler(message: types.Message):
    """Ответ на команды: start.

    :param message: app_types.Message
    """
    async with DBConnection() as connection:
        register_new_user = RegisterNewUser(
            UserRepository(connection),
            UserActionRepository(connection),
            AdminMessageRepository(connection),
            AyatRepository(connection),
        )

        user_repository = UserRepository(connection)
        register_user = RegisterUser(
            register_new_user,
            RegisterUserWithReferrer(
                register_new_user,
                user_repository,
                get_start_message_query(message.text),
            ),
            RegisterAlreadyExistsUser(
                user_repository,
                UserActionRepository(connection),
                UsersRepository(connection),
            ),
            user_repository,
            message.chat.id
        )
        answer = await register_user.register()
        await answer.send()
