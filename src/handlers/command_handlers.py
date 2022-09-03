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
    RegisterUser,
    RegisterUserWithReferrer,
    RegisterNewUserEvent,
    RegisterUserWithReferrerEvent,
    SafeRegistrationWithReferrer,
)
from services.start_message import StartMessage
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
    register_new_user = RegisterNewUser(
        BotInstance.get(),
        registration_repository,
    )
    await StateFinishAnswer(
        RegisterUser(
            RegisterNewUserEvent(
                message.chat.id,
                register_new_user,
                NatsIntegration([]),
            ),
            SafeRegistrationWithReferrer(
                RegisterUserWithReferrerEvent(
                    message.chat.id,
                    RegisterUserWithReferrer(
                        BotInstance.get(),
                        register_new_user,
                        UserRepository(database),
                        StartMessage(message.text, UserRepository(database)),
                    ),
                    NatsIntegration([]),
                    StartMessage(message.text, UserRepository(database)),
                ),
                RegisterNewUserEvent(
                    message.chat.id,
                    register_new_user,
                    NatsIntegration([]),
                ),
                database,
            ),
            RegisterAlreadyExistsUser(
                BotInstance.get(),
                UserRepository(database),
                UsersRepository(database),
            ),
            message.chat.id,
        ),
        state,
    ).send()
