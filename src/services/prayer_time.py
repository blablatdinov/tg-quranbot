import datetime
from dataclasses import dataclass, field

from aiogram import types
from loguru import logger

from constants import PRAYER_NOT_READED_EMOJI, PRAYER_READED_EMOJI
from repository.prayer_time import Prayer, PrayerNames, PrayerTimeRepositoryInterface, UserPrayer
from repository.user import UserRepositoryInterface
from services.answer import Answer, AnswerInterface


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
        logger.info('Search user prayers...')
        user_prayers = await self.prayer_times.prayer_times_repository.get_user_prayer_times(
            prayers_without_sunrise_ids,
            self.prayer_times.chat_id,
            datetime.datetime.now().date(),
        )
        logger.info('Search result: {0}'.format(user_prayers))
        if not user_prayers:
            logger.info('User prayers not found. Creating...')
            user = await self.prayer_times.user_repository.get_by_chat_id(self.prayer_times.chat_id)
            user_prayers = await self.prayer_times.prayer_times_repository.create_user_prayer_times(
                prayer_ids=prayers_without_sunrise_ids,
                user_id=user.id,
            )

        return user_prayers


@dataclass
class UserPrayerTimesKeyboard(object):
    """Клавиатура для времен намазов пользователей."""

    user_prayer_times: UserPrayerTimes

    async def generate(self):
        """Генерация.

        :returns: types.InlineKeyboardMarkup
        """
        keyboard = types.InlineKeyboardMarkup()
        user_prayers = await self.user_prayer_times.get_or_create_user_prayer_times()
        buttons = []
        # assert False, user_prayers
        for user_prayer in user_prayers:
            callback_data_template = 'mark_not_readed({0})' if user_prayer.is_readed else 'mark_readed({0})'
            buttons.append(types.InlineKeyboardButton(
                PRAYER_READED_EMOJI if user_prayer.is_readed else PRAYER_NOT_READED_EMOJI,
                callback_data=callback_data_template.format(user_prayer.id),
            ))

        keyboard.row(*buttons)

        return keyboard


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


@dataclass
class UserPrayerTimesAnswer(object):
    """Ответ пользователю с временами намазов."""

    user_prayer_times: UserPrayerTimes

    async def to_answer(self) -> AnswerInterface:
        """Форматировать в ответ.

        :returns: AnswerInterface
        """
        return Answer(
            message=str(self.user_prayer_times.prayer_times),
            keyboard=await UserPrayerTimesKeyboard(
                self.user_prayer_times,
            ).generate(),
        )


@dataclass
class UserPrayerStatus(object):

    prayer_times_repository: PrayerTimeRepositoryInterface
    user_prayer_times: UserPrayerTimes
    user_prayer_id: int

    async def change(self, is_readed: bool):
        await self.prayer_times_repository.change_user_prayer_time_status(self.user_prayer_id, is_readed)

    async def generate_refresh_keyboard(self) -> types.InlineKeyboardMarkup:
        return await UserPrayerTimesKeyboard(
            self.user_prayer_times,
        ).generate()
