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


class Update(BaseModel):
    """Класс для парсинга данных обновления от телеграмма."""

    update_id: int
    _message: Optional[Message] = Field(None, alias='message')
    _callback_query: Optional[CallbackQuery] = Field(None, alias='callback_query')

    def message_id(self) -> int:
        """Идентификатор сообщения.

        :return: int
        """
        try:
            return self.message().message_id
        except AttributeError:
            return self.callback_query().message.message_id

    def chat_id(self) -> int:
        """Идентификатор чата.

        :return: int
        """
        try:
            return self.message().chat.id
        except AttributeError:
            return self.callback_query().from_.id

    def callback_query(self) -> CallbackQuery:
        """Данные с инлайн кнопки.

        :return: CallbackQuery
        :raises AttributeError: if callback query not founc
        """
        if self._callback_query:
            return self._callback_query
        raise AttributeError

    def message(self) -> Message:
        """Сообщение.

        :return: Message
        :raises AttributeError: if message not founc
        """
        if self._message:
            return self._message
        raise AttributeError
