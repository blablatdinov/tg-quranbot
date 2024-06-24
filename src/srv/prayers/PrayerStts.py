from pyeo import elegant


from typing import Protocol


@elegant
class PrayerStts(Protocol):
    """Объект, рассчитывающий данные кнопки для изменения статуса прочитанности намаза."""

    def user_prayer_id(self) -> int:
        """Рассчитать идентификатор времени намаза пользователя."""

    def change_to(self) -> bool:
        """Рассчитать статус времени намаза пользователя."""