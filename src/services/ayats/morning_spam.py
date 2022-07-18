from repository.ayats.ayat_spam import AyatSpamRepositoryInterface
from repository.users.users import UsersRepositoryInterface
from services.answer import Answer, SpamAnswerList


class MorningSpam(object):
    """Утренняя рассылка."""

    _ayat_spam_repository: AyatSpamRepositoryInterface
    _users_repository: UsersRepositoryInterface

    def __init__(self, ayat_spam_repository: AyatSpamRepositoryInterface, users_repository: UsersRepositoryInterface):
        self._ayat_spam_repository = ayat_spam_repository
        self._users_repository = users_repository

    async def send(self) -> None:
        """Отправка."""
        spam_contents = await self._ayat_spam_repository.get_content_for_spam()
        answers = []
        for spam_content in spam_contents:
            answers.append(Answer(
                chat_id=spam_content.chat_id,
                message='{0}\n\n<a href="https://umma.ru{1}">Ссылка на источник</a>'.format(
                    spam_content.content,
                    spam_content.link.split('|')[0],
                ),
            ))

        await SpamAnswerList(self._users_repository, *answers).send()
