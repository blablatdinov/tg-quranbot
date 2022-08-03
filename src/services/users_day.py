from repository.users.users import UsersRepositoryInterface
from services.ayats.morning_spam import MorningSpam


class MailingWithUpdateUserDays(object):

    def __init__(self, mailing: MorningSpam, users_repository: UsersRepositoryInterface):
        self._origin = mailing
        self._users_repository = users_repository

    async def send(self):
        messages = await self._origin.send()
        await self._users_repository.increment_user_days([message.chat.id for message in messages])
