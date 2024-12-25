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
# Словарь терминов

### Сообщение с аятом
Сообщения, содержащие:
- номер суры/аята, ссылку на источник, контент на русском
- озвучка на арабском языке
- [клавиатура](glossary.md#Клавиатура-аята)

Пример:

> [5:4)](https://umma.ru/sura-5-al-maida-trapeza/)
>
>َلَّمْتُمْ مِنَ الْجَوَارِحِ مُكَلِّبِينَ تُعَلِّمُونَهُنَّ مِمَّا عَلَّمَكُمُ اللَّهُ فَكُلُوا مِمَّا أَمْسَكْنَ عَلَيْكُمْ وَاذْكُرُوا اسْمَ اللَّهِ عَلَيْهِ وَاتَّقُوا اللَّهَ إِنَّ اللَّهَ سَرِيعُ الْحِسَابِ
>
> У тебя [Мухаммад] спрашивают о разрешенном для них [для верующих]. Скажи: «Разрешено вам все хорошее [приятное с точки зрения здорового общечеловеческого восприятия. Все незапрещенное — изначально дозволено]. Вам разрешается использовать обученных животных и птиц для охоты. Ешьте добычу, что они удерживают [приносят] для вас. А отправляя их за нею, упоминайте имя Аллаха (Бога, Господа).Бойтесь Аллаха (Бога, Господа). Воистину, Он быстро отчитает [человека в Судный День за дела мирские и поступки (быстро подведет итог его мирского бытия). Долгие разбирательства не потребуются, результат мирских деяний человека будет нагляден и очевиден].
>
> [Йас\`алюнака Маза Ухилля Ляхум Куль Ухилля Лякумут-Таййибату Уа Ма \`Аллzмтум Миналь-Джаварихи Мукаллибина Ту\`аллимунахунна Мимма \`АллямакумуЛлаху Факулю Мимма Амсакна \`Алейкум Уа Аpкуру АсмаЛлахи \`Алейхи УаТтакуЛлаха ИннаЛлаха Сари`уль-Хисааб.]

### Избранные аяты

Аяты, которые пользователь добавил в "Избранные"

### Клавиатура аята

Клавиатура с пагинацией и кнопкой для добавления/удаления аята в ["избранные аяты"](glossary.md#Избранные-аяты)

Пример клавиатуры:

<table>
    <tbody>
        <tr>
            <td>⬅️ 5:3</td>
            <td>5:5 ➡️</td>
        </tr>
        <tr>
            <td colspan="2">Добавить в избранное</td>
        </tr>
    </tbody>
</table>

### Сообщение с временем намаза

Сообщение, в котором содержатся времена намаза и клавиатура для пометки намаза прочитанным/непрочитанным

Пример текста сообщения:

```
Время намаза для г. Казань (15.08.2022)

Иртәнге: 01:09
Восход: 04:14
Өйлә: 11:48
Икенде: 16:54
Ахшам: 19:20
Ястү: 21:35
```

Пример клавиатуры с непрочитанными намазами:

<table>
    <tbody>
        <tr>
            <td>❌</td>
            <td>❌</td>
            <td>❌</td>
            <td>❌</td>
            <td>❌</td>
        </tr>
    </tbody>
</table>

Пример клавиатуры с прочитанными намазами:

<table>
    <tbody>
        <tr>
            <td>✅</td>
            <td>✅</td>
            <td>✅</td>
            <td>✅</td>
            <td>✅</td>
        </tr>
    </tbody>
</table>

### Сообщение с предложением выбрать город

Пример текста сообщения:

```
Вы не указали город, отправьте местоположение или воспользуйтесь поиском
```

Пример клавиатуры:

<table>
    <tbody>
        <tr>
            <td>Поиск города</td>
        </tr>
    </tbody>
</table>

### Аяты для утренней рассылки

До 5 аятов без аудио и клавиатуры в одном сообщении

```
10 октября 2018 г., 14:02
От кого: «команда umma» <info@umma.ru>
Кому: «Алмаз Илалетдинов» <a.ilaletdinov@yandex.ru>

Здравствуйте!
Только при прямой активной ссылке на конкретную суру.
И не более 5-ти аятов в сутки.


С уважением, команда umma.ru
сайт Ш. Аляутдинова: https://umma.ru/
книги Ш. Аляутдинова: https://ummastore.ru/ семинары Ш. Аляутдинова: https://trillioner.life/ позитивно об Исламе: http://umma.news/
доставка воды «Триллионер»: https://trillioner.store/
```

### Сохраненное сообщение

Сообщение присланное в бота или отправленное ботом

Пример в формате json:

```
{
    "message_id":20810,
    "from":{
        "id":358610865,
        "is_bot":false,
        "first_name":"Алмаз",
        "last_name":"Илалетдинов",
        "username":"ilaletdinov",
        "language_code":"ru"
    },
    "chat":{
        "id":358610865,
        "first_name":"Алмаз",
        "last_name":"Илалетдинов",
        "username":"ilaletdinov",
        "type":"private"
    },
    "date":1658397839,
    "text":"🌟 Избранное"
}
```

Пример сообщения с файлом:

```
{
    "message_id": 12120,
    "from": {
        "id": 705810219,
        "is_bot_init": true,
        "first_name": "Quran",
        "username": "Quran_365_bot_init"
    },
    "chat": {
        "id": 358610865,
        "first_name": "Алмаз",
        "last_name": "Илалетдинов",
        "username": "ilaletdinov",
        "type": "private"
    },
    "date": 1582624476,
    "audio": {
        "duration": 0,
        "mime_type": "audio/mpeg",
        "title": "Остерегайтесь сект!",
        "performer": "Шамиль Аялутдинов",
        "file_id": "CQACAgIAAxkDAAIvWF5U7tyc4kGu7CuJjG0s1w4eSrXeAAL4BwACwtR4SjHMgbJ9LMmFGAQ",
        "file_unique_id": "AgAD-AcAAsLUeEo",
        "file_size": 29956029
    }
}
```

### Сохраненное нажатие на кнопку

Нажатие на кнопку пользователям

Пример в формате json:

```
{
    "id":"1540221939457636489",
    "from":{
        "id":358610865,
        "is_bot":false,
        "first_name":"Алмаз",
        "last_name":"Илалетдинов",
        "username":"ilaletdinov",
        "language_code":"ru"
    },
    "message":{
        "message_id":20821,
        "from":{
            "id":452230948,
            "is_bot":true,
            "first_name":"WokeUpSmiled",
            "username":"WokeUpSmiled_bot"
        },
        "chat":{
            "id":358610865,
            "first_name":"Алмаз",
            "last_name":"Илалетдинов",
            "username":"ilaletdinov",
            "type":"private"
        },
        "date":1658401777,
        "text":"2:24)\nفَإِنْ لَمْ تَفْعَلُوا وَلَنْ تَفْعَلُوا فَاتَّقُوا النَّارَ الَّتِي وَقُودُهَا النَّاسُ وَالْحِجَارَةُ أُعِدَّتْ لِلْكَافِرِينَ\n\nИ если вы этого сделать не смогли — а вы [люди] никогда и не сможете, — тогда [если не уверуете] бойтесь Ада, топливом для которого будут люди и камни. Уготован он для безбожников.\n\n[Фа-иллам-таф’алу уа лантаф-’алу фаттакун-Нарал-лати уакуду-хан-насу уалхижарату у-’иддат лил-Кафирин]",
        "entities":[
            {
                "type":"text_link",
                "offset":0,
                "length":5,
                "url":"https://umma.ru/sura-2-al-bakara-korova/"
            },
            {
                "type":"italic",
                "offset":318,
                "length":102
            }
        ],
        "reply_markup":{
            "inline_keyboard":[
                [
                    {
                        "text":"11:83 ➡️",
                        "callback_data":"search_text_ayat(1533)"
                    }
                ],
                [
                    {
                        "text":"Добавить в избранное",
                        "callback_data":"add_to_favorite(17)"
                    }
                ]
            ]
        }
    },
    "chat_instance":"-8377414756201282502",
    "data":"add_to_favorite(17)"
}
```

### Приветственное сообщение

Сообщение, отправляемое при регистрации

Пр:

> Этот бот поможет тебе изучить Коран по богословскому переводу Шамиля Аляутдинова.
>
> Каждое утро, вам будут приходить аяты из Священного Корана.
При нажатии на кнопку Подкасты, вам будут присылаться проповеди с сайта umma.ru.
>
> Также вы можете отправите номер суры, аята (например <b>4:7</b>) и получить: аят в оригинале, перевод на русский язык, транслитерацию и аудио
