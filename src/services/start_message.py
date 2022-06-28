from typing import Optional

from pydantic import BaseModel, ValidationError


class StartMessageMeta(BaseModel):
    """Мета информация стартового сообщения."""

    referrer: Optional[int] = None


def get_start_message_query(message: str) -> StartMessageMeta:
    """Получить метаинформацию из стартового сообщения.

    :param message: str
    :return: StartMessageMeta
    """
    splitted_message = message.split(' ')
    try:
        return parse_start_message(splitted_message)
    except Exception:
        return StartMessageMeta(referrer=None)


def parse_start_message(splitted_message: list[str]) -> StartMessageMeta:
    """Распарсить стартовое сообщение.

    :param splitted_message: str
    :return: StartMessageMeta
    """
    if len(splitted_message) == 1:
        return StartMessageMeta(referrer=None)
    message_raw_meta = ' '.join(splitted_message[1:])
    try:
        return StartMessageMeta.parse_raw(message_raw_meta)
    except ValidationError:
        return StartMessageMeta(referrer=int(splitted_message[1]))
