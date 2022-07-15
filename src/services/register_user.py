from repository.admin_message import AdminMessageRepository
from repository.ayats.ayat import AyatRepository, AyatRepositoryInterface
from repository.user import UserRepository
from repository.user_actions import UserActionEnum, UserActionRepository
from repository.user_registration_repository import UserRegistrationRepository, UserRegistrationRepositoryInterface
from services.answer import Answer, AnswerInterface, AnswersList
from services.start_message import StartMessageMeta, get_start_message_query


class RegisterUser(object):
    """Класс осуществляющий регистрацию пользователя."""

    _user_registration_repository: UserRegistrationRepositoryInterface
    _ayat_repository: AyatRepositoryInterface
    _chat_id: int
    _start_message_meta: StartMessageMeta

    def __init__(
        self,
        user_registration_repository: UserRegistrationRepositoryInterface,
        ayat_repository: AyatRepositoryInterface,
        chat_id: int,
        start_message_meta: StartMessageMeta,
    ):
        self._user_registration_repository = user_registration_repository
        self._ayat_repository = ayat_repository
        self._chat_id = chat_id
        self._start_message_meta = start_message_meta

    async def register(self) -> AnswerInterface:
        """Entrypoint.

        :returns: str Ответ пользователю
        """
        user_exists = await self._user_registration_repository.check_user_exists(self._chat_id)
        if user_exists:
            return await self.service_exists_user()

        await self.creating_user()
        start_message, formatted_first_ayat = await self.get_start_messages()

        if self._start_message_meta.referrer:
            return await self.register_with_referrer(
                self._start_message_meta.referrer, start_message, formatted_first_ayat,
            )
        return AnswersList(
            Answer(chat_id=self._chat_id, message=start_message),
            Answer(chat_id=self._chat_id, message=formatted_first_ayat),
        )

    async def creating_user(self) -> None:
        """Создание пользователя."""
        await self._user_registration_repository.create_user(self._chat_id, self._start_message_meta.referrer)
        await self._user_registration_repository.create_user_action(self._chat_id, UserActionEnum.SUBSCRIBED)

    async def service_exists_user(self) -> Answer:
        """Обработка уже зарегестрированного пользователя.

        :return: Answer
        """
        user = await self._user_registration_repository.get_user_by_chat_id(self._chat_id)
        if user.is_active:
            return Answer(chat_id=self._chat_id, message='Вы уже зарегистрированы')

        await self._user_registration_repository.create_user_action(self._chat_id, UserActionEnum.REACTIVATED)
        return Answer(
            chat_id=self._chat_id,
            message='Рады видеть вас снова, вы продолжите с дня {user_day}'.format(user_day=user.day),
        )

    async def register_with_referrer(
        self,
        referrer_id: int,
        start_message: str,
        formatted_first_ayat: str,
    ) -> AnswersList:
        """Создание сообщения после регистрации, если пользователь зарегистрировался по реф. ссылке.

        :param referrer_id: int
        :param start_message: str
        :param formatted_first_ayat: str
        :return: AnswersList
        """
        message_for_referrer = 'По вашей реферральной ссылке произошла регистрация'
        referrer_user_record = await self._user_registration_repository.get_by_id(referrer_id)
        return AnswersList(
            Answer(chat_id=self._chat_id, message=start_message),
            Answer(chat_id=self._chat_id, message=formatted_first_ayat),
            Answer(chat_id=referrer_user_record.chat_id, message=message_for_referrer),
        )

    async def get_start_messages(self) -> tuple[str, str]:
        """Получить стартовые сообщение.

        :return: tuple[str, str]
        """
        return (
            await self._user_registration_repository.get_admin_message('start'),
            str(await self._ayat_repository.get(1)),
        )


async def get_register_user_instance(connection, chat_id: int, message: str) -> RegisterUser:
    """Возвращает объект для регистрации пользователя.

    :param chat_id: int
    :param connection: int
    :param message: str
    :returns: RegisterUser
    """
    return RegisterUser(
        user_registration_repository=UserRegistrationRepository(
            UserRepository(connection),
            UserActionRepository(connection),
            AdminMessageRepository(connection),
        ),
        ayat_repository=AyatRepository(connection),
        chat_id=chat_id,
        start_message_meta=get_start_message_query(message),
    )
