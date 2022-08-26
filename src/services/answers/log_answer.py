from aiogram import types

from repository.update_log import UpdatesLogRepositoryInterface
from services.answers.interface import AnswerInterface
from services.markup_edit.interface import MarkupEditInterface


class LoggedAnswer(AnswerInterface):
    """Декоратор для сохранения ответа пользователю.

    Пример использования:

    >>> await LoggedAnswer(
    ...     TextAnswer(BotInstance.get(), 928734, 'text', DefaultKeyboard())
    ...     UpdatesLogRepository(NatsIntegration([])),
    ... ).send()
    """

    _origin: AnswerInterface
    _updates_log_repository: UpdatesLogRepositoryInterface

    def __init__(self, answer: AnswerInterface, updates_log_repository: UpdatesLogRepositoryInterface):
        self._origin = answer
        self._updates_log_repository = updates_log_repository

    async def send(self) -> list[types.Message]:
        """Метод для отправки ответа.

        :return: types.Message
        """
        messages = await self._origin.send()
        await self._updates_log_repository.save_messages(messages)
        return messages


class LoggedSourceMessageAnswer(AnswerInterface):
    """Декоратор для оборачивания бизнес логики с логированием исходного сообщения."""

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
        messages = await self._origin.send()
        await self._updates_log_repository.save_messages_with_trigger_message(
            [self._source_message] + messages, self._source_message.message_id,
        )
        return messages


class LoggedAnswerByCallback(AnswerInterface):

    def __init__(
        self,
        updates_log_repository: UpdatesLogRepositoryInterface,
        callback_query: types.CallbackQuery,
        answer: AnswerInterface,
    ):
        self._origin = answer
        self._source_callback_query = callback_query
        self._updates_log_repository = updates_log_repository

    async def send(self, chat_id: int = None) -> list[types.Message]:
        """Метод для отправки ответа.

        :param chat_id: int
        :return: types.Message
        """
        messages = await self._origin.send()
        await self._updates_log_repository.save_callback_query(self._source_callback_query)
        await self._updates_log_repository.save_messages(messages)
        return messages


class LoggedSourceCallback(MarkupEditInterface):
    """Класс для логгирования данных с клавиатуры."""

    def __init__(
        self,
        ayat_search_keyboard: MarkupEditInterface,
        updates_log_repository: UpdatesLogRepositoryInterface,
        callback_query: types.CallbackQuery,
    ):
        self._origin = ayat_search_keyboard
        self._source_callback_query = callback_query
        self._updates_log_repository = updates_log_repository

    async def edit(self) -> None:
        """Сгенерировать клавиатуру."""
        await self._updates_log_repository.save_callback_query(self._source_callback_query)
        await self._origin.edit()
