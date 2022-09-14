from app_types.stringable import Stringable

AYAT_SEARCH_INPUT_REGEXP = r'\d( |):( |)\d'
GET_PRAYER_TIMES_REGEXP = '(В|в)ремя намаза'
PODCAST_BUTTON = '(П|п)одкасты'


class PrayerReadedEmoji(Stringable):
    """Смайлик для прочитанного намаза."""

    def __str__(self):
        """Строковое представление.

        :return: str
        """
        return '✅'


class PrayerNotReadedEmoji(Stringable):
    """Смайлик для непрочитанного намаза."""

    def __str__(self):
        """Строковое представление.

        :return: str
        """
        return '❌'
