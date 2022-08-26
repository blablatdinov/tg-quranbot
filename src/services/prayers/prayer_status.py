from services.regular_expression import IntableRegularExpression


class PrayerStatus(object):
    """Объект, рассчитывающий данные кнопки для изменения статуса прочитанности намаза."""

    def __init__(self, source: str):
        self._source = source

    def user_prayer_id(self) -> int:
        """Рассчитать идентификатор времени намаза пользователя.

        :return: int
        """
        return int(IntableRegularExpression(self._source))

    def change_to(self) -> bool:
        """Рассчитать статус времени намаза пользователя.

        :return: bool
        """
        return 'not' not in self._source.split('(')[0]
