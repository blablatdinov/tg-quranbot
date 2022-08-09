from aiogram import types

from repository.update_log import UpdatesLogRepositoryInterface
from services.answers.interface import AnswerInterface, SingleAnswerInterface
from services.ayats.keyboard_interface import AyatSearchKeyboardInterface
from services.user_prayer_status_interface import UserPrayerStatusInterface


class LoggedAnswer(AnswerInterface):
    """Декоратор для сохранения ответа пользователю.

    Пример использования:

    >>> await LoggedAnswer(
    ...     Answer(message='text')
    ...     UpdatesLogRepository(database),
    ... ).send(182390)
    """

    _origin: AnswerInterface
    _updates_log_repository: UpdatesLogRepositoryInterface

    def __init__(self, answer: AnswerInterface, updates_log_repository: UpdatesLogRepositoryInterface):
        self._origin = answer
        self._updates_log_repository = updates_log_repository

    async def send(self, chat_id: int = None) -> list[types.Message]:
        """Метод для отправки ответа.

        :param chat_id: int
        :return: types.Message
        """
        messages = await self._origin.send(chat_id)
        await self._updates_log_repository.bulk_save_messages(messages)
        return messages

    async def edit_markup(self, message_id: int, chat_id: int = None):
        """Метод для редактирования сообщения.

        :param chat_id: int
        :param message_id: int
        """
        await self._origin.edit_markup(message_id, chat_id)

    def to_list(self) -> list[SingleAnswerInterface]:
        """Метод для конвертации в список.

        :return: list[SingleAnswerInterface]
        """
        return self._origin.to_list()


class LoggedSourceMessageAnswerProcess(AnswerInterface):
    """Декоратор для оборачивания бизнес логики с логированием исходного сообщения."""

    _origin: AnswerInterface
    _updates_log_repository: UpdatesLogRepositoryInterface
    _source_message: types.Message

    def __init__(
        self,
        updates_log_repository: UpdatesLogRepositoryInterface,
        message: types.Message,
        answer: AnswerInterface,
    ):
        self._origin = answer
        self._source_message = message
        self._updates_log_repository = updates_log_repository

    async def send(self, chat_id: int = None) -> list[types.Message]:
        """Метод для отправки ответа.

        :param chat_id: int
        :return: types.Message
        """
        await self._updates_log_repository.save_message(self._source_message)
        return await self._origin.send(chat_id)

    async def edit_markup(self, message_id: int, chat_id: int = None):
        """Метод для редактирования сообщения.

        :param chat_id: int
        :param message_id: int
        """
        await self._origin.edit_markup(message_id, chat_id)

    def to_list(self) -> list[SingleAnswerInterface]:
        """Метод для конвертации в список.

        :return: list[SingleAnswerInterface]
        """
        return self._origin.to_list()


class LoggedSourceCallbackAyatSearchKeyboard(AyatSearchKeyboardInterface):
    """Класс для логгирования данных с клавиатуры."""

    _origin: AyatSearchKeyboardInterface
    _updates_log_repository: UpdatesLogRepositoryInterface
    _source_callback_query: types.CallbackQuery

    def __init__(
        self,
        ayat_search_keyboard: AyatSearchKeyboardInterface,
        updates_log_repository: UpdatesLogRepositoryInterface,
        callback_query: types.CallbackQuery,
    ):
        self._origin = ayat_search_keyboard
        self._source_callback_query = callback_query
        self._updates_log_repository = updates_log_repository

    async def generate(self) -> types.InlineKeyboardMarkup:
        """Сгенерировать клавиатуру.

        :return: types.InlineKeyboardMarkup
        """
        await self._updates_log_repository.save_callback_query(self._source_callback_query)
        return await self._origin.generate()


class LoggedSourceCallbackUserPrayerStatus(UserPrayerStatusInterface):
    """Класс для логгирования данных с клавиатуры."""

    _origin: UserPrayerStatusInterface
    _updates_log_repository: UpdatesLogRepositoryInterface
    _callback_query: types.CallbackQuery

    def __init__(
        self,
        user_prayer_status: UserPrayerStatusInterface,
        updates_log_repository: UpdatesLogRepositoryInterface,
        callback_query: types.CallbackQuery,
    ):
        self._origin = user_prayer_status
        self._updates_log_repository = updates_log_repository
        self._callback_query = callback_query

    async def change(self, is_readed: bool):
        """Метод меняет статус прочитанности намаза.

        :param is_readed: bool
        """
        await self._updates_log_repository.save_callback_query(self._callback_query)
        await self._origin.change(is_readed)

    async def generate_refresh_keyboard(self) -> types.InlineKeyboardMarkup:
        """Сгенерировать обновленную клавиатуру.

        :returns: app_types.InlineKeyboardMarkup
        """
        return await self._origin.generate_refresh_keyboard()


class LoggedSourceCallbackAnswerProcess(AnswerInterface):
    """Декоратор для оборачивания бизнес логики с логированием исходных данных с клавиатуры."""

    _origin: AnswerInterface
    _updates_log_repository: UpdatesLogRepositoryInterface
    _source_callback_query: types.CallbackQuery

    def __init__(
        self,
        updates_log_repository: UpdatesLogRepositoryInterface,
        callback_query: types.CallbackQuery,
        answer: AnswerInterface,
    ):
        self._origin = answer
        self._source_callback_query = callback_query
        self._updates_log_repository = updates_log_repository

    async def send(self, chat_id: int = None) -> types.Message:
        """Метод для отправки ответа.

        :param chat_id: int
        :return: types.Message
        """
        await self._updates_log_repository.save_callback_query(self._source_callback_query)
        return await self._origin.send(chat_id)

    async def edit_markup(self, message_id: int, chat_id: int = None):
        """Метод для редактирования сообщения.

        :param chat_id: int
        :param message_id: int
        """
        await self._origin.edit_markup(message_id, chat_id)

    def to_list(self) -> list[SingleAnswerInterface]:
        """Метод для конвертации в список.

        :return: list[SingleAnswerInterface]
        """
        return self._origin.to_list()
