from aiogram import types
from aiogram.dispatcher import FSMContext

from db.connection import database
from repository.admin_message import AdminMessageRepository
from repository.ayats.ayat import AyatRepository
from repository.users.registration import RegistrationRepository
from repository.users.user import UserRepository
from repository.users.users import UsersRepository
from services.register_user import RegisterAlreadyExistsUser, RegisterNewUser, RegisterUser, RegisterUserWithReferrer
from services.start_message import get_start_message_query
from utlls import BotInstance


async def start_handler(message: types.Message, state: FSMContext):
    """Ответ на команды: start.

    :param message: app_types.Message
    :param state: FSMContext
    """
    await RegisterUser(
        RegisterNewUser(
            BotInstance.get(),
            message.chat.id,
            RegistrationRepository(
                UserRepository(database),
                AdminMessageRepository(database),
                AyatRepository(database),
            ),
        ),
        RegisterUserWithReferrer(
            BotInstance.get(),
            message.chat.id,
            RegisterNewUser(
                BotInstance.get(),
                message.chat.id,
                RegistrationRepository(
                    UserRepository(database),
                    AdminMessageRepository(database),
                    AyatRepository(database),
                ),
            ),
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
    ).send()

    await state.finish()
