from aiogram import types, Bot

from services.answers.interface import AnswerInterface


class KeyboardInterface(object):

    async def generate(self):
        raise NotImplementedError


class DefaultKeyboard(KeyboardInterface):

    async def generate(self):
        return (
            types.ReplyKeyboardMarkup()
            .row(types.KeyboardButton('🎧 Подкасты'))
            .row(types.KeyboardButton('🕋 Время намаза'))
            .row(types.KeyboardButton('🌟 Избранное'), types.KeyboardButton('🔍 Найти аят'))
        )


class FileAnswer(AnswerInterface):

    def __init__(self, debug_mode: bool, telegram_file_id_answer: AnswerInterface, file_link_answer: AnswerInterface):
        self._debug_mode = debug_mode
        self._telegram_file_id_answer = telegram_file_id_answer
        self._file_link_answer = file_link_answer

    async def send(self) -> list[types.Message]:
        if self._debug_mode:
            return await self._file_link_answer.send()

        return await self._telegram_file_id_answer.send()


class TelegramFileIdAnswer(AnswerInterface):

    def __init__(self, bot: Bot, chat_id: int, telegram_file_id: str, keyboard: KeyboardInterface):
        self._chat_id = chat_id
        self._bot = bot
        self._telegram_file_id = telegram_file_id
        self._keyboard = keyboard

    async def send(self):
        message = await self._bot.send_audio(
            chat_id=self._chat_id,
            audio=self._telegram_file_id,
            reply_markup=await self._keyboard.generate(),
        )
        return [message]


class FileLinkAnswer(AnswerInterface):

    def __init__(self, bot: Bot, chat_id: int, link_to_file: str, keyboard: KeyboardInterface):
        self._chat_id = chat_id
        self._bot = bot
        self._link_to_file = link_to_file
        self._keyboard = keyboard

    async def send(self):
        message = await self._bot.send_message(
            chat_id=self._chat_id,
            text=self._link_to_file,
            reply_markup=await self._keyboard.generate(),
        )
        return [message]


class TextAnswer(AnswerInterface):
    """Ответ пользователю."""

    chat_id: int
    message: str
    keyboard: KeyboardInterface

    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        message: str,
        keyboard: KeyboardInterface,
    ):
        self._bot = bot
        self._chat_id = chat_id
        self._message = message
        self._keyboard = keyboard

    async def send(self) -> list[types.Message]:
        """Метод для отправки ответа.

        :return: types.Message
        :raises InternalBotError: if not take _chat_id
        """
        message = await self._bot.send_message(chat_id=self._chat_id, text=self._message, reply_markup=await self._keyboard.generate())
        return [message]
