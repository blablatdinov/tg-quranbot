import enum


class PrayerNames(enum.Enum):
    """Имена намазов."""

    fajr = ('fajr', 'Иртәнге')
    sunrise = ('sunrise', 'Рассвет')
    dhuhr = ('dhuhr', 'Өйлә')
    asr = ('asr', 'Икенде')
    maghrib = ('maghrib', 'Ахшам')
    isha = ("isha'a", 'Ястү')

    @classmethod
    def names(cls) -> tuple[str, ...]:
        """Названия полей.

        :return: tuple[str, ...]
        """
        return tuple(field.name for field in cls.fields_without_sunrise())

    @classmethod
    def fields_without_sunrise(cls) -> tuple['PrayerNames', ...]:
        """Намазы без рассвета.

        Время рассвета важно, т.к. это время завершения периода утреннего намаза
        Однако рассветного намаза нет и отмечать его прочитанность не нужно

        :return: tuple[str, ...]
        """
        return tuple(field for field in cls if field.value[0] != 'sunrise')
