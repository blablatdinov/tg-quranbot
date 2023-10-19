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
# Процесс регистрации

Пользователь отправляет сообщение `/start`, далее обработка идет по 3 сценариям:

1) Это новый пользователь [подробности](#Регистрация-нового-пользователя)
2) Этот пользователь уже зарегистрирован и активен
3) Пользователь уже есть в базе, но он был отписан на момент отправки команды `/start`

Если пользователь регистрируется, деактивируется или реактивируется, то нужно логировать это действие в БД для статистики.

При регистрации пользователя нужно сохранить его идентификатор чата.

## Регистрация нового пользователя

При регистрации нового пользователя ему отправляется [приветственное сообщение](glossary.md#Приветственное-сообщение) и контент первого дня.

## Регистрация активного пользователя

Если пользователь уже зарегистрирован и активен, бот должен отправлять сообщение `Вы уже зарегистрированы`

## Регистрация пользователя, который отписан от бота

Если пользователь был зарегистрирован и отписался от бота, ему отправляется сообщение `Рады видеть вас снова, вы продолжите с дня 43`
