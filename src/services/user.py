import asyncio

from aiogram.utils.exceptions import BotBlocked, ChatNotFound, UserDeactivated
from loguru import logger

from repository.users.users import UsersRepositoryInterface
from utlls import get_bot_instance

bot = get_bot_instance()


class UsersStatus(object):
    """Статус пользователя."""

    _users_repository: UsersRepositoryInterface
    _unsubscribed_user_chat_ids: list[int] = []

    def __init__(self, users_repository: UsersRepositoryInterface):
        self._users_repository = users_repository

    async def check(self) -> None:
        """Проверить статус."""
        active_users_chat_ids = await self._users_repository.get_active_user_chat_ids()
        user_number = 0
        for index in range(0, len(active_users_chat_ids), 100):
            tasks = []
            for chat_id in active_users_chat_ids[index:index + 100]:
                tasks += [
                    self._try_send_typing_action(user_number, chat_id),
                ]
                user_number += 1
            await asyncio.gather(*tasks)
        if self._unsubscribed_user_chat_ids:
            await self._users_repository.update_status(self._unsubscribed_user_chat_ids, to=False)

    async def _try_send_typing_action(self, user_number: int, chat_id: int) -> None:
        logger.info('{0}, try check id={1}'.format(user_number, chat_id))
        try:
            await bot.send_chat_action(chat_id, 'typing')
        except (ChatNotFound, BotBlocked, UserDeactivated):
            logger.info('id={0} unsubscribed'.format(chat_id))
            self._unsubscribed_user_chat_ids.append(chat_id)
