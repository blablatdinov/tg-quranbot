from app_types.stringable import Stringable

AYAT_SEARCH_INPUT_REGEXP = r'\d( |):( |)\d'
GET_PRAYER_TIMES_REGEXP = '(В|в)ремя намаза'
PODCAST_BUTTON = '(П|п)одкасты'


class PrayerReadedEmoji(Stringable):

    def __str__(self):
        return '✅'


class PrayerNotReadedEmoji(Stringable):

    def __str__(self):
        return '❌'
