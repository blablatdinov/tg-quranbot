from dataclasses import dataclass
from typing import Optional

from aiogram import types

from exceptions import AyatNotFoundError, SuraNotFoundError, exception_to_answer_formatter
from repository.ayats import Ayat, AyatRepositoryInterface
from services.answer import Answer, AnswerInterface, AnswersList

KEYBOARD_AYAT_TEMPLATE = '{0}:{1}'
CALLBACK_DATA_PLUG = '1'
CALLBACT_DATA_GET_AYAT_TEMPLATE = 'get_ayat({ayat_id})'


@dataclass
class AyatServiceInterface(object):
    """Интерфейс для действий над аятами."""

    ayat_repository: AyatRepositoryInterface
    chat_id: int

    async def get_formatted_first_ayat(self) -> str:
        """Получить отформатированный аят.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    def format_ayat(self, ayat: Ayat) -> str:
        """Отформатировать аят.

        :param ayat: Ayat
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def search_by_number(self, search_input: str) -> AnswerInterface:
        """Найти аят по номеру.

        :param search_input: str
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


@dataclass
class AyatSearchKeyboard(object):
    """Клавиатура, выводимая пользователям вместе с найденными аятами."""

    ayat_repository: AyatRepositoryInterface
    ayat: Ayat
    chat_id: int

    async def generate(self):
        """Генерация клавиатуры.

        :returns: InlineKeyboard
        """
        first_ayat_id = 1
        last_ayat_id = 5737
        ayat_is_favorite = await self.ayat_repository.check_ayat_is_favorite_for_user(self.ayat.id, self.chat_id)
        neighbor_ayats = await self.ayat_repository.get_ayat_neighbors(self.ayat.id)
        favorite_button_message = 'Удалить из избранного' if ayat_is_favorite else 'Добавить в избранное'
        if self.ayat.id == first_ayat_id:
            return self._first_ayat_case(neighbor_ayats, favorite_button_message)
        elif self.ayat.id == last_ayat_id:
            return self._last_ayat_case(neighbor_ayats, favorite_button_message)

        return self._middle_ayat_case(neighbor_ayats, favorite_button_message)

    def _first_ayat_case(self, neighbor_ayats, favorite_button_message):
        right_ayat = neighbor_ayats[1]
        return (
            types.InlineKeyboardMarkup()
            .row(
                types.InlineKeyboardButton(
                    text=KEYBOARD_AYAT_TEMPLATE.format(right_ayat.sura_num, right_ayat.ayat_num),
                    callback_data=CALLBACT_DATA_GET_AYAT_TEMPLATE.format(ayat_id=right_ayat.id),
                ),
            )
            .row(types.InlineKeyboardButton(text=favorite_button_message, callback_data=CALLBACK_DATA_PLUG))
        )

    def _last_ayat_case(self, neighbor_ayats, favorite_button_message):
        left_ayat = neighbor_ayats[0]
        return (
            types.InlineKeyboardMarkup()
            .row(
                types.InlineKeyboardButton(
                    text=KEYBOARD_AYAT_TEMPLATE.format(left_ayat.sura_num, left_ayat.ayat_num),
                    callback_data=CALLBACT_DATA_GET_AYAT_TEMPLATE.format(ayat_id=left_ayat.id),
                ),
            )
            .row(types.InlineKeyboardButton(text=favorite_button_message, callback_data=CALLBACK_DATA_PLUG))
        )

    def _middle_ayat_case(self, neighbor_ayats, favorite_button_message):
        left_ayat, right_ayat = neighbor_ayats[0], neighbor_ayats[2]
        return (
            types.InlineKeyboardMarkup()
            .row(
                types.InlineKeyboardButton(
                    text=KEYBOARD_AYAT_TEMPLATE.format(left_ayat.sura_num, left_ayat.ayat_num),
                    callback_data=CALLBACT_DATA_GET_AYAT_TEMPLATE.format(ayat_id=left_ayat.id),
                ),
                types.InlineKeyboardButton(
                    text=KEYBOARD_AYAT_TEMPLATE.format(right_ayat.sura_num, right_ayat.ayat_num),
                    callback_data=CALLBACT_DATA_GET_AYAT_TEMPLATE.format(ayat_id=right_ayat.id),
                ),
            )
            .row(types.InlineKeyboardButton(text=favorite_button_message, callback_data=CALLBACK_DATA_PLUG))
        )


class AyatsService(AyatServiceInterface):
    """Сервис для действий над аятами."""

    ayat_repository: AyatRepositoryInterface
    chat_id: int

    async def get_formatted_first_ayat(self) -> str:
        """Получить отформатированный аят.

        :returns: str
        """
        ayat = await self.ayat_repository.first()
        return self.format_ayat(ayat)

    def format_ayat(self, ayat: Ayat) -> str:
        """Отформатировать аят для сообщения.

        :param ayat: Ayat
        :returns: str
        """
        link = 'https://umma.ru{sura_link}'.format(sura_link=ayat.sura_link)
        template = '<a href="{link}">{sura}:{ayat})</a>\n{arab_text}\n\n{content}\n\n<i>{transliteration}</i>'
        return template.format(
            link=link,
            sura=ayat.sura_num,
            ayat=ayat.ayat_num,
            arab_text=ayat.arab_text,
            content=ayat.content,
            transliteration=ayat.transliteration,
        )

    async def format_ayat_to_answers(self, ayat: Ayat) -> AnswersList:
        """Форматировать аят в ответы.

        :param ayat: Ayat
        :returns: AnswersList
        """
        keyboard = await AyatSearchKeyboard(self.ayat_repository, ayat, self.chat_id).generate()
        return AnswersList(
            Answer(message=self.format_ayat(ayat), chat_id=self.chat_id),
            Answer(
                telegram_file_id=ayat.audio_telegram_id,
                chat_id=self.chat_id,
                link_to_file=ayat.link_to_audio_file,
                keyboard=keyboard,
            ),
        )

    @exception_to_answer_formatter
    async def search_by_number(self, search_input: str) -> AnswerInterface:
        """Найти аят по номеру.

        :param search_input: str
        :returns: AnswerInterface
        """
        sura_num, ayat_num = search_input.split(':')
        ayats = await self.ayat_repository.get_ayats_by_sura_num(int(sura_num))
        self._validate_sura_ayat_numbers(int(sura_num), int(ayat_num))
        for ayat in ayats:
            answer = None
            if '-' in ayat.ayat_num:
                answer = await self._service_range_case(ayat, ayat_num)
            elif ',' in ayat.ayat_num:
                answer = await self._service_comma_case(ayat, ayat_num)
            elif ayat.ayat_num == ayat_num:
                answer = await self.format_ayat_to_answers(ayat)

            if answer:
                return answer

        return Answer(message='Аят не найден')

    async def _service_range_case(self, ayat: Ayat, ayat_num: str) -> Optional[AnswerInterface]:
        left, right = map(int, ayat.ayat_num.split('-'))
        ayats_range = range(left, right + 1)
        if int(ayat_num) in ayats_range:
            return await self.format_ayat_to_answers(ayat)
        return None

    async def _service_comma_case(self, ayat: Ayat, ayat_num: str) -> Optional[AnswerInterface]:
        left, right = map(int, ayat.ayat_num.split(','))
        ayats_range = range(left, right + 1)
        if int(ayat_num) in ayats_range:
            return await self.format_ayat_to_answers(ayat)
        return None

    def _validate_sura_ayat_numbers(self, sura_num: int, ayat_num: int) -> None:
        max_sura_num = 114
        if not 0 < sura_num <= max_sura_num:  # noqa: WPS508
            # https://github.com/wemake-services/wemake-python-styleguide/issues/1942
            raise SuraNotFoundError
        if ayat_num <= 0:
            raise AyatNotFoundError
