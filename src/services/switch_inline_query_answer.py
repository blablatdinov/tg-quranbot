import json

from integrations.tg.tg_answers.update import Update
from services.answers.answer import KeyboardInterface


class SwitchInlineQueryKeyboard(KeyboardInterface):

    async def generate(self, update: Update) -> str:
        return json.dumps({
            'inline_keyboard': [
                [{'text': 'Поиск города', 'switch_inline_query_current_chat': ''}]
            ]
        })
