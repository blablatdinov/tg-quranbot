from repository.admin_message import AdminMessageRepositoryInterface


class AdminMessageRepositoryMock(AdminMessageRepositoryInterface):

    async def get(self, key: str) -> str:
        return {
            'start': 'start message_handlers',
        }[key]
