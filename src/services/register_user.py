from dataclasses import dataclass

from repository.user import UserRepositoryInterface


@dataclass
class RegisterUser(object):
    repository: UserRepositoryInterface
    chat_id: int

    def __call__(self) -> str:
        self.repository.create(self.chat_id)
        return 'user created'
