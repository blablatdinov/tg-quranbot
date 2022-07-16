import datetime

from repository.users.user_actions import UserAction, UserActionEnum, UserActionRepositoryInterface


class UserActionRepositoryMock(UserActionRepositoryInterface):

    storage: list[UserAction]

    def __init__(self) -> None:
        self.storage = []

    async def create_user_action(self, chat_id: int, action: UserActionEnum):
        self.storage.append(
            UserAction(
                date_time=datetime.datetime.now(),
                action=action,
                chat_id=chat_id,
            ),
        )
