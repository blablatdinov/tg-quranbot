import httpx
from aioredis import Redis
from databases import Database

from integrations.client import IntegrationClient
from integrations.nats_integration import SinkInterface
from integrations.nominatim import NominatimIntegration
from integrations.tg.tg_answers import (
    TgAnswerFork,
    TgAnswerInterface,
    TgAnswerMarkup,
    TgAnswerToSender,
    TgAudioAnswer,
    TgCallbackQueryRegexAnswer,
    TgEmptyAnswer,
    TgHtmlParseAnswer,
    TgKeyboardEditAnswer,
    TgMessageAnswer,
    TgMessageRegexAnswer,
    TgReplySourceAnswer,
    TgTextAnswer,
)
from integrations.tg.tg_answers.location_answer import TgLocationAnswer
from integrations.tg.tg_answers.skip_not_processable import TgSkipNotProcessable
from integrations.tg.tg_answers.update import Update
from repository.admin_message import AdminMessageRepository
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.sura import Sura
from repository.podcast import RandomPodcast
from repository.prayer_time import NewUserPrayers, SafeNotFoundPrayers, SafeUserPrayers, UserPrayers
from repository.users.user import UserRepository
from repository.users.users import UsersRepository
from services.answers.answer import DefaultKeyboard, ResizedKeyboard
from services.answers.change_state_answer import ChangeStateAnswer
from services.answers.safe_fork import SafeFork
from services.ayats.ayat_by_id import AyatByIdAnswer
from services.ayats.ayat_by_sura_ayat_num_answer import AyatBySuraAyatNumAnswer
from services.ayats.ayat_not_found_safe_answer import AyatNotFoundSafeAnswer
from services.ayats.favorite_ayats import FavoriteAyatAnswer, FavoriteAyatPage
from services.ayats.favorites.change_favorite import ChangeFavoriteAyatAnswer
from services.ayats.highlited_search_answer import HighlightedSearchAnswer
from services.ayats.search.ayat_by_id import AyatById
from services.ayats.search_by_sura_ayat_num import AyatBySuraAyatNum
from services.ayats.search_by_text import (
    CachedAyatSearchQueryAnswer,
    SearchAyatByTextAnswer,
    SearchAyatByTextCallbackAnswer,
)
from services.ayats.sura_not_found_safe_answer import SuraNotFoundSafeAnswer
from services.city.change_city_answer import ChangeCityAnswer, CityNotSupportedAnswer
from services.city.inline_query_answer import InlineQueryAnswer
from services.city.search import SearchCityByCoordinates, SearchCityByName
from services.podcast_answer import PodcastAnswer
from services.prayers.invite_set_city_answer import InviteSetCityAnswer
from services.prayers.prayer_for_user_answer import PrayerForUserAnswer
from services.prayers.prayer_status import UserPrayerStatus
from services.prayers.prayer_times import UserPrayerStatusChangeAnswer
from services.reset_state_answer import ResetStateAnswer
from services.start_answer import (
    StartAnswer,
    StartWithEventAnswer,
    UserAlreadyActiveSafeAnswer,
    UserAlreadyExistsAnswer,
)
from services.state_answer import StepAnswer
from services.user_state import UserStep
from settings import settings


class QuranbotAnswer(TgAnswerInterface):
    """Ответ бота quranbot."""

    def __init__(
        self,
        database: Database,
        redis: Redis,
        event_sink: SinkInterface,
    ):
        self._database = database
        self._redis = redis
        self._event_sink = event_sink

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        empty_answer = TgEmptyAnswer(settings.API_TOKEN)
        answer_to_sender = TgAnswerToSender(TgMessageAnswer(empty_answer))
        audio_to_sender = TgAudioAnswer(answer_to_sender)
        html_to_sender = TgAnswerToSender(
            TgHtmlParseAnswer(
                TgMessageAnswer(empty_answer),
            ),
        )
        ayat_repo = AyatRepository(self._database)
        return await SafeFork(
            TgAnswerFork(
                TgMessageRegexAnswer(
                    'Подкасты',
                    ResetStateAnswer(
                        PodcastAnswer(
                            settings.DEBUG,
                            empty_answer,
                            RandomPodcast(self._database),
                        ),
                        self._redis,
                    ),
                ),
                TgMessageRegexAnswer(
                    'Время намаза',
                    InviteSetCityAnswer(
                        ResetStateAnswer(
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
                            self._redis,
                        ),
                        TgMessageAnswer(empty_answer),
                        self._redis,
                    ),
                ),
                TgMessageRegexAnswer(
                    'Избранное',
                    ResetStateAnswer(
                        FavoriteAyatAnswer(
                            settings.DEBUG,
                            html_to_sender,
                            audio_to_sender,
                            FavoriteAyatsRepository(self._database),
                        ),
                        self._redis,
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
                    ResetStateAnswer(
                        SuraNotFoundSafeAnswer(
                            AyatNotFoundSafeAnswer(
                                AyatBySuraAyatNumAnswer(
                                    settings.DEBUG,
                                    html_to_sender,
                                    audio_to_sender,
                                    AyatBySuraAyatNum(
                                        Sura(self._database),
                                    ),
                                ),
                                answer_to_sender,
                            ),
                            answer_to_sender,
                        ),
                        self._redis,
                    ),
                ),
                TgMessageRegexAnswer(
                    'Найти аят',
                    ChangeStateAnswer(
                        TgTextAnswer(
                            answer_to_sender,
                            'Введите слово для поиска:',
                        ),
                        self._redis,
                        UserStep.ayat_search,
                    ),
                ),
                TgMessageRegexAnswer(
                    '/start',
                    ResetStateAnswer(
                        TgAnswerMarkup(
                            UserAlreadyActiveSafeAnswer(
                                UserAlreadyExistsAnswer(
                                    StartWithEventAnswer(
                                        StartAnswer(
                                            TgMessageAnswer(empty_answer),
                                            UserRepository(self._database),
                                            AdminMessageRepository(self._database),
                                            ayat_repo,
                                        ),
                                        self._event_sink,
                                        UserRepository(self._database),
                                    ),
                                    answer_to_sender,
                                    UserRepository(self._database),
                                    UsersRepository(self._database),
                                    self._event_sink,
                                ),
                                answer_to_sender,
                            ),
                            ResizedKeyboard(
                                DefaultKeyboard(),
                            ),
                        ),
                        self._redis,
                    ),
                ),
                StepAnswer(
                    UserStep.ayat_search.value,
                    TgMessageRegexAnswer(
                        '.+',
                        HighlightedSearchAnswer(
                            CachedAyatSearchQueryAnswer(
                                SearchAyatByTextAnswer(
                                    settings.DEBUG,
                                    html_to_sender,
                                    audio_to_sender,
                                    ayat_repo,
                                    self._redis,
                                ),
                                self._redis,
                            ),
                            self._redis,
                        ),
                    ),
                    self._redis,
                ),
                TgCallbackQueryRegexAnswer(
                    '(mark_readed|mark_not_readed)',
                    UserPrayerStatusChangeAnswer(
                        TgAnswerToSender(
                            TgKeyboardEditAnswer(empty_answer),
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
                            ayat_repo,
                        ),
                        html_to_sender,
                        audio_to_sender,
                    ),
                ),
                StepAnswer(
                    UserStep.ayat_search.value,
                    TgCallbackQueryRegexAnswer(
                        'getSAyat',
                        HighlightedSearchAnswer(
                            SearchAyatByTextCallbackAnswer(
                                settings.DEBUG,
                                html_to_sender,
                                audio_to_sender,
                                ayat_repo,
                                self._redis,
                            ),
                            self._redis,
                        ),
                    ),
                    self._redis,
                ),
                TgCallbackQueryRegexAnswer(
                    'getFAyat',
                    FavoriteAyatPage(
                        settings.DEBUG,
                        html_to_sender,
                        audio_to_sender,
                        FavoriteAyatsRepository(self._database),
                    ),
                ),
                TgCallbackQueryRegexAnswer(
                    '(addToFavor|removeFromFavor)',
                    ChangeFavoriteAyatAnswer(
                        AyatById(
                            ayat_repo,
                        ),
                        self._database,
                        answer_to_sender,
                    ),
                ),
                InlineQueryAnswer(
                    empty_answer,
                    SearchCityByName(self._database),
                ),
            ),
            TgReplySourceAnswer(
                answer_to_sender,
            ),
        ).build(update)
