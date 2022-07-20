from aiogram import types

from db import DBConnection
from repository.admin_message import AdminMessageRepository
from repository.ayats.ayat import AyatRepository
from repository.update_log import UpdatesLogRepository
from repository.users.user import UserRepository
from repository.users.user_actions import UserActionRepository
from repository.users.users import UsersRepository
from services.answers.log_answer import LoggedAnswer, LoggedSourceMessageAnswerProcess
from services.register_user import RegisterAlreadyExistsUser, RegisterNewUser, RegisterUser, RegisterUserWithReferrer
from services.start_message import get_start_message_query


async def start_handler(message: types.Message):
    """Ответ на команды: start.

    :param message: app_types.Message
    """
    async with DBConnection() as connection:
        user_action_repository = UserActionRepository(connection)
        user_repository = UserRepository(connection)
        register_new_user = RegisterNewUser(
            user_repository,
            user_action_repository,
            AdminMessageRepository(connection),
            AyatRepository(connection),
        )
        answer = await RegisterUser(
            register_new_user,
            RegisterUserWithReferrer(
                register_new_user,
                user_repository,
                get_start_message_query(message.text),
            ),
            RegisterAlreadyExistsUser(
                user_repository,
                user_action_repository,
                UsersRepository(connection),
            ),
            message.chat.id,
        ).register()
        answer = LoggedSourceMessageAnswerProcess(
            UpdatesLogRepository(connection),
            message,
            LoggedAnswer(
                answer,
                UpdatesLogRepository(connection),
            ),
        )
        await answer.send()
