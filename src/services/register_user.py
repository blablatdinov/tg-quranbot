from dataclasses import dataclass

from repository.user import UserRepositoryInterface


@dataclass
class RegisterUser(object):
    """Класс осуществляющий регистрацию пользователя."""

    repository: UserRepositoryInterface
    chat_id: int

    async def register(self) -> str:
        """Entrypoint.

        :returns: str Ответ пользователю
        """
        user_exists = await self.repository.exists(self.chat_id)
        if user_exists:
            user = await self.repository.get(self.chat_id)
            if user.is_active:
                return 'user already registered'
            else:
                return 'user active again'
        await self.repository.create(self.chat_id)
        return 'user created'
