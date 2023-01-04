import httpx
from aioredis import Redis

from db.connection import database
from exceptions.content_exceptions import AyatNotFoundError
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswerInterface
from repository.ayats.ayat import AyatRepositoryInterface
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import TextSearchNeighborAyatsRepository
from services.ayats.ayat_answer import AyatAnswer
from services.ayats.ayat_keyboard_callback_template import AyatCallbackTemplate
from services.ayats.ayat_text_search_query import AyatTextSearchQuery
from services.ayats.keyboards import AyatAnswerKeyboard
from services.regular_expression import IntableRegularExpression


class SearchAyatByTextCallbackAnswer(TgAnswerInterface):
    """Поиск аята по тексту для обработки нажатия кнопки."""

    def __init__(
        self,
        debug_mode: bool,
        message_answer: TgAnswerInterface,
        file_answer: TgAnswerInterface,
        ayat_repo: AyatRepositoryInterface,
        redis: Redis,
    ):
        """Конструктор класса.

        :param debug_mode: bool
        :param message_answer: TgAnswerInterface
        :param file_answer: TgAnswerInterface
        :param ayat_repo: AyatRepositoryInterface
        :param redis: Redis
        """
        self._debug_mode = debug_mode
        self._message_answer = message_answer
        self._file_answer = file_answer
        self._ayat_repo = ayat_repo
        self._redis = redis

    async def build(self, update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :return: list[httpx.Request]
        :raises AyatNotFoundError: if ayat not found
        """
        target_ayat_id = int(IntableRegularExpression(str(CallbackQueryData(update))))
        try:
            ayats = await self._ayat_repo.search_by_text(
                await AyatTextSearchQuery.for_reading_cs(self._redis, int(TgChatId(update))).read(),
            )
        except IndexError as err:
            raise AyatNotFoundError from err
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
            AyatAnswerKeyboard(
                result_ayat,
                FavoriteAyatsRepository(database),
                TextSearchNeighborAyatsRepository(
                    database,
                    result_ayat.id,
                    AyatTextSearchQuery.for_reading_cs(
                        self._redis,
                        int(TgChatId(update)),
                    ),
                ),
                AyatCallbackTemplate.get_search_ayat,
            ),
        ).build(update)
