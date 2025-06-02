import attrs
from integrations.tg.tg_answers import TgAnswer
from metrics.prometheus import BOT_REQUESTS


@attrs.define(frozen=True)
class MeasuredAnswer(TgAnswer):

    _origin: TgAnswer

    async def build(self, update):
        BOT_REQUESTS.inc()
        return await self._origin.build(update)

