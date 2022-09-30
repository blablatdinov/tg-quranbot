import httpx
from aioredis import Redis
from databases import Database

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
    TgReplySourceAnswer,
)
from integrations.tg.tg_answers.update import Update
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.sura import Sura
from repository.city import CityRepository
from repository.podcast import RandomPodcast
from repository.prayer_time import (
    NewUserPrayers,
    PrayersWithoutSunrise,
    SafeNotFoundPrayers,
    SafeUserPrayers,
    UserPrayers,
)
from repository.users.user import UserRepository
from services.answers.answer import DefaultKeyboard
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
from services.city.search import SearchCityByName
from services.podcast_answer import PodcastAnswer
from services.prayers.prayer_status import UserPrayerStatus
from services.prayers.prayer_times import InviteSetCityAnswer, PrayerForUserAnswer, UserPrayerStatusChangeAnswer
from services.state_answer import StepAnswer
from settings import settings


class QuranbotAnswer(TgAnswerInterface):

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
                            TgAnswerToSender(self._message_answer),
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
                    'city_search',
                    TgMessageRegexAnswer(
                        '.+',
                        CityNotSupportedAnswer(
                            ChangeCityAnswer(
                                TgAnswerToSender(self._message_answer),
                                SearchCityByName(
                                    CityRepository(self._database),
                                ),
                                self._redis,
                                UserRepository(self._database),
                            ),
                            TgAnswerToSender(self._message_answer),
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
                            TgAnswerToSender(self._message_answer),
                        ),
                        TgAnswerToSender(self._message_answer),
                    ),
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
                InlineQueryAnswer(self._empty_answer)
            ),
            TgReplySourceAnswer(
                TgAnswerToSender(self._message_answer),
            ),
        ).build(update)
