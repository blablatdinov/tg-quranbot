from aiogram import types
from aiogram.dispatcher import FSMContext

from db.connection import database
from integrations.nats_integration import NatsIntegration
from repository.admin_message import AdminMessageRepository
from repository.ayats.ayat import AyatRepository
from repository.users.registration import RegistrationRepository
from repository.users.user import UserRepository
from repository.users.users import UsersRepository
from services.answers.state_finish_answer import StateFinishAnswer
from services.register_user import (
    RegisterAlreadyExistsUser,
    RegisterNewUser,
    RegisterNewUserEvent,
    RegisterUser,
    RegisterUserWithReferrer,
)
from services.start_message import get_start_message_query
from utlls import BotInstance


async def start_handler(message: types.Message, state: FSMContext):
    """Ответ на команды: start.

    :param message: app_types.Message
    :param state: FSMContext
    """
    registration_repository = RegistrationRepository(
        UserRepository(database),
        AdminMessageRepository(database),
        AyatRepository(database),
    )
    register_new_user = RegisterNewUserEvent(
        message.chat.id,
        RegisterNewUser(
            BotInstance.get(),
            message.chat.id,
            registration_repository,
        ),
        NatsIntegration([]),
    )
    await StateFinishAnswer(
        RegisterUser(
            register_new_user,
            RegisterUserWithReferrer(
                BotInstance.get(),
                message.chat.id,
                register_new_user,
                UserRepository(database),
                get_start_message_query(message.text),
            ),
            RegisterAlreadyExistsUser(
                BotInstance.get(),
                message.chat.id,
                UserRepository(database),
                UsersRepository(database),
            ),
            message.chat.id,
        ),
        state,
    ).send()
