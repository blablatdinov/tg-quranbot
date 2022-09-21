import httpx

from db.connection import database
from integrations.tg.tg_answers import TgAnswerInterface, TgAnswerList, TgAnswerMarkup, TgTextAnswer
from integrations.tg.tg_answers.update import Update
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface, FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import FavoriteNeighborAyats
from repository.ayats.schemas import Ayat
from services.answers.answer import FileAnswer, KeyboardInterface, TelegramFileIdAnswer
from services.ayats.ayat_favorite_keyboard_button import AyatFavoriteKeyboardButton
from services.ayats.ayat_keyboard_callback_template import AyatCallbackTemplate
from services.ayats.ayat_neighbor_keyboard import AyatNeighborAyatKeyboard


class AyatAnswerKeyboard(KeyboardInterface):
    """Клавиатура аята."""

    def __init__(self, ayat: Ayat, favorite_ayats_repo: FavoriteAyatRepositoryInterface):
        self._ayat = ayat
        self._favorite_ayats_repo = favorite_ayats_repo

    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        """
        return await AyatFavoriteKeyboardButton(
            self._ayat,
            AyatNeighborAyatKeyboard(
                FavoriteNeighborAyats(
                    self._ayat.id,
                    update.chat_id(),
                    self._favorite_ayats_repo,
                ),
                AyatCallbackTemplate.get_favorite_ayat,
            ),
            FavoriteAyatsRepository(database),
        ).generate(update)


class AyatAnswer(TgAnswerInterface):
    """Ответ с аятом."""

    def __init__(
        self,
        debug: bool,
        answers: tuple[TgAnswerInterface, TgAnswerInterface],
        ayat: Ayat,
        ayat_answer_keyboard: KeyboardInterface,
    ):
        self._debug_mode = debug
        self._message_answer = answers[0]
        self._file_answer = answers[1]
        self._ayat = ayat
        self._ayat_answer_keyboard = ayat_answer_keyboard

    async def build(self, update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await TgAnswerList(
            TgAnswerMarkup(
                TgTextAnswer(
                    self._message_answer,
                    str(self._ayat),
                ),
                self._ayat_answer_keyboard,
            ),
            FileAnswer(
                self._debug_mode,
                TelegramFileIdAnswer(
                    self._file_answer,
                    self._ayat.audio_telegram_id,
                ),
                TgTextAnswer(
                    self._message_answer,
                    self._ayat.link_to_audio_file,
                ),
            ),
        ).build(update)
