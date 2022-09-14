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

    id: int


class CallbackQuery(BaseModel):

    from_: CallbackQueryFrom = Field(..., alias='from')
    message: Message
    data: str


class Update(BaseModel):
    """Класс для парсинга данных обновления от телеграмма."""

    update_id: int
    message: Optional[Message]
    callback_query: Optional[CallbackQuery]

    def chat_id(self):
        try:
            return self.message.chat.id
        except AttributeError:
            return self.callback_query.from_.id
