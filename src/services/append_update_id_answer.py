import httpx

from integrations.tg.tg_answers import TgAnswerInterface
from integrations.tg.tg_answers.update import Update


class AppendUpdateIdAnswer(TgAnswerInterface):

    def __init__(self, debug_mode: bool, answer: TgAnswerInterface):
        self._debug = debug_mode
        self._origin = answer

    async def build(self, update: Update) -> list[httpx.Request]:
        origin_requests = await self._origin.build(update)
        if not self._debug:
            return origin_requests
        new_requests = []
        for request in origin_requests:
            if 'sendMessage' in str(request.url):
                text = request.url.params['text']
                new_requests.append(httpx.Request(
                    method=request.method,
                    url=request.url.copy_set_param(
                        'text',
                        '{0}\n\nUpdate id: {1}'.format(text, update.update_id)
                    ),
                    headers=request.headers,
                ))
        return new_requests
