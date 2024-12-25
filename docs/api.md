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
# Спецификация API

### Любому пользователю должен быть доступен просмотр аятов с пагинацией

Пример запроса:

```bash
curl -X 'GET' \
  'https://quranbot.ilaletdinov.ru/api/v1/ayats/?page_num=1&page_size=50' \
  -H 'accept: application/json'
```

Пример ответа:

```json
{
  "count": 5737,
  "next": "http://quranbot.ilaletdinov.ru/api/v1/ayats/?page_num=2&page_size=50",
  "prev": null,
  "results": [
    {
      "id": 1,
      "content": "Именем Аллаха [именем Бога, Творца всего сущего, Одного и Единственного для всех и вся], милость Которого вечна и безгранична. Истинное восхваление принадлежит только Аллаху, Господу миров, милость Которого вечна и безгранична, Владыке Судного Дня. Тебе поклоняемся и у Тебя просим помощи [поддержки, Божьего благословения в делах наших]. Направь нас на правильный путь. Путь тех, которым он был дарован [из числа пророков и посланников, праведников и мучеников, а также всех тех, кто удостоен был такой чести — идти правильным путем]. Не тех, на которых Ты разгневался, и не тех, которые сошли с него[,] .",
      "arab_text": "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ١ الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ٢ الرَّحْمَنِ الرَّحِيمِ٣ مَالِكِ يَوْمِ الدِّينِ٤ إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ٥ اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ٦ صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ٧",
      "trans": "[Бисмилляяхир-Рахмаанир-Рахиим (1) Аль-Хамду Лилляяхи Раббиль-`Алямиин(2) Эр-Рахмаанир-Рахимм (3) Малики йаумид-диин (4) Ийяякя ня`буду уа ийяякя наста`иин (5) Ихдиня ссырааталь-мустакыыйм (6) Ссырааталь-лязиина ан`амта `алейхим, гайриль-магдууби `алейхим уа ляд-дааалиин. (7)]",
      "sura_num": 1,
      "ayat_num": "1-7",
      "audio_file_link": "https://umma.ru/audio/Ozvucjka-statei/Quran/audio/Husary_64/1/001001-7.mp3"
    },
    ...
  ]
}
```
