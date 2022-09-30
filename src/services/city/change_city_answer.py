import httpx
from aioredis import Redis

from exceptions.content_exceptions import CityNotSupportedError
from integrations.tg.tg_answers import TgAnswerInterface, TgTextAnswer
from integrations.tg.tg_answers.update import Update
from repository.users.user import UserRepositoryInterface
from services.city.search import CitySearchInterface, SearchCityQuery
from services.user_state import UserState, UserStep, LoggedUserState


class CityNotSupportedAnswer(TgAnswerInterface):

    def __init__(self, answer: TgAnswerInterface, error_answer: TgAnswerInterface):
        self._origin = answer
        self._error_answer = error_answer

    async def build(self, update: Update) -> list[httpx.Request]:
        try:
            return await self._origin.build(update)
        except CityNotSupportedError:
            return await TgTextAnswer(
                self._error_answer,
                'Этот город не поддерживается',
            ).build(update)


class ChangeCityAnswer(TgAnswerInterface):

    def __init__(
        self,
        answer: TgAnswerInterface,
        search_city: CitySearchInterface,
        redis: Redis,
        user_repo: UserRepositoryInterface,
    ):
        self._city = search_city
        self._origin = answer
        self._redis = redis
        self._user_repo = user_repo

    async def build(self, update: Update) -> list[httpx.Request]:
        try:
            query = SearchCityQuery.from_string_cs(update.message().text())
        except AttributeError:
            query = SearchCityQuery.from_coordinates_cs(
                update.message().location().latitude,
                update.message().location().longitude,
            )
        cities = await self._city.search(query)
        if not cities:
            raise CityNotSupportedError
        await self._user_repo.update_city(update.chat_id(), cities[0].id)
        await LoggedUserState(
            UserState(self._redis, update.chat_id()),
        ).change_step(UserStep.nothing)
        return await TgTextAnswer(
            self._origin,
            'Вам будет приходить время намаза для города {0}'.format(cities[0].name),
        ).build(update)
