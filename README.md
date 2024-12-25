<!---
The MIT License (MIT).

Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
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
