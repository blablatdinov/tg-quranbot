import json

from integrations.nats_integration import SinkInterface
from integrations.tg.sendable import SendableInterface


class LoggedAnswer(SendableInterface):
    """Декоратор логирующий сообщения."""

    def __init__(self, answer: SendableInterface, event_sink: SinkInterface):
        self._origin = answer
        self._event_sink = event_sink

    async def send(self, update: str) -> list[dict]:
        """Отправка.

        :param update: str
        :return: list[dict]
        """
        await self._event_sink.send(
            {
                'messages': [{
                    'message_json': update,
                    'is_unknown': False,
                    'trigger_message_id': None,
                }],
            },
            'Messages.Created',
            1,
        )
        sent_answers = await self._origin.send(update)
        await self._event_sink.send(
            {
                'messages': [
                    {
                        'message_json': json.dumps(answer),
                        'is_unknown': False,
                        'trigger_message_id': json.loads(update)['update_id'],
                    }
                    for answer in sent_answers
                ],
            },
            'Messages.Created',
            1,
        )
        return sent_answers
