# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from typing import final, override

import attrs
import httpx
from databases import Database
from redis.asyncio import Redis

from app_types.logger import LogSink
from app_types.update import Update
from handlers.concrete_podcast_answer import ConcretePodcastAnswer
from handlers.decrement_skipped_prayer_answer import DecrementSkippedPrayerAnswer
from handlers.favorites_answer import FavoriteAyatsAnswer
from handlers.full_start_answer import FullStartAnswer
from handlers.next_day_ayats import NextDayAyats
from handlers.paginate_by_search_ayat import PaginateBySearchAyat
from handlers.pagination_per_day_prayer_answer import PaginationPerDayPrayerAnswer
from handlers.pg_set_user_city_answer import PgSetUserCityAnswer
from handlers.podcast_reaction_change_answer import PodcastReactionChangeAnswer
from handlers.prayer_time_answer import PrayerTimeAnswer
from handlers.search_ayat_by_keyword_answer import SearchAyatByKeywordAnswer
from handlers.search_ayat_by_numbers_answer import SearchAyatByNumbersAnswer
from handlers.skipped_prayers_answer import SkippedPrayersAnswer
from handlers.status_answer import StatusAnswer
from handlers.user_prayer_status_change_answer import UserPrayerStatusChangeAnswer
from integrations.tg.tg_answers import (
    TgAnswer,
    TgAnswerFork,
    TgAnswerToSender,
    TgCallbackQueryRegexAnswer,
    TgEmptyAnswer,
    TgMessageAnswer,
    TgMessageRegexAnswer,
    TgTextAnswer,
)
from integrations.tg.tg_answers.message_answer_to_sender import TgHtmlMessageAnswerToSender
from services.answers.change_state_answer import ChangeStateAnswer
from services.answers.safe_fork import SafeFork
from services.help_answer import HelpAnswer
from services.state_answer import StepAnswer
from settings import Settings
from srv.admin_messages.pg_admin_message import PgAdminMessage
from srv.ayats.ayat_by_id_answer import AyatByIdAnswer
from srv.ayats.change_favorite_ayat_answer import ChangeFavoriteAyatAnswer
from srv.ayats.favorite_ayat_page import FavoriteAyatPage
from srv.events.sink import Sink
from srv.podcasts.random_podcast_answer import RandomPodcastAnswer
from srv.prayers.inline_query_answer import InlineQueryAnswer
from srv.prayers.invite_set_city_answer import InviteSetCityAnswer
from srv.users.user_step import UserStep


@final
@attrs.define(frozen=True)
class QuranbotAnswer(TgAnswer):
    """Ответ бота quranbot."""

    _answer: TgAnswer

    @classmethod
    def ctor(
        cls,
        pgsql: Database,
        redis: Redis,
        event_sink: Sink,
        settings: Settings,
        logger: LogSink,
    ) -> TgAnswer:
        """Конструктор класса.

        :param pgsql: Database
        :param redis: Redis
        :param event_sink: SinkInterface
        :param settings: Settings
        :param logger: LogSink
        :return: TgAnswer
        """
        empty_answer = TgEmptyAnswer(settings.API_TOKEN)
        return cls(
            SafeFork(
                TgAnswerFork.ctor(
                    logger,
                    TgMessageRegexAnswer(
                        'Подкасты',
                        RandomPodcastAnswer(
                            settings.DEBUG,
                            empty_answer,
                            redis,
                            pgsql,
                            logger,
                        ),
                    ),
                    TgMessageRegexAnswer(
                        r'/podcast\d+',
                        ConcretePodcastAnswer(
                            settings.DEBUG,
                            empty_answer,
                            redis,
                            pgsql,
                            logger,
                        ),
                    ),
                    # TODO #1428:30min Интегрировать просмотр времени намаза с сайта https://namaz.today
                    #  Нужно встроить feature flag, чтобы включать и выключать эту функцию
                    #  для отдельных пользователей
                    TgMessageRegexAnswer(
                        'Время намаза',
                        PrayerTimeAnswer.new_prayers_ctor(
                            pgsql,
                            empty_answer,
                            settings.admin_chat_ids(),
                            redis,
                            logger,
                            settings,
                        ),
                    ),
                    TgMessageRegexAnswer(
                        '/skipped_prayers',
                        SkippedPrayersAnswer(empty_answer, pgsql),
                    ),
                    TgMessageRegexAnswer(
                        'Избранное',
                        FavoriteAyatsAnswer(
                            settings.DEBUG, pgsql, redis, empty_answer, logger,
                        ),
                    ),
                    TgMessageRegexAnswer(
                        r'\d+:\d+',
                        SearchAyatByNumbersAnswer(
                            settings.DEBUG,
                            empty_answer,
                            redis,
                            pgsql,
                            logger,
                        ),
                    ),
                    TgMessageRegexAnswer(
                        'Найти аят',
                        ChangeStateAnswer(
                            TgTextAnswer.str_ctor(
                                TgHtmlMessageAnswerToSender(empty_answer),
                                'Введите слово для поиска:',
                            ),
                            redis,
                            UserStep.ayat_search,
                            logger,
                        ),
                    ),
                    TgMessageRegexAnswer(
                        'Поменять город',
                        InviteSetCityAnswer(
                            TgTextAnswer.str_ctor(
                                TgHtmlMessageAnswerToSender(empty_answer),
                                'Отправьте местоположение или воспользуйтесь поиском',
                            ),
                            redis,
                            logger,
                        ),
                    ),
                    TgMessageRegexAnswer(
                        '/start',
                        FullStartAnswer(
                            pgsql, empty_answer, event_sink, redis, settings, logger,
                        ),
                    ),
                    TgMessageRegexAnswer(
                        '/status',
                        StatusAnswer(empty_answer, pgsql, redis),
                    ),
                    TgMessageRegexAnswer(
                        '/help',
                        HelpAnswer(
                            empty_answer,
                            PgAdminMessage('start', pgsql),
                            redis,
                            logger,
                        ),
                    ),
                    StepAnswer(
                        UserStep.ayat_search.value,
                        SearchAyatByKeywordAnswer(
                            settings.DEBUG,
                            empty_answer,
                            redis,
                            pgsql,
                            logger,
                        ),
                        redis,
                        logger,
                    ),
                    TgCallbackQueryRegexAnswer(
                        '(mark_readed|mark_not_readed)',
                        UserPrayerStatusChangeAnswer(empty_answer, pgsql, redis, logger, settings),
                    ),
                    TgCallbackQueryRegexAnswer(
                        'pagPrDay',
                        PaginationPerDayPrayerAnswer(
                            empty_answer,
                            pgsql,
                            settings.admin_chat_ids(),
                            redis,
                            logger,
                            settings,
                        ),
                    ),
                    TgCallbackQueryRegexAnswer(
                        '(like|dislike)',
                        PodcastReactionChangeAnswer(
                            settings.DEBUG,
                            empty_answer,
                            redis,
                            pgsql,
                            logger,
                        ),
                    ),
                    TgCallbackQueryRegexAnswer(
                        'getAyat',
                        AyatByIdAnswer(settings.DEBUG, empty_answer, pgsql),
                    ),
                    TgCallbackQueryRegexAnswer(
                        'decr',
                        DecrementSkippedPrayerAnswer(empty_answer, pgsql),
                    ),
                    TgCallbackQueryRegexAnswer(
                        'nextDayAyats',
                        NextDayAyats(empty_answer, pgsql),
                    ),
                    StepAnswer(
                        UserStep.ayat_search.value,
                        TgCallbackQueryRegexAnswer(
                            'getSAyat',
                            PaginateBySearchAyat(empty_answer, redis, pgsql, settings, logger),
                        ),
                        redis,
                        logger,
                    ),
                    StepAnswer(
                        UserStep.city_search.value,
                        PgSetUserCityAnswer(pgsql, empty_answer, settings.DEBUG, redis, logger),
                        redis,
                        logger,
                    ),
                    TgCallbackQueryRegexAnswer(
                        'getFAyat',
                        FavoriteAyatPage(settings.DEBUG, empty_answer, pgsql),
                    ),
                    TgCallbackQueryRegexAnswer(
                        '(addToFavor|removeFromFavor)',
                        ChangeFavoriteAyatAnswer(pgsql, empty_answer, redis, logger),
                    ),
                    InlineQueryAnswer(empty_answer, pgsql),
                ),
                TgAnswerToSender(
                    TgMessageAnswer(empty_answer),
                ),
            ),
        )

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await self._answer.build(update)
