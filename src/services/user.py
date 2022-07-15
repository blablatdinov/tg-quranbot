import asyncio
from dataclasses import dataclass

from aiogram.utils.exceptions import BotBlocked, ChatNotFound, UserDeactivated
from loguru import logger

from repository.user import UserRepositoryInterface
from utlls import get_bot_instance

bot = get_bot_instance()


@dataclass
class UsersStatus(object):
    """Статус пользователя."""

    user_repository: UserRepositoryInterface

    async def check(self):
        """Проверить статус."""
        users = await self.user_repository.active_users()
        user_number = 0
        for index in range(0, len(users), 100):
            tasks = []
            for user in users[index:index + 100]:
                tasks += [
                    self._try_send_typing_action(user_number, user.chat_id),
                ]
                user_number += 1
            await asyncio.gather(*tasks)

    async def _try_send_typing_action(self, user_number: int, chat_id: int) -> None:
        logger.info('{0}, try check id={1}'.format(user_number, chat_id))
        try:
            await bot.send_chat_action(chat_id, 'typing')
        except (ChatNotFound, BotBlocked, UserDeactivated):
            logger.info('id={0} unsubscribed'.format(chat_id))
