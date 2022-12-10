import httpx

from app_types.stringable import Stringable
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswerInterface
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from repository.ayats.neighbor_ayats import FavoriteNeighborAyats
from services.ayats.ayat_answer import AyatAnswer
from services.ayats.keyboards import AyatAnswerKeyboard
from services.regular_expression import IntableRegularExpression


class FavoriteAyatStatus(object):
    """Пользовательский ввод статуса аята в избранном."""

    def __init__(self, source: str):
        self._source = source

    def ayat_id(self) -> int:
        """Идентификатор аята.

        :return: int
        """
        return int(IntableRegularExpression(self._source))

    def change_to(self) -> bool:
        """Целевое значение.

        :return: bool
        """
        return 'addToFavor' in self._source


class FavoriteAyatAnswer(TgAnswerInterface):
    """Ответ с избранными аятами."""

    def __init__(
        self,
        debug: bool,
        message_answer: TgAnswerInterface,
        file_answer: TgAnswerInterface,
        favorite_ayats_repo: FavoriteAyatRepositoryInterface,
    ):
        self._debug_mode = debug
        self._message_answer = message_answer
        self._file_answer = file_answer
        self._favorite_ayats_repo = favorite_ayats_repo

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        result_ayat = (await self._favorite_ayats_repo.get_favorites(int(TgChatId(update))))[0]
        answers = (self._message_answer, self._file_answer)
        return await AyatAnswer(
            self._debug_mode,
            answers,
            result_ayat,
            AyatAnswerKeyboard(
                result_ayat,
                self._favorite_ayats_repo,
                FavoriteNeighborAyats(
                    result_ayat.id, int(TgChatId(update)), self._favorite_ayats_repo,
                ),
            ),
        ).build(update)


class FavoriteAyatPage(TgAnswerInterface):
    """Страница с избранным аятом."""

    def __init__(
        self,
        debug: bool,
        message_answer: TgAnswerInterface,
        file_answer: TgAnswerInterface,
        favorite_ayats_repo: FavoriteAyatRepositoryInterface,
    ):
        self._debug_mode = debug
        self._message_answer = message_answer
        self._file_answer = file_answer
        self._favorite_ayats_repo = favorite_ayats_repo

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        result_ayat = await self._favorite_ayats_repo.get_favorite(
            int(IntableRegularExpression(str(CallbackQueryData(update)))),
        )
        answers = (self._message_answer, self._file_answer)
        return await AyatAnswer(
            self._debug_mode,
            answers,
            result_ayat,
            AyatAnswerKeyboard(
                result_ayat,
                self._favorite_ayats_repo,
                FavoriteNeighborAyats(result_ayat.id, int(TgChatId(update)), self._favorite_ayats_repo),
            ),
        ).build(update)
