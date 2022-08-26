import datetime

from aiogram import types, Bot
from loguru import logger

from app_types.intable import Intable
from exceptions.content_exceptions import UserHasNotCityIdError
from repository.prayer_time import PrayerTimeRepositoryInterface, PrayerNames
from repository.users.user import UserRepositoryInterface
from services.answers.answer import TextAnswer, KeyboardInterface
from services.answers.interface import AnswerInterface
from services.regular_expression import IntableRegularExpression


class PrayerTimesInterface(object):

    async def as_list(self):
        raise NotImplementedError


class UserPrayerTimesInterface(object):

    async def as_list(self):
        raise NotImplementedError


class PrayerTimes(PrayerTimesInterface):

    def __init__(
        self,
        chat_id: int,
        user_repository: UserRepositoryInterface,
        prayer_times_repository: PrayerTimeRepositoryInterface,
        date: datetime.date
    ):
        self._chat_id = chat_id
        self._user_repository = user_repository
        self._prayer_times_repository = prayer_times_repository
        self._date = date

    async def as_list(self):
        user = await self._user_repository.get_by_chat_id(self._chat_id)
        if not user.city_id:
            raise UserHasNotCityIdError
        prayers = await self._prayer_times_repository.get_prayer_times_for_date(
            chat_id=self._chat_id,
            target_datetime=self._date,
            city_id=user.city_id,
        )
        return prayers


class UserPrayerTimes(UserPrayerTimesInterface):

    def __init__(
        self,
        chat_id: int,
        prayer_times: PrayerTimesInterface,
        user_repository: UserRepositoryInterface,
        prayer_times_repo: PrayerTimeRepositoryInterface
    ):
        self._chat_id = chat_id
        self._prayer_times = prayer_times
        self._user_repository = user_repository
        self._prayer_times_repository = prayer_times_repo

    async def as_list(self):
        prayers = await self._prayer_times.as_list()
        user_prayers = await self._prayer_times_repository.get_user_prayer_times(
            [prayer.id for prayer in prayers],
            self._chat_id,
            datetime.datetime.now(),
        )
        logger.info('Search result: {0}'.format(user_prayers))
        if not user_prayers:
            logger.info('User prayers not found. Creating...')
            user = await self._user_repository.get_by_chat_id(self._chat_id)
            user_prayers = await self._prayer_times_repository.create_user_prayer_times(
                prayer_ids=prayers,
                user_id=user.chat_id,
            )

        return user_prayers


class PrayerStatus(object):

    def __init__(self, source: str):
        self._source = source

    def user_prayer_id(self):
        return int(IntableRegularExpression(self._source))

    def change_to(self):
        return 'not' not in self._source.split('(')[0]


class EditedUserPrayerTimes(UserPrayerTimesInterface):

    def __init__(
        self,
        user_prayer_times: UserPrayerTimesInterface,
        prayer_times_repo: PrayerTimeRepositoryInterface,
        prayer_status: PrayerStatus,
    ):
        self._origin = user_prayer_times
        self._prayer_times_repo = prayer_times_repo
        self._user_prayer_status = prayer_status

    async def as_list(self):
        await self._prayer_times_repo.change_user_prayer_time_status(
            self._user_prayer_status.user_prayer_id(), self._user_prayer_status.change_to(),
        )
        return await self._origin.as_list()


class PrayersWithoutSunrise(PrayerTimesInterface):

    def __init__(self, prayer_times: PrayerTimesInterface):
        self._origin = prayer_times

    async def as_list(self):
        filter(
            lambda prayer: prayer.name != PrayerNames.SUNRISE,
            await self._origin.as_list(),
        )


class PrayerForUserAnswer(AnswerInterface):

    def __init__(self, bot: Bot, chat_id: int, user_prayer_times: PrayerTimesInterface, keyboard: KeyboardInterface):
        self._bot = bot
        self._chat_id = chat_id
        self._user_prayer_times = user_prayer_times
        self._keyboard = keyboard

    async def send(self) -> list[types.Message]:
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
