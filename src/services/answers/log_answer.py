from aiogram import types

from repository.update_log import UpdatesLogRepositoryInterface
from services.answers.interface import AnswerInterface, SingleAnswerInterface


class LoggedAnswer(AnswerInterface):

    _origin: AnswerInterface
    _updates_log_repository: UpdatesLogRepositoryInterface

    def __init__(self, answer: AnswerInterface, updates_log_repository: UpdatesLogRepositoryInterface):
        self._origin = answer
        self._updates_log_repository = updates_log_repository

    async def send(self, chat_id: int = None):
        """Метод для отправки ответа.

        :param chat_id: int
        :raises NotImplementedError: if not implement
        """
        message = await self._origin.send(chat_id)
        await self._updates_log_repository.save_message(message)
        return message

    async def edit_markup(self, message_id: int, chat_id: int = None):
        """Метод для редактирования сообщения.

        :param chat_id: int
        :param message_id: int
        :raises NotImplementedError: if not implement
        """
        await self._origin.edit_markup(message_id, chat_id)

    def to_list(self) -> list[SingleAnswerInterface]:
        """Метод для конвертации в список.

        :raises NotImplementedError: if not implement
        """
        return self._origin.to_list()


class LoggedSourceMessageAnswer(AnswerInterface):

    _origin: AnswerInterface
    _updates_log_repository: UpdatesLogRepositoryInterface

    def __init__(self, updates_log_repository: UpdatesLogRepositoryInterface, message: types.Message, answer: AnswerInterface):
        self._origin = answer
        self._source_message = message
        self._updates_log_repository = updates_log_repository

    async def send(self, chat_id: int = None):
        """Метод для отправки ответа.

        :param chat_id: int
        :raises NotImplementedError: if not implement
        """
        await self._updates_log_repository.save_message(self._source_message)
        message = await self._origin.send(chat_id)
        return message

    async def edit_markup(self, message_id: int, chat_id: int = None):
        """Метод для редактирования сообщения.

        :param chat_id: int
        :param message_id: int
        :raises NotImplementedError: if not implement
        """
        await self._origin.edit_markup(message_id, chat_id)

    def to_list(self) -> list[SingleAnswerInterface]:
        """Метод для конвертации в список.

        :raises NotImplementedError: if not implement
        """
        return self._origin.to_list()
