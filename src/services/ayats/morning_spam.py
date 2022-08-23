from aiogram import types

from app_types.mailing_interface import MailingInterface
from repository.ayats.ayat_morning_content import AyatMorningContentRepositoryInterface
from repository.users.users import UsersRepositoryInterface
from services.answers.answer import TextAnswer
from services.answers.spam_answer_list import SpamAnswerList


class MorningSpam(MailingInterface):
    """Утренняя рассылка."""

    _ayat_spam_repository: AyatMorningContentRepositoryInterface
    _users_repository: UsersRepositoryInterface

    def __init__(
        self,
        ayat_spam_repository: AyatMorningContentRepositoryInterface,
        users_repository: UsersRepositoryInterface,
    ):
        self._ayat_spam_repository = ayat_spam_repository
        self._users_repository = users_repository

    async def send(self) -> list[types.Message]:
        """Отправка.

        :return: list[types.Message]
        """
        spam_contents = await self._ayat_spam_repository.get_morning_content()
        answers = []
        for spam_content in spam_contents:
            answers.append(TextAnswer(
                chat_id=spam_content.chat_id,
                message='{0}\n\n<a href="https://umma.ru{1}">Ссылка на источник</a>'.format(
                    spam_content.content,
                    spam_content.link.split('|')[0],
                ),
            ))

        return await SpamAnswerList(self._users_repository, *answers).send()
