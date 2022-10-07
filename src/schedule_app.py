import httpx

from app_types.runable import Runable
from integrations.tg.sendable import BulkSendableAnswer
from integrations.tg.tg_answers import TgAnswerInterface, TgChatIdAnswer
from integrations.tg.tg_answers.chat_action import TgChatAction
from integrations.tg.tg_answers.update import Update
from repository.users.users import UsersRepositoryInterface


class TypingAction(TgAnswerInterface):
    """Действие с печатью."""

    def __init__(self, answer: TgAnswerInterface):
        self._origin = answer

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                method=request.method, url=request.url.copy_add_param('action', 'typing'), headers=request.headers,
            )
            for request in await self._origin.build(update)
        ]


class CheckUsersStatus(Runable):
    """Статусы пользователей."""

    def __init__(self, users_repo: UsersRepositoryInterface, empty_answer: TgAnswerInterface):
        self._users_repo = users_repo
        self._empty_answer = empty_answer

    async def run(self):
        """Запуск."""
        chat_ids = await self._users_repo.get_active_user_chat_ids()
        deactivated_users = []
        answers: list[TgAnswerInterface] = [
            TypingAction(
                TgChatIdAnswer(
                    TgChatAction(self._empty_answer),
                    chat_id,
                ),
            )
            for chat_id in chat_ids
        ]
        for response_list in await BulkSendableAnswer(answers).send(Update(update_id=0)):
            for response_dict in response_list:
                if not response_dict['ok']:
                    deactivated_users.append(response_dict['chat_id'])
        await self._users_repo.update_status(list(set(deactivated_users)), to=False)


# class ScheduleApp(Runable):
#
#     async def run(self) -> None:
