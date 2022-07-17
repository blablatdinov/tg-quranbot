from repository.users.users import UsersRepositoryInterface


class UsersRepositoryMock(UsersRepositoryInterface):

    async def get_active_user_chat_ids(self) -> list[int]:
        return []

    async def update_status(self, chat_ids: list[int], to: bool):
        pass
