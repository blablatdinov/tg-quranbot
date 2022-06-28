import datetime
from dataclasses import dataclass, field

from repository.prayer_time import PrayerTimeRepositoryInterface, Prayer
from repository.user import UserRepositoryInterface
from services.answer import AnswerInterface, Answer


@dataclass
class UserPrayerTimes(object):
    prayer_times_repository: PrayerTimeRepositoryInterface
    chat_id: int
    user_repository: UserRepositoryInterface
    prayers: list[Prayer] = field(default_factory=list)

    async def get(self) -> 'UserPrayerTimes':
        user = await self.user_repository.get_by_chat_id(self.chat_id)
        prayers = await self.prayer_times_repository.get_prayer_times_for_date(
            chat_id=self.chat_id,
            target_datetime=datetime.datetime.now(),
            city_id=user.city_id,
        )
        return UserPrayerTimes(
            prayers=prayers,
            prayer_times_repository=self.prayer_times_repository,
            chat_id=self.chat_id,
            user_repository=self.user_repository,
        )

    def format_to_answer(self) -> AnswerInterface:
        template = (
            'Время намаза для г. {city_name} ({date})\n\n'
            'Иртәнге: {first_prayer_time}\n'
            'Восход: {second_prayer_time}\n'
            'Өйлә: {third_prayer_time}\n'
            'Икенде: {fourth_prayer_time}\n'
            'Ахшам: {fifth_prayer_time}\n'
            'Ястү: {sixth_prayer_time}'
        )
        text = template.format(
            city_name=self.prayers[0].city,
            date=self.prayers[0].day.strftime('%d.%m.%Y'),
            first_prayer_time=self.prayers[0].time,
            second_prayer_time=self.prayers[1].time,
            third_prayer_time=self.prayers[2].time,
            fourth_prayer_time=self.prayers[3].time,
            fifth_prayer_time=self.prayers[4].time,
            sixth_prayer_time=self.prayers[5].time,
        )
        return Answer(message=text)
