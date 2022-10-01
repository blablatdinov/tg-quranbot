import httpx
from aioredis import Redis

from db.connection import database
from exceptions.content_exceptions import AyatNotFoundError
from integrations.tg.tg_answers import TgAnswerInterface
from integrations.tg.tg_answers.update import Update
from repository.ayats.ayat import AyatRepositoryInterface
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from services.ayats.ayat_answer import AyatAnswer, AyatSearchByTextAnswerKeyboard
from services.ayats.ayat_text_search_query import AyatTextSearchQuery
from services.regular_expression import IntableRegularExpression


class CachedAyatSearchQueryAnswer(TgAnswerInterface):
    """

    TODO: что делать если данные из кэша будут удалены
    """

    def __init__(self, answer: TgAnswerInterface, redis: Redis):
        self._origin = answer
        self._redis = redis

    async def build(self, update: Update) -> list[httpx.Request]:
        requests = await self._origin.build(update)
        await AyatTextSearchQuery.for_write_cs(
            self._redis,
            update.message().text(),
            update.chat_id(),
        ).write()
        return requests


class SearchAyatByTextAnswer(TgAnswerInterface):

    def __init__(
        self,
        debug_mode: bool,
        message_answer: TgAnswerInterface,
        file_answer: TgAnswerInterface,
        ayat_repo: AyatRepositoryInterface,
        redis: Redis,
    ):
        self._debug_mode = debug_mode
        self._message_answer = message_answer
        self._file_answer = file_answer
        self._ayat_repo = ayat_repo
        self._redis = redis

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        query = update.message().text()
        try:
            result_ayat = (await self._ayat_repo.search_by_text(query))[0]
        except IndexError:
            raise AyatNotFoundError
        answers = (self._message_answer, self._file_answer)
        return await AyatAnswer(
            self._debug_mode,
            answers,
            result_ayat,
            AyatSearchByTextAnswerKeyboard(
                result_ayat, FavoriteAyatsRepository(database), self._redis,
            ),
        ).build(update)


class SearchAyatByTextCallbackAnswer(TgAnswerInterface):

    def __init__(
        self,
        debug_mode: bool,
        message_answer: TgAnswerInterface,
        file_answer: TgAnswerInterface,
        ayat_repo: AyatRepositoryInterface,
        redis: Redis,
    ):
        self._debug_mode = debug_mode
        self._message_answer = message_answer
        self._file_answer = file_answer
        self._ayat_repo = ayat_repo
        self._redis = redis

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        target_ayat_id = int(IntableRegularExpression(update.callback_query().data))
        search_query = AyatTextSearchQuery.for_reading_cs(self._redis, update.chat_id())
        try:
            ayats = await self._ayat_repo.search_by_text(
                await search_query.read()
            )
        except IndexError:
            raise AyatNotFoundError
        for ayat in ayats:
            if ayat.id == target_ayat_id:
                result_ayat = ayat
                break
        else:
            raise AyatNotFoundError
        answers = (self._message_answer, self._file_answer)
        return await AyatAnswer(
            self._debug_mode,
            answers,
            result_ayat,
            AyatSearchByTextAnswerKeyboard(
                result_ayat, FavoriteAyatsRepository(database), self._redis,
            ),
        ).build(update)
