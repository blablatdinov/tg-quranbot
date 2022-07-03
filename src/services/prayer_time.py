import datetime
from dataclasses import dataclass, field

from repository.prayer_time import Prayer, PrayerNames, PrayerTimeRepositoryInterface, UserPrayer
from repository.user import UserRepositoryInterface


class PrayerTimesInterface(object):
    """Интерфейс для работы с временами намазов пользователя."""

    prayer_times_repository: PrayerTimeRepositoryInterface
    chat_id: int
    user_repository: UserRepositoryInterface
    prayers: list[Prayer]

    async def get(self) -> 'PrayerTimes':
        """Получить времена намазов пользователя.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


@dataclass
class UserPrayerTimes(object):
    """Класс для работы с временами намазов пользователя."""

    prayer_times: PrayerTimesInterface
    date_time: datetime.datetime

    async def get_or_create_user_prayer_times(self) -> list[UserPrayer]:
        """Получить или создать времена намазов пользователя.

        :returns: list[UserPrayer]
        """
        prayers_without_sunrise = filter(
            lambda prayer: prayer.name != PrayerNames.SUNRISE,
            self.prayer_times.prayers,
        )
        prayers_without_sunrise_ids = [
            prayer.id
            for prayer in prayers_without_sunrise
        ]
        user_prayers = await self.prayer_times.prayer_times_repository.get_user_prayer_times(
            prayers_without_sunrise_ids,
            self.prayer_times.chat_id,
            datetime.datetime.now(),
        )
        if not user_prayers:
            user = await self.prayer_times.user_repository.get_by_chat_id(self.prayer_times.chat_id)
            user_prayers = await self.prayer_times.prayer_times_repository.create_user_prayer_times(
                prayer_ids=prayers_without_sunrise_ids,
                user_id=user.id,
            )

        return user_prayers


@dataclass
class PrayerTimes(PrayerTimesInterface):
    """Класс для работы с временами намазов."""

    prayer_times_repository: PrayerTimeRepositoryInterface
    chat_id: int
    user_repository: UserRepositoryInterface
    prayers: list[Prayer] = field(default_factory=list)

    async def get(self) -> 'PrayerTimes':
        """Получить экземпляр класса.

        :returns: PrayerTimes
        """
        user = await self.user_repository.get_by_chat_id(self.chat_id)
        prayers = await self.prayer_times_repository.get_prayer_times_for_date(
            chat_id=self.chat_id,
            target_datetime=datetime.datetime.now(),
            city_id=user.city_id,
        )
        return PrayerTimes(
            prayers=prayers,
            prayer_times_repository=self.prayer_times_repository,
            chat_id=self.chat_id,
            user_repository=self.user_repository,
        )

    def __str__(self) -> str:
        """Форматировать экземпляр класса в ответ.

        :returns: AnswerInterface
        """
        time_format = '%H:%M'
        template = (
            'Время намаза для г. {city_name} ({date})\n\n'
            + 'Иртәнге: {fajr_prayer_time}\n'
            + 'Восход: {sunrise_prayer_time}\n'
            + 'Өйлә: {dhuhr_prayer_time}\n'
            + 'Икенде: {asr_prayer_time}\n'
            + 'Ахшам: {magrib_prayer_time}\n'
            + 'Ястү: {ishaa_prayer_time}'
        )
        return template.format(
            city_name=self.prayers[0].city,
            date=self.prayers[0].day.strftime('%d.%m.%Y'),
            fajr_prayer_time=self.prayers[0].time.strftime(time_format),
            sunrise_prayer_time=self.prayers[1].time.strftime(time_format),
            dhuhr_prayer_time=self.prayers[2].time.strftime(time_format),
            asr_prayer_time=self.prayers[3].time.strftime(time_format),
            magrib_prayer_time=self.prayers[4].time.strftime(time_format),
            ishaa_prayer_time=self.prayers[5].time.strftime(time_format),
        )
