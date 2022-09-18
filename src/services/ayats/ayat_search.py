from typing import Optional

from aiogram import Bot, types

from app_types.intable import Intable
from exceptions.content_exceptions import AyatNotFoundError, UserHasNotFavoriteAyatsError
from repository.ayats.schemas import Ayat
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from services.answers.answer import DefaultKeyboard, FileAnswer, FileLinkAnswer, TelegramFileIdAnswer, TextAnswer
from services.answers.answer_list import AnswersList
from services.answers.interface import AnswerInterface
from services.ayats.ayat_search_interface import AyatSearchInterface
from services.ayats.keyboard import AyatPaginatorCallbackDataTemplate, AyatSearchKeyboard


class FavoriteAyats(AyatSearchInterface):
    """Получить избранные аяты."""

    _ayat_repository: FavoriteAyatRepositoryInterface
    _chat_id: int
    _ayat_id: Optional[Intable]
    _ayat_paginator_callback_data_template: AyatPaginatorCallbackDataTemplate

    def __init__(
        self,
        ayat_repository: FavoriteAyatRepositoryInterface,
        chat_id: int,
        ayat_id: Optional[Intable] = None,  # TODO: maybe separate class for None cases
        ayat_paginator_callback_data_template: AyatPaginatorCallbackDataTemplate = None,
    ):
        self._ayat_repository = ayat_repository
        self._chat_id = chat_id
        self._ayat_id = ayat_id
        if not ayat_paginator_callback_data_template:
            ayat_paginator_callback_data_template = AyatPaginatorCallbackDataTemplate.favorite_ayat_template
        self._ayat_paginator_callback_data_template = ayat_paginator_callback_data_template

    async def search(self) -> Ayat:
        """Поиск избранных аятов.

        :returns: Ayat
        :raises UserHasNotFavoriteAyatsError: если избранные аяты для этого пользователя не найдены
        """
        favorite_ayats = await self._ayat_repository.get_favorites(self._chat_id)
        if not favorite_ayats:
            raise UserHasNotFavoriteAyatsError
        if not self._ayat_id:
            return favorite_ayats[0]

        return [ayat for ayat in favorite_ayats if ayat.id == int(self._ayat_id)][0]


class SearchAnswer(AnswerInterface):
    """Класс, собирающий ответ на запрос о поиске."""

    _ayat_search: AyatSearchInterface

    def __init__(
        self,
        debug_mode: bool,
        bot: Bot,
        chat_id: int,
        ayat_search: AyatSearchInterface,
        keyboard: AyatSearchKeyboard,
    ):
        self._debug_mode = debug_mode
        self._bot = bot
        self._chat_id = chat_id
        self._ayat_search = ayat_search
        self._keyboard = keyboard

    async def send(self) -> list[types.Message]:
        """Отправить.

        :returns: AnswerInterface
        """
        ayat = await self._ayat_search.search()
        return await AnswersList(
            TextAnswer(self._bot, self._chat_id, str(ayat), self._keyboard),
            FileAnswer(
                self._debug_mode,
                TelegramFileIdAnswer(
                    self._bot,
                    self._chat_id,
                    ayat.audio_telegram_id,
                    DefaultKeyboard(),
                ),
                FileLinkAnswer(
                    self._bot,
                    self._chat_id,
                    ayat.link_to_audio_file,
                    DefaultKeyboard(),
                ),
            ),
        ).send()


class AyatNotFoundSafeAnswer(AnswerInterface):
    """Декортаор, для обработки ошибки."""

    def __init__(self, bot: Bot, chat_id: int, answerable: AnswerInterface):
        self._bot = bot
        self._chat_id = chat_id
        self._origin = answerable

    async def send(self) -> list[types.Message]:
        """Конвертация в ответ.

        :returns: AnswerInterface
        """
        try:
            return await self._origin.send()
        except AyatNotFoundError as error:
            return await TextAnswer(
                self._bot,
                self._chat_id,
                error.user_message,
                DefaultKeyboard(),
            ).send()
