import httpx
from aioredis import Redis
from databases import Database

from integrations.client import IntegrationClient
from integrations.nominatim import NominatimIntegration
from integrations.tg.tg_answers import (
    TgAnswerFork,
    TgAnswerInterface,
    TgAnswerMarkup,
    TgAnswerToSender,
    TgAudioAnswer,
    TgCallbackQueryRegexAnswer,
    TgHtmlParseAnswer,
    TgKeyboardEditAnswer,
    TgMessageRegexAnswer,
    TgReplySourceAnswer, TgTextAnswer,
)
from integrations.tg.tg_answers.location_answer import TgLocationAnswer
from integrations.tg.tg_answers.skip_not_processable import TgSkipNotProcessable
from integrations.tg.tg_answers.update import Update
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.sura import Sura
from repository.podcast import RandomPodcast
from repository.prayer_time import NewUserPrayers, SafeNotFoundPrayers, SafeUserPrayers, UserPrayers
from repository.users.user import UserRepository
from services.answers.answer import DefaultKeyboard
from services.answers.change_state_answer import ChangeStateAnswer
from services.answers.safe_fork import SafeFork
from services.ayats.ayat_by_id import AyatByIdAnswer
from services.ayats.ayat_not_found_safe_answer import AyatNotFoundSafeAnswer
from services.ayats.favorite_ayats import FavoriteAyatAnswer, FavoriteAyatPage
from services.ayats.favorites.change_favorite import ChangeFavoriteAyatAnswer
from services.ayats.search.ayat_by_id import AyatById
from services.ayats.search_by_sura_ayat_num import AyatBySuraAyatNum, AyatBySuraAyatNumAnswer
from services.ayats.sura_not_found_safe_answer import SuraNotFoundSafeAnswer
from services.city.change_city_answer import ChangeCityAnswer, CityNotSupportedAnswer
from services.city.inline_query_answer import InlineQueryAnswer
from services.city.search import SearchCityByCoordinates, SearchCityByName
from services.debug_answer import DebugAnswer
from services.podcast_answer import PodcastAnswer
from services.prayers.invite_set_city_answer import InviteSetCityAnswer
from services.prayers.prayer_for_user_answer import PrayerForUserAnswer
from services.prayers.prayer_status import UserPrayerStatus
from services.prayers.prayer_times import UserPrayerStatusChangeAnswer
from services.state_answer import StepAnswer
from services.user_state import UserStep, LoggedUserState, UserState
from settings import settings


class QuranbotAnswer(TgAnswerInterface):
    """Ответ бота quranbot."""

    def __init__(
        self,
        empty_answer: TgAnswerInterface,
        message_answer: TgAnswerInterface,
        database: Database,
        redis: Redis,
    ):
        self._empty_answer = empty_answer
        self._message_answer = message_answer
        self._database = database
        self._redis = redis

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        answer_to_sender = TgAnswerToSender(self._message_answer)
        return await SafeFork(
            TgAnswerFork(
                TgMessageRegexAnswer(
                    'Подкасты',
                    TgAnswerMarkup(
                        PodcastAnswer(
                            settings.DEBUG,
                            self._empty_answer,
                            RandomPodcast(self._database),
                        ),
                        DefaultKeyboard(),
                    ),
                ),
                TgMessageRegexAnswer(
                    'Время намаза',
                    InviteSetCityAnswer(
                        PrayerForUserAnswer(
                            answer_to_sender,
                            SafeNotFoundPrayers(
                                self._database,
                                SafeUserPrayers(
                                    UserPrayers(self._database),
                                    NewUserPrayers(
                                        self._database,
                                        UserPrayers(self._database),
                                    ),
                                ),
                            ),
                        ),
                        self._message_answer,
                        self._redis,
                    ),
                ),
                TgMessageRegexAnswer(
                    'Избранное',
                    FavoriteAyatAnswer(
                        settings.DEBUG,
                        TgAnswerToSender(
                            TgHtmlParseAnswer(self._message_answer),
                        ),
                        TgAnswerToSender(
                            TgAudioAnswer(self._empty_answer),
                        ),
                        FavoriteAyatsRepository(self._database),
                    ),
                ),
                StepAnswer(
                    UserStep.city_search.value,
                    TgSkipNotProcessable(
                        TgAnswerFork(
                            TgMessageRegexAnswer(
                                '.+',
                                CityNotSupportedAnswer(
                                    ChangeCityAnswer(
                                        answer_to_sender,
                                        SearchCityByName(self._database),
                                        self._redis,
                                        UserRepository(self._database),
                                    ),
                                    answer_to_sender,
                                ),
                            ),
                            TgLocationAnswer(
                                CityNotSupportedAnswer(
                                    ChangeCityAnswer(
                                        answer_to_sender,
                                        SearchCityByCoordinates(
                                            SearchCityByName(self._database),
                                            NominatimIntegration(IntegrationClient()),
                                        ),
                                        self._redis,
                                        UserRepository(self._database),
                                    ),
                                    answer_to_sender,
                                ),
                            ),
                        ),
                    ),
                    self._redis,
                ),
                TgMessageRegexAnswer(
                    r'\d+:\d+',
                    SuraNotFoundSafeAnswer(
                        AyatNotFoundSafeAnswer(
                            AyatBySuraAyatNumAnswer(
                                settings.DEBUG,
                                TgAnswerToSender(
                                    TgHtmlParseAnswer(self._message_answer),
                                ),
                                TgAnswerToSender(
                                    TgAudioAnswer(self._empty_answer),
                                ),
                                AyatBySuraAyatNum(
                                    Sura(self._database),
                                ),
                            ),
                            answer_to_sender,
                        ),
                        answer_to_sender,
                    ),
                ),
                TgMessageRegexAnswer(
                    'Найти аят',
                    ChangeStateAnswer(
                        TgTextAnswer(
                            answer_to_sender,
                            'Введите слово для поиска:'
                        ),
                        self._redis,
                        UserStep.ayat_search,
                    )
                ),
                TgCallbackQueryRegexAnswer(
                    '(mark_readed|mark_not_readed)',
                    UserPrayerStatusChangeAnswer(
                        TgAnswerToSender(
                            TgKeyboardEditAnswer(self._empty_answer),
                        ),
                        UserPrayerStatus(self._database),
                        UserPrayers(self._database),
                    ),
                ),
                TgCallbackQueryRegexAnswer(
                    'getAyat',
                    AyatByIdAnswer(
                        settings.DEBUG,
                        AyatById(
                            AyatRepository(self._database),
                        ),
                        TgAnswerToSender(
                            TgHtmlParseAnswer(self._message_answer),
                        ),
                        TgAnswerToSender(
                            TgAudioAnswer(self._empty_answer),
                        ),
                    ),
                ),
                TgCallbackQueryRegexAnswer(
                    'getFAyat',
                    FavoriteAyatPage(
                        settings.DEBUG,
                        TgAnswerToSender(
                            TgHtmlParseAnswer(self._message_answer),
                        ),
                        TgAnswerToSender(
                            TgAudioAnswer(self._empty_answer),
                        ),
                        FavoriteAyatsRepository(self._database),
                    ),
                ),
                TgCallbackQueryRegexAnswer(
                    '(addToFavor|removeFromFavor)',
                    ChangeFavoriteAyatAnswer(
                        AyatById(
                            AyatRepository(self._database),
                        ),
                        self._database,
                        TgAnswerToSender(self._empty_answer),
                    ),
                ),
                InlineQueryAnswer(
                    self._empty_answer,
                    SearchCityByName(self._database),
                ),
            ),
            TgReplySourceAnswer(
                answer_to_sender,
            ),
        ).build(update)
