import asyncio
from contextlib import suppress

import aioredis

from db.connection import database
from integrations.tg import tg_answers
from integrations.tg.app import PollingApp
from integrations.tg.polling_updates import (
    PollingUpdatesIterator,
    UpdatesLongPollingURL,
    UpdatesTimeout,
    UpdatesURL,
    UpdatesWithOffsetURL,
)
from integrations.tg.sendable import SendableAnswer
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.sura import Sura
from repository.city import CityRepository
from repository.podcast import RandomPodcast
from repository.prayer_time import NewUserPrayers, PrayersWithoutSunrise, SafeUserPrayers, UserPrayers, SafeNotFoundPrayers
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
from services.debug_answer import DebugAnswer
from services.podcast_answer import PodcastAnswer
from services.prayers.prayer_status import UserPrayerStatus
from services.prayers.prayer_times import PrayerForUserAnswer, UserPrayerStatusChangeAnswer, InviteSetCityAnswer
from services.state_answer import StepAnswer
from services.switch_inline_query_answer import SwitchInlineQueryKeyboard
from services.user_state import UserStep
from settings import settings


async def main() -> None:
    """Точка входа в приложение."""
    redis = await aioredis.from_url(str(settings.REDIS_DSN))
    empty_answer = tg_answers.TgEmptyAnswer(settings.API_TOKEN)
    message_answer = tg_answers.TgMessageAnswer(empty_answer)
    quranbot_answer = tg_answers.TgMeasureAnswer(
        SafeFork(
            tg_answers.TgAnswerFork(
                tg_answers.TgMessageRegexAnswer(
                    'Подкасты',
                    tg_answers.TgAnswerMarkup(
                        PodcastAnswer(
                            settings.DEBUG,
                            empty_answer,
                            RandomPodcast(database),
                        ),
                        DefaultKeyboard(),
                    ),
                ),
                tg_answers.TgMessageRegexAnswer(
                    'Время намаза',
                    InviteSetCityAnswer(
                        PrayerForUserAnswer(
                            tg_answers.TgAnswerToSender(message_answer),
                            SafeNotFoundPrayers(
                                database,
                                SafeUserPrayers(
                                    UserPrayers(database),
                                    NewUserPrayers(
                                        database,
                                        PrayersWithoutSunrise(
                                            UserPrayers(database),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                        message_answer,
                        redis,
                    ),
                ),
                tg_answers.TgMessageRegexAnswer(
                    'Избранное',
                    FavoriteAyatAnswer(
                        settings.DEBUG,
                        tg_answers.TgAnswerToSender(
                            tg_answers.TgHtmlParseAnswer(message_answer),
                        ),
                        tg_answers.TgAnswerToSender(
                            tg_answers.TgAudioAnswer(
                                empty_answer,
                            ),
                        ),
                        FavoriteAyatsRepository(database),
                    ),
                ),
                StepAnswer(
                    'city_search',
                    tg_answers.TgMessageRegexAnswer(
                        '.+',
                        CityNotSupportedAnswer(
                            ChangeCityAnswer(
                                tg_answers.TgAnswerToSender(message_answer),
                                SearchCityByName(
                                    CityRepository(database),
                                ),
                                redis,
                                UserRepository(database),
                            ),
                            tg_answers.TgAnswerToSender(message_answer),
                        ),
                    ),
                    redis,
                ),
                tg_answers.TgMessageRegexAnswer(
                    r'\d+:\d+',
                    SuraNotFoundSafeAnswer(
                        AyatNotFoundSafeAnswer(
                            AyatBySuraAyatNumAnswer(
                                settings.DEBUG,
                                tg_answers.TgAnswerToSender(
                                    tg_answers.TgHtmlParseAnswer(message_answer),
                                ),
                                tg_answers.TgAnswerToSender(
                                    tg_answers.TgAudioAnswer(
                                        empty_answer,
                                    ),
                                ),
                                AyatBySuraAyatNum(
                                    Sura(database),
                                ),
                            ),
                            tg_answers.TgAnswerToSender(message_answer),
                        ),
                        tg_answers.TgAnswerToSender(message_answer),
                    ),
                ),
                tg_answers.TgCallbackQueryRegexAnswer(
                    '(mark_readed|mark_not_readed)',
                    UserPrayerStatusChangeAnswer(
                        tg_answers.TgAnswerToSender(
                            tg_answers.TgKeyboardEditAnswer(
                                empty_answer,
                            ),
                        ),
                        UserPrayerStatus(database),
                        UserPrayers(database),
                    ),
                ),
                tg_answers.TgCallbackQueryRegexAnswer(
                    'getAyat',
                    AyatByIdAnswer(
                        settings.DEBUG,
                        AyatById(
                            AyatRepository(database),
                        ),
                        tg_answers.TgAnswerToSender(
                            tg_answers.TgHtmlParseAnswer(message_answer),
                        ),
                        tg_answers.TgAnswerToSender(
                            tg_answers.TgAudioAnswer(
                                empty_answer,
                            ),
                        ),
                    ),
                ),
                tg_answers.TgCallbackQueryRegexAnswer(
                    'getFAyat',
                    FavoriteAyatPage(
                        settings.DEBUG,
                        tg_answers.TgAnswerToSender(
                            tg_answers.TgHtmlParseAnswer(message_answer),
                        ),
                        tg_answers.TgAnswerToSender(
                            tg_answers.TgAudioAnswer(
                                empty_answer,
                            ),
                        ),
                        FavoriteAyatsRepository(database),
                    ),
                ),
                tg_answers.TgCallbackQueryRegexAnswer(
                    '(addToFavor|removeFromFavor)',
                    ChangeFavoriteAyatAnswer(
                        AyatById(
                            AyatRepository(database),
                        ),
                        database,
                        tg_answers.TgAnswerToSender(empty_answer),
                    ),
                ),
                InlineQueryAnswer(
                    empty_answer,
                )
            ),
            tg_answers.TgReplySourceAnswer(
                tg_answers.TgAnswerToSender(message_answer),
            ),
        ),
    )
    await database.connect()
    await PollingApp(
        PollingUpdatesIterator(
            UpdatesLongPollingURL(
                UpdatesWithOffsetURL(
                    UpdatesURL(settings.API_TOKEN),
                ),
                UpdatesTimeout(),
            ),
            UpdatesTimeout(),
        ),
        SendableAnswer(quranbot_answer),
    ).run()


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
