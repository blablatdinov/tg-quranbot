from dataclasses import dataclass

from repository.admin_message import AdminMessageRepositoryInterface
from repository.user import UserRepositoryInterface
from services.answer import Answer, AnswerInterface, AnswersList
from services.ayat import AyatServiceInterface
from services.start_message import StartMessageMeta


@dataclass
class RegisterUser(object):
    """Класс осуществляющий регистрацию пользователя."""

    user_repository: UserRepositoryInterface
    admin_messages_repository: AdminMessageRepositoryInterface
    ayat_service: AyatServiceInterface
    chat_id: int
    start_message_meta: StartMessageMeta

    async def service_exists_user(self) -> Answer:
        """Обработка уже зарегестрированного пользователя.

        :return: Answer
        """
        user = await self.user_repository.get_by_chat_id(self.chat_id)
        if user.is_active:
            return Answer(chat_id=self.chat_id, message='Вы уже зарегистрированы')

        return Answer(
            chat_id=self.chat_id,
            message='Рады видеть вас снова, вы продолжите с дня {user_day}'.format(user_day=user.day),
        )

    async def register_with_referrer(
        self,
        referrer_id: int,
        start_message: str,
        formatted_first_ayat: str,
    ) -> AnswersList:
        """Обработка регистрации с реферальным кодом.

        :param referrer_id: int
        :param start_message: str
        :param formatted_first_ayat: str
        :return: AnswersList
        """
        message_for_referrer = 'По вашей реферральной ссылке произошла регистрация'
        referrer_user_record = await self.user_repository.get_by_id(referrer_id)
        return AnswersList(
            Answer(chat_id=self.chat_id, message=start_message),
            Answer(chat_id=self.chat_id, message=formatted_first_ayat),
            Answer(chat_id=referrer_user_record.chat_id, message=message_for_referrer),
        )

    async def get_start_messages(self) -> tuple[str, str]:
        """Получить стартовые сообщение.

        :return: tuple[str, str]
        """
        return (
            await self.admin_messages_repository.get('start'),
            await self.ayat_service.get_formatted_first_ayat(),
        )

    async def register(self) -> AnswerInterface:
        """Entrypoint.

        :returns: str Ответ пользователю
        """
        user_exists = await self.user_repository.exists(self.chat_id)
        if user_exists:
            return await self.service_exists_user()

        await self.user_repository.create(self.chat_id, self.start_message_meta.referrer)
        start_message, formatted_first_ayat = await self.get_start_messages()

        if self.start_message_meta.referrer:
            return await self.register_with_referrer(
                self.start_message_meta.referrer, start_message, formatted_first_ayat,
            )
        return AnswersList(
            Answer(chat_id=self.chat_id, message=start_message),
            Answer(chat_id=self.chat_id, message=formatted_first_ayat),
        )
