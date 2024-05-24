<!---
The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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
# Требования к подкастам

## Получить подкаст в боте:

Если пользователь присылает сообщение "Подкасты" ему должен возвращаться случайный подкаст

Бот должен отправлять подкасты по идентификатору файла в телеграм https://core.telegram.org/bots/api#sendaudio

Стандартная клавиатура должна содержать кнопку "🎧 Подкасты"

Вариации текста сообщения для получения подкаста:

- Подкасты
- подкасты
- 🎧 Подкасты

При запросе подкаста с идентификатором (пр. `/podcast753`, где 753 - идентификатор подкаста),
пользователю возвращается подкаст с этим идентификатором

Клавиатура подкастов:

| 👍 0 | 👎 0 |
|------|------|

Пользователь может оставить свою реакцию на подкаст

Пользователь может отменить реакцию на подкаст повторным нажатием

Пользователь может изменить реакцию на подкаст, нажатием на другу кнопку

## Парсинг подкастов

Парсер собирает подкасты со страницы https://umma.ru/audlo/shamil-alyautdinov/

Парсер запускается каждую неделю в понедельник, скачивает аудио, отправляет его в телеграм и сохраняет `file_id`
