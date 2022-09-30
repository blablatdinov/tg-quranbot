from contextlib import suppress
from typing import Optional

from pydantic import BaseModel, Field


class Chat(BaseModel):
    """Класс для парсинга данных чата."""

    id: int


class Location(BaseModel):
    """Координаты."""

    latitude: float
    longitude: float


class Message(BaseModel):
    """Класс для парсинга данных сообщения."""

    message_id: int
    text_: Optional[str] = Field(None, alias='text')
    chat: Chat
    location_: Optional[Location] = Field(None, alias='location')

    def location(self) -> Location:
        """Местоположение.

        :return: Location
        :raises AttributeError: if update hasn't location
        """
        if not self.location_:
            raise AttributeError
        return self.location_

    def text(self) -> str:
        """Текст сообщения.

        :return: str
        :raises AttributeError: if update hasn't location
        """
        if not self.text_:
            raise AttributeError
        return self.text_


class CallbackQueryFrom(BaseModel):
    """Данные отправителя, нажавшего на кнопку."""

    id: int


class CallbackQuery(BaseModel):
    """Данные нажатия на кнопку."""

    from_: CallbackQueryFrom = Field(..., alias='from')
    message: Message
    data: str  # noqa: WPS110


class InlineQuery(BaseModel):
    """Инлайн запрос."""

    id: str
    from_: CallbackQueryFrom = Field(..., alias='from')
    query_: str = Field(..., alias='query')

    def query(self) -> str:
        """Запрос.

        :return: str
        """
        return self.query_


class Update(BaseModel):
    """Класс для парсинга данных обновления от телеграмма."""

    update_id: int
    message_: Optional[Message] = Field(None, alias='message')
    callback_query_: Optional[CallbackQuery] = Field(None, alias='callback_query')
    inline_query_: Optional[InlineQuery] = Field(None, alias='inline_query')

    def message_id(self) -> int:
        """Идентификатор сообщения.

        :return: int
        :raises AttributeError: if update hasn't message_id
        """
        with suppress(AttributeError):
            return self.message().message_id
        with suppress(AttributeError):
            return self.callback_query().message.message_id
        raise AttributeError

    def chat_id(self) -> int:
        """Идентификатор чата.

        :return: int
        :raises AttributeError: if update hasn't chat_id
        """
        with suppress(AttributeError):
            return self.message().chat.id
        with suppress(AttributeError):
            return self.callback_query().from_.id
        with suppress(AttributeError):
            return self.inline_query().from_.id
        raise AttributeError

    def inline_query(self) -> InlineQuery:
        """Инлайн запрос.

        :return: InlineQuery
        :raises AttributeError: if update hasn't inline query
        """
        if self.inline_query_:
            return self.inline_query_
        raise AttributeError

    def callback_query(self) -> CallbackQuery:
        """Данные с инлайн кнопки.

        :return: CallbackQuery
        :raises AttributeError: if callback query not founc
        """
        if self.callback_query_:
            return self.callback_query_
        raise AttributeError

    def message(self) -> Message:
        """Сообщение.

        :return: Message
        :raises AttributeError: if message not founc
        """
        if self.message_:
            return self.message_
        raise AttributeError
