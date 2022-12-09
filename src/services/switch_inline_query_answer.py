import json

from app_types.stringable import Stringable
from services.answers.answer import KeyboardInterface


class SwitchInlineQueryKeyboard(KeyboardInterface):
    """Переключение на инлайн поиск."""

    async def generate(self, update: Stringable) -> str:
        """Сборка клавиатуры.

        :param update: Stringable
        :return: str
        """
        return json.dumps({
            'inline_keyboard': [
                [{'text': 'Поиск города', 'switch_inline_query_current_chat': ''}],
            ],
        })
