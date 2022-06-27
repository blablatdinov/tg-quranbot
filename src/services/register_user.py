from dataclasses import dataclass

from repository.user import UserRepositoryInterface


@dataclass
class RegisterUser(object):
    """Класс осуществляющий регистрацию пользователя."""

    repository: UserRepositoryInterface
    chat_id: int

    def __call__(self) -> str:
        """Entrypoint.

        :returns: str Ответ пользователю
        """
        self.repository.create(self.chat_id)
        return 'user created'
