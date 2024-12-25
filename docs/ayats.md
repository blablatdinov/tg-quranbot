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
# Требования к работе с аятами

## Получить аяты по номеру суры и аята

Когда пользователь отправляет сообщение `5:4`, ему должно возвращаться [Сообщение с аятом](glossary.md#Сообщение-с-аятом):

#### Пример отправляемого текста:
Пример клавиатуры:

Если это первый аят, клавиатура будет выглядеть следующим образом:

<table>
    <tbody>
        <tr>
            <td>стр. 1/5737</td>
            <td>2:1-5 ➡️</td>
        </tr>
        <tr>
            <td colspan="2">Добавить в избранное</td>
        </tr>
    </tbody>
</table>

Последний аят:

<table>
    <tbody>
        <tr>
            <td>⬅️ 114:1-6</td>
            <td>стр. 5737/5737</td>
        </tr>
        <tr>
            <td colspan="2">Добавить в избранное</td>
        </tr>
    </tbody>
</table>

Если аят уже в избранном текст кнопки "Добавить в избранное" меняется на "Удалить из избранного"

<table>
    <tbody>
        <tr>
            <td>⬅️ 5:3</td>
            <td>стр. 656/5737</td>
            <td>5:5 ➡️</td>
        </tr>
        <tr>
            <td colspan="3">Удалить из избранного</td>
        </tr>
    </tbody>
</table>

## Поиск по содержимому аятов:

Пользователь нажимает на кнопку "🔍 Найти аят", и переходит в режим поиска аята: следующие текстовые сообщения считаются запросом для поиска по контенту аятов.

В ответе запрос должен быть выделен жирным шрифтом. Пример:

Пример запроса: камни

Пример перевода: И если вы этого сделать не смогли — а вы [люди] никогда и не сможете, — тогда [если не уверуете] бойтесь Ада, топливом для которого будут люди и __камни__. Уготован он для безбожников.

Пример диалога:

```mermaid
sequenceDiagram
    actor User
    User->>Bot:  🔍 Найти аят
    Bot->>User: Введите слово для поиска:
    User->>Bot: камни
    Bot->>User: <Контент аята>
    Bot->>User: <Аудио аята>
```

Пагинация в клавиатуре происходит по результатам поиска

## Избранные аяты:

Если пользователь нажимает на кнопку или отправляет сообщение "Избранные аяты", ему возвращается [Сообщение с аятом](glossary.md#Сообщение-с-аятом) и клавиатура с пагинацией по избранным

Если пользователь нажимает на кнопку "Добавить в избранное", то аят помещается в ["избранные аяты"](glossary.md#Избранные-аяты) этого пользователя

Если пользователь нажимает на кнопку "Удалить из избранного", то аят удаляется из ["избранных аятов"](glossary.md#Избранные-аяты) этого пользователя

## Создание аятов:

Аят создается единожды.

Информация об аяте парсится с сайта https://umma.ru/perevod-korana/

## Обновление аятов:

При обновлении содержимого аята на сайте https://umma.ru/perevod-korana/, данные в базе об этом аяте должны обновиться
