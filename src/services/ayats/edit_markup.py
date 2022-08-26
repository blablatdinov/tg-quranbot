from aiogram import Bot

from app_types.intable import Intable
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from services.answers.answer import KeyboardInterface
from services.markup_edit.interface import MarkupEditInterface


class Markup(MarkupEditInterface):
    """Класс, представляющий клавиатуру."""

    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        message_id: int,
        keyboard: KeyboardInterface,
    ):
        self._bot = bot
        self._chat_id = chat_id
        self._message_id = message_id
        self._keyboard = keyboard

    async def edit(self):
        """Редактирование."""
        await self._bot.edit_message_reply_markup(
            chat_id=self._chat_id,
            message_id=self._message_id,
            reply_markup=await self._keyboard.generate(),
        )


class AyatFavoriteStatus(MarkupEditInterface):
    """Статус избранности аята."""

    _favorite_ayat_repository: FavoriteAyatRepositoryInterface
    _ayat_id: Intable
    _chat_id: int

    def __init__(
        self,
        is_favorite: bool,
        favorite_ayat_repository: FavoriteAyatRepositoryInterface,
        ayat_id: Intable,
        chat_id: int,
        markup: MarkupEditInterface,
    ):
        self._is_favorite = is_favorite
        self._favorite_ayat_repository = favorite_ayat_repository
        self._ayat_id = ayat_id
        self._chat_id = chat_id
        self._origin = markup

    async def edit(self) -> None:
        """Поменять статус."""
        if self._is_favorite:
            await self._favorite_ayat_repository.add_to_favorite(
                self._chat_id, int(self._ayat_id),
            )
        else:
            await self._favorite_ayat_repository.remove_from_favorite(
                self._chat_id, int(self._ayat_id),
            )

        await self._origin.edit()
