from repository.mailing import MailingRepository
from repository.users.users import UsersRepositoryInterface
from services.answers.answer import DefaultKeyboard, TextAnswer
from services.answers.spam_answer_list import SavedSpamAnswerList, SpamAnswerList
from utlls import BotInstance


class MailingCreatedEvent(object):
    """Класс обработывающий события о создании рассылки."""

    event_name = 'Mailing.Created'
    _users_repository: UsersRepositoryInterface

    def __init__(self, users_repository: UsersRepositoryInterface, mailing_repository: MailingRepository):
        self._users_repository = users_repository
        self._mailing_repository = mailing_repository

    async def handle_event(self, event):
        """Обработка события.

        :param event: dict
        """
        active_user_chat_ids = await self._users_repository.get_active_user_chat_ids()
        await SavedSpamAnswerList(
            SpamAnswerList(
                self._users_repository,
                *[
                    TextAnswer(
                        BotInstance.get(),
                        active_user_chat_id,
                        event['text'],
                        DefaultKeyboard(),
                    )
                    for active_user_chat_id in active_user_chat_ids
                ],
            ),
            self._mailing_repository,
        ).send()
