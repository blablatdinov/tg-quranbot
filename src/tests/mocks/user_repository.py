import random
import uuid
from typing import Optional

from exceptions.content_exceptions import UserNotFoundError
from repository.users.user import User, UserRepositoryInterface


class UserRepositoryMock(UserRepositoryInterface):
    storage: list[User] = []

    async def create(self, chat_id: int, referrer_id: Optional[int] = None):
        user_id = random.randint(0, 100)
        self.storage.append(
            User(
                id=user_id,
                is_active=True,
                day=2,
                referrer=referrer_id,
                chat_id=chat_id,
                city_id=uuid.uuid4(),
            ),
        )

    async def get_by_id(self, user_id: int) -> User:
        return list(
            filter(
                lambda user: user.legacy_id == user_id, self.storage,
            ),
        )[0]

    async def get_by_chat_id(self, chat_id: int) -> User:
        users = [
            user
            for user in self.storage
            if user.chat_id == chat_id
        ]
        if not users:
            raise UserNotFoundError
        return users[0]

    async def exists(self, chat_id: int):
        return chat_id in {user.chat_id for user in self.storage}

    async def active_users(self):
        return list(filter(lambda user: user.is_active, self.storage))

    async def update_referrer(self, chat_id: int, referrer_id: int):
        for storage_index, user in enumerate(self.storage):
            if user.chat_id == chat_id:
                self.storage[storage_index].referrer = referrer_id
