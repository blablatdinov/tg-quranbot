from dataclasses import dataclass
import asyncio
import datetime
from loguru import logger
from aiogram.utils.exceptions import ChatNotFound, BotBlocked, UserDeactivated

from repository.user import UserRepositoryInterface
from utlls import get_bot_instance

bot = get_bot_instance()


@dataclass
class UsersStatus(object):

    user_repository: UserRepositoryInterface

    async def check(self):
        users = await self.user_repository.active_users()
        t = datetime.datetime.now()
        n = 0
        for i in range(0, len(users), 100):
            tasks = []
            for user in users[i:i + 100]:
                tasks += [
                    self.some_task(n, user.chat_id)
                ]
                n += 1
            await asyncio.gather(*tasks)

        logger.info('Time: {0}'.format(datetime.datetime.now() - t))

    async def some_task(self, n, chat_id):
        logger.info('{0}, try check id={1}'.format(n, chat_id))
        try:
            await bot.send_chat_action(chat_id, 'typing')
        except (ChatNotFound, BotBlocked, UserDeactivated):
            logger.info('id={1} unsubscribed'.format(n, chat_id))
            pass
