from aiogram import types

from repository.update_log import UpdatesLogRepositoryInterface


class UpdateLogService(object):

    _updates_log_repository: UpdatesLogRepositoryInterface

    def __init__(self, updates_log_repository: UpdatesLogRepositoryInterface):
        self._updates_log_repository = updates_log_repository

    async def save(self, update: types.Update):
        if update.message:
            await self._updates_log_repository.save_message(update.message)
        elif update.callback_query:
            await self._updates_log_repository.save_callback_query(update.callback_query)
