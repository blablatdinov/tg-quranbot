from aiogram import types

from app_types.mailing_interface import MailingInterface
from repository.users.users import UsersRepositoryInterface
from services.ayats.morning_spam import MorningSpam


class MailingWithUpdateUserDays(MailingInterface):
    """Рассылка с обновлением дня у пользователя."""

    def __init__(self, mailing: MorningSpam, users_repository: UsersRepositoryInterface):
        self._origin = mailing
        self._users_repository = users_repository

    async def send(self) -> list[types.Message]:
        """Отправка.

        :return: list[types.Message]
        """
        messages = await self._origin.send()
        await self._users_repository.increment_user_days([message.chat.id for message in messages])
        return messages
