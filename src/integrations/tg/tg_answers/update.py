from contextlib import suppress
from typing import Optional

from pydantic import BaseModel, Field


class Chat(BaseModel):
    """Класс для парсинга данных чата."""

    id: int


class Message(BaseModel):
    """Класс для парсинга данных сообщения."""

    message_id: int
    text: str
    chat: Chat


class CallbackQueryFrom(BaseModel):
    """Данные отправителя, нажавшего на кнопку."""

    id: int


class CallbackQuery(BaseModel):
    """Данные нажатия на кнопку."""

    from_: CallbackQueryFrom = Field(..., alias='from')
    message: Message
    data: str  # noqa: WPS110


class InlineQuery(BaseModel):

    id: str
    from_: CallbackQueryFrom = Field(..., alias='from')


class Update(BaseModel):
    """Класс для парсинга данных обновления от телеграмма."""

    update_id: int
    message_: Optional[Message] = Field(None, alias='message')
    callback_query_: Optional[CallbackQuery] = Field(None, alias='callback_query')
    inline_query_: Optional[InlineQuery] = Field(None, alias='inline_query')

    def message_id(self) -> int:
        with suppress(AttributeError):
            return self.message().message_id
        with suppress(AttributeError):
            return self.callback_query().message.message_id
        with suppress(AttributeError):
            return self.inline_query().message.message_id
        raise AttributeError

    def chat_id(self) -> int:
        """Идентификатор чата.

        :return: int
        """
        with suppress(AttributeError):
            return self.message().chat.id
        with suppress(AttributeError):
            return self.callback_query().from_.id
        with suppress(AttributeError):
            return self.inline_query().from_.id
        raise AttributeError

    def inline_query(self) -> CallbackQuery:
        if self.inline_query_:
            return self.inline_query_
        raise AttributeError

    def callback_query(self) -> CallbackQuery:
        if self.callback_query_:
            return self.callback_query_
        raise AttributeError

    def message(self) -> Message:
        if self.message_:
            return self.message_
        raise AttributeError


