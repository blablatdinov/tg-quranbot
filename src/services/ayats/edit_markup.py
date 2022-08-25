from aiogram import Bot

from services.answers.answer import KeyboardInterface
from services.markup_edit.interface import MarkupEditInterface


class Markup(MarkupEditInterface):

    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        message_id: int,
        keyboard: KeyboardInterface
    ):
        self._bot = bot
        self._chat_id = chat_id
        self._message_id = message_id
        self._keyboard = keyboard

    async def edit(self):
        await self._bot.edit_message_reply_markup(
            chat_id=self._chat_id,
            message_id=self._message_id,
            reply_markup=await self._keyboard.generate(),
        )
