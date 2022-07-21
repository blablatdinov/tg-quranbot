from app_types.answerable import Answerable
from exceptions.content_exceptions import CityNotSupportedError
from repository.city import City
from repository.users.user import UserRepositoryInterface
from services.answers.answer import Answer
from services.answers.interface import AnswerInterface
from services.city.search import CitySearchInterface


class UserCity(object):
    """Класс обслуживающий город пользователя."""

    _city_search: CitySearchInterface
    _user_repository: UserRepositoryInterface
    _chat_id: int

    def __init__(self, city_search: CitySearchInterface, user_repository: UserRepositoryInterface, chat_id: int):
        self._city_search = city_search
        self._user_repository = user_repository
        self._chat_id = chat_id

    async def update_city(self) -> City:
        """Обновить город.

        :returns: City
        """
        city = (await self._city_search.search())[0]
        await self._user_repository.update_city(self._chat_id, city.id)
        return city


class UserCityAnswer(Answerable):
    """Ответ пользователю о смене города."""

    _user_city: UserCity

    def __init__(self, user_city: UserCity):
        self._user_city = user_city

    async def to_answer(self) -> AnswerInterface:
        """Форматировать в ответ.

        :returns: AnswerInterface
        """
        city = await self._user_city.update_city()
        return Answer(message='Вам будет приходить время намаза для г. {0}'.format(city.name))


class CityNotSupportedSafetyAnswer(Answerable):
    """Ответ на поиск с обраоткой ошибки о необслуживаемом городе."""

    def __init__(self, answer: Answerable):
        self._origin = answer

    async def to_answer(self) -> AnswerInterface:
        """Форматировать в ответ.

        :returns: AnswerInterface
        """
        try:
            return await self._origin.to_answer()
        except CityNotSupportedError as error:
            return Answer(message=error.user_message)
