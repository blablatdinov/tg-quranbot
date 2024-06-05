from app_types.update import Update
from integrations.tg.chat_id import ChatId
from services.answers.answer import KeyboardInterface
from srv.prayers.exist_user_prayers import ExistUserPrayers
from srv.prayers.prayer_date import PrayerDate


import attrs
from databases import Database
from pyeo import elegant


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class PrayersProtectDouble(KeyboardInterface):
    """Предохранитель от дублей во временах намаза."""

    _origin: KeyboardInterface
    _pgsql: Database
    _chat_id: ChatId
    _date: PrayerDate

    @override
    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        :raises ValueError: Пользователь запросил времена дважды
        """
        exist_prayers = ExistUserPrayers(self._pgsql, self._chat_id, await self._date.parse(update))
        async with self._pgsql.transaction():
            origin_val = await self._origin.generate(update)
            expected_prayers_count = 5
            if len(await exist_prayers.fetch()) > expected_prayers_count:
                msg = 'Prayers doubled'
                raise ValueError(msg)
        return origin_val