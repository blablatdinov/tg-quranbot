from app_types.stringable import Stringable
from repository.user_prayers_interface import UserPrayer


class UserPrayersButtonCallback(Stringable):
    """Кнопка клавиатуры времен намазов."""

    def __init__(self, user_prayer: UserPrayer):
        self._user_prayer = user_prayer

    def __str__(self):
        """Строковое представление.

        :return: str
        """
        if self._user_prayer.is_readed:
            return 'mark_not_readed({0})'.format(self._user_prayer.id)
        return 'mark_readed({0})'.format(self._user_prayer.id)
