import asyncio

from aiogram.utils.exceptions import BotBlocked, ChatNotFound, UserDeactivated

from repository.users.users import UsersRepositoryInterface
from services.answers.answer import Answer
from services.answers.interface import AnswerInterface, SingleAnswerInterface


class SpamAnswerList(list, AnswerInterface):  # noqa: WPS600
    """Список ответов для рассылки.

    Отправляет сообщения пачками
    """

    _users_repository: UsersRepositoryInterface
    _unsubscriber_user_chat_ids: list[int] = []

    def __init__(self, users_repository: UsersRepositoryInterface, *args: AnswerInterface) -> None:
        self._users_repository = users_repository
        super().__init__(args)

    async def send(self, chat_id: int = None) -> None:
        """Метод для отправки ответа.

        :param chat_id: int
        """
        self._validate()
        for index in range(0, len(self), 100):
            tasks = []
            for answer in self[index:index + 100]:
                tasks.append(self._send_one_answer(answer))

            await asyncio.gather(*tasks)

        if self._unsubscriber_user_chat_ids:
            await self._users_repository.update_status(self._unsubscriber_user_chat_ids, to=False)

    async def edit_markup(self, message_id: int, chat_id: int = None):
        """Метод для редактирования сообщения.

        :param chat_id: int
        :param message_id: int
        """
        for elem in self:
            await elem.edit_markup(chat_id)

    def to_list(self) -> list[SingleAnswerInterface]:
        """Форматировать в строку из элементов.

        :returns: list[Answer]
        """
        return self

    async def _send_one_answer(self, answer: Answer):
        try:
            await answer.send()
        except (ChatNotFound, BotBlocked, UserDeactivated):
            # answer._chat_id is not None already checked in self._validate method
            self._unsubscriber_user_chat_ids.append(answer.chat_id)  # type: ignore

    def _validate(self) -> None:
        # cycle import protect
        from exceptions import InternalBotError  # noqa: WPS433
        answers_chat_ids = {answer.chat_id for answer in self}
        if None in answers_chat_ids:
            raise InternalBotError
