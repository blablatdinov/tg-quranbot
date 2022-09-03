from aiogram import types
from aiogram.dispatcher import FSMContext

from db.connection import database
from integrations.nats_integration import NatsIntegration
from repository.admin_message import AdminMessageRepository
from repository.ayats.ayat import AyatRepository
from repository.update_log import UpdatesLogRepository
from repository.users.registration import RegistrationRepository
from repository.users.user import UserRepository
from repository.users.users import UsersRepository
from services.answers.log_answer import LoggedSourceMessageAnswer
from services.answers.state_finish_answer import StateFinishAnswer
from services.register.register_already_exists_user import RegisterAlreadyExistsUser
from services.register.register_answer import RegisterAnswer
from services.register.register_new_user import RegisterNewUser
from services.register.register_user_event import RegisterNewUserEvent
from services.register.register_user_with_referrer import RegisterUserWithReferrer
from services.register.register_user_with_referrer_event import RegisterUserWithReferrerEvent
from services.register.safe_register_with_referrer import SafeRegistrationWithReferrer
from services.start_message import StartMessage
from utlls import BotInstance


async def start_handler(message: types.Message, state: FSMContext):
    """Ответ на команды: start.

    :param message: app_types.Message
    :param state: FSMContext
    """
    user_repository = UserRepository(database)
    registration_repository = RegistrationRepository(
        user_repository,
        AdminMessageRepository(database),
        AyatRepository(database),
    )
    register_new_user = RegisterNewUser(
        BotInstance.get(),
        registration_repository,
    )
    await StateFinishAnswer(
        LoggedSourceMessageAnswer(
            UpdatesLogRepository(
                NatsIntegration([]),
            ),
            message,
            RegisterAnswer(
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
                            user_repository,
                            StartMessage(message.text, user_repository),
                        ),
                        NatsIntegration([]),
                        StartMessage(message.text, user_repository),
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
                    user_repository,
                    UsersRepository(database),
                ),
                message.chat.id,
            ),
        ),
        state,
    ).send()
