from asyncpg import Connection

from repository.update_log import UpdatesLogRepositoryInterface


class MailingRepository(object):

    def __init__(self, connection: Connection, messages_repository: UpdatesLogRepositoryInterface):
        self._connection = connection
        self._messages_repository = messages_repository

    async def create_mailing(self, messages):
        query = "INSERT INTO bot_init_mailing (id, is_cleaned) values (default, 'f') RETURNING id"
        row = await self._connection.fetchrow(query)
        await self._messages_repository.bulk_save_messages(messages, row['id'])
