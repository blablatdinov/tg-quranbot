from pydantic import BaseModel


class Chat(BaseModel):
    """Класс для парсинга данных чата."""

    id: int


class Message(BaseModel):
    """Класс для парсинга данных сообщения."""

    message_id: int
    text: str
    chat: Chat


class Update(BaseModel):
    """Класс для парсинга данных обновления от телеграмма."""

    update_id: int
    message: Message
