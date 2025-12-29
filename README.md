<!---
SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
SPDX-License-Identifier: MIT
-->
# Quranbot
[![EO principles respected here](https://www.elegantobjects.org/badge.svg)](https://www.elegantobjects.org)

<a href="https://codeclimate.com/github/blablatdinov/tg-quranbot/maintainability"><img src="https://api.codeclimate.com/v1/badges/e4206df635326574026e/maintainability" /></a>
[![codecov](https://codecov.io/gh/blablatdinov/tg-quranbot/graph/badge.svg?token=4862UGV4AB)](https://codecov.io/gh/blablatdinov/tg-quranbot)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)
![](https://tokei.rs/b1/github/blablatdinov/tg-quranbot)
[![Hits-of-Code](https://hitsofcode.com/github/blablatdinov/tg-quranbot)](https://hitsofcode.com/github/blablatdinov/tg-quranbot/view)
![Custom badge](https://img.shields.io/endpoint?style=flat&url=https://quranbot.ilaletdinov.ru/api/v1/count-github-badge)

[Документация](docs)

Функционал:
- Каждое утро, вам будут приходить аяты из Священного Корана.
- При нажатии на кнопку **Подкасты**, вам будут присылаться проповеди с сайта umma.ru.
- В боте вы можете получать время намаза
- Доступен поиск по ключевым словам

Также вы можете отправить номер суры, аята (например **4:7**) и получить: аят в оригинале, перевод на русский язык, транслитерацию и аудио

Ссылка на бота: [Quran_365_bot](https://t.me/Quran_365_bot?start=github)

Если хотите поучаствовать в разработке пишите - [telegram](https://t.me/ilaletdinov), [email](mailto:a.ilaletdinov@yandex.ru?subject=[GitHub]%20Quranbot)

## Информация берется с сайтов:

[umma.ru](https://umma.ru/)

[dumrt.ru](http://dumrt.ru/ru/)

## Используемые технологии:

- ~~aiogram~~
- rabbitmq
- postgres
- ~~pydantic~~
- pytest
- flake8
- mypy
- redis

## Смежные проекты:

[django-version](https://github.com/blablatdinov/quranbot) - предыдущая версия бота

[API](https://github.com/blablatdinov/quranbot-admin) - для административной панели. Доступен по [ссылке](https://quranbot.ilaletdinov.ru/docs)

[Хранилище схем для событий](https://github.com/blablatdinov/quranbot-schema-registry/)
