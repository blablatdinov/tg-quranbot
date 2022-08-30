import datetime

from aiogram import Bot, types
from loguru import logger

from exceptions.content_exceptions import UserHasNotCityIdError
from repository.prayer_time import Prayer, PrayerNames, PrayerTimeRepositoryInterface, UserPrayer
from repository.users.user import UserRepositoryInterface
from services.answers.answer import KeyboardInterface, TextAnswer
from services.answers.interface import AnswerInterface
from services.prayers.prayer_status import PrayerStatus


class PrayerTimesInterface(object):
    """Интерфейс для времен намаза."""

    async def as_list(self) -> list[Prayer]:
        """Представить объект как список.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class UserPrayerTimesInterface(object):
    """Интерфейс для времен намазов пользователя."""

    async def as_list(self) -> list[UserPrayer]:
        """Представить объект как список.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class PrayerTimes(PrayerTimesInterface):
    """Класс для работы с временами намаза."""

    def __init__(
        self,
        chat_id: int,
        user_repository: UserRepositoryInterface,
        prayer_times_repository: PrayerTimeRepositoryInterface,
        date: datetime.date,
    ):
        self._chat_id = chat_id
        self._user_repository = user_repository
        self._prayer_times_repository = prayer_times_repository
        self._date = date

    async def as_list(self) -> list[Prayer]:
        """Представить объект как список.

        :return: list[Prayer]
        :raises UserHasNotCityIdError: если у пользователя не установлен город
        """
        user = await self._user_repository.get_by_chat_id(self._chat_id)
        if not user.city_id:
            raise UserHasNotCityIdError
        return await self._prayer_times_repository.get_prayer_times_for_date(
            chat_id=self._chat_id,
            target_datetime=self._date,
            city_id=user.city_id,
        )


class UserPrayerTimes(UserPrayerTimesInterface):
    """Класс для работы с временами намаза пользователей."""

    def __init__(
        self,
        chat_id: int,
        prayer_times: PrayerTimesInterface,
        user_repository: UserRepositoryInterface,
        prayer_times_repo: PrayerTimeRepositoryInterface,
    ):
        self._chat_id = chat_id
        self._prayer_times = prayer_times
        self._user_repository = user_repository
        self._prayer_times_repository = prayer_times_repo

    async def as_list(self) -> list[UserPrayer]:
        """Представить объект как список.

        :return: list[UserPrayer]
        """
        prayer_ids = [prayer.id for prayer in await self._prayer_times.as_list()]
        user_prayers = await self._prayer_times_repository.get_user_prayer_times(
            prayer_ids,
            self._chat_id,
            datetime.datetime.now(),
        )
        logger.info('Search result: {0}'.format(user_prayers))
        if not user_prayers:
            logger.info('User prayers not found. Creating...')
            user = await self._user_repository.get_by_chat_id(self._chat_id)
            user_prayers = await self._prayer_times_repository.create_user_prayer_times(
                prayer_ids=prayer_ids,
                user_id=user.chat_id,
            )

        return user_prayers


class EditedUserPrayerTimes(UserPrayerTimesInterface):
    """Измененный статус времени намаза пользвоателя."""

    def __init__(
        self,
        user_prayer_times: UserPrayerTimesInterface,
        prayer_times_repo: PrayerTimeRepositoryInterface,
        prayer_status: PrayerStatus,
    ):
        self._origin = user_prayer_times
        self._prayer_times_repo = prayer_times_repo
        self._user_prayer_status = prayer_status

    async def as_list(self) -> list[UserPrayer]:
        """Представить объект как список.

        :return: list[UserPrayer]
        """
        await self._prayer_times_repo.change_user_prayer_time_status(
            self._user_prayer_status.user_prayer_id(), self._user_prayer_status.change_to(),
        )
        return await self._origin.as_list()


class PrayersWithoutSunrise(PrayerTimesInterface):
    """Времена намаза без времени восхода."""

    def __init__(self, prayer_times: PrayerTimesInterface):
        self._origin = prayer_times

    async def as_list(self) -> list[Prayer]:
        """Представить объект как список.

        :return: list[Prayer]
        """
        return list(filter(
            lambda prayer: prayer.name != PrayerNames.SUNRISE,
            await self._origin.as_list(),
        ))


class PrayerForUserAnswer(AnswerInterface):
    """Ответ пользователю с временами намаза."""

    def __init__(self, bot: Bot, chat_id: int, user_prayer_times: PrayerTimesInterface, keyboard: KeyboardInterface):
        self._bot = bot
        self._chat_id = chat_id
        self._user_prayer_times = user_prayer_times
        self._keyboard = keyboard

    async def send(self) -> list[types.Message]:
        """Отправить.

        :return: list[types.Message]
        """
        prayers = await self._user_prayer_times.as_list()
        time_format = '%H:%M'
        template = '\n'.join([
            'Время намаза для г. {city_name} ({date})\n',
            'Иртәнге: {fajr_prayer_time}',
            'Восход: {sunrise_prayer_time}',
            'Өйлә: {dhuhr_prayer_time}',
            'Икенде: {asr_prayer_time}',
            'Ахшам: {magrib_prayer_time}',
            'Ястү: {ishaa_prayer_time}',
        ])
        return await TextAnswer(
            self._bot,
            self._chat_id,
            template.format(
                city_name=prayers[0].city,
                date=prayers[0].day.strftime('%d.%m.%Y'),
                fajr_prayer_time=prayers[0].time.strftime(time_format),
                sunrise_prayer_time=prayers[1].time.strftime(time_format),
                dhuhr_prayer_time=prayers[2].time.strftime(time_format),
                asr_prayer_time=prayers[3].time.strftime(time_format),
                magrib_prayer_time=prayers[4].time.strftime(time_format),
                ishaa_prayer_time=prayers[5].time.strftime(time_format),
            ),
            self._keyboard,
        ).send()
