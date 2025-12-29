# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from prometheus_client import Counter

BOT_REQUESTS = Counter('bot_requests_total', 'Total number of requests to the bot')
