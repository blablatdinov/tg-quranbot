import json

import httpx

from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.tg_answers import TgAnswerInterface
from integrations.tg.tg_answers.update import Update
from services.debug_answer import DebugAnswer


class InlineQueryAnswer(TgAnswerInterface):

    def __init__(self, answer: TgAnswerInterface):
        self._origin = answer

    async def build(self, update: Update) -> list[httpx.Request]:
        try:
            update.inline_query()
        except AttributeError:
            raise NotProcessableUpdateError
        origin_requests = await DebugAnswer(self._origin).build(update)
        return [
            httpx.Request(
                origin_requests[0].method,
                (
                    origin_requests[0]
                    .url
                    .join('answerInlineQuery')
                    .copy_add_param('inline_query_id', update.inline_query().id)
                    .copy_add_param(
                        'results',
                        json.dumps(
                            [
                                {
                                    'id': '1',
                                    'type': 'article',
                                    'title': 'wow',
                                    'input_message_content': {'message_text': 'weoijo'}
                                },
                                {
                                    'id': '2',
                                    'type': 'article',
                                    'title': 'wow2',
                                    'input_message_content': {'message_text': 'weoijo'}
                                },
                                {
                                    'id': '3',
                                    'type': 'article',
                                    'title': 'wow3',
                                    'input_message_content': {'message_text': 'weoijo'}
                                },
                                {
                                    'id': '4',
                                    'type': 'article',
                                    'title': 'wow4',
                                    'input_message_content': {'message_text': 'weoijo'}
                                },
                            ]
                        )
                    )
                )
            )
        ]
