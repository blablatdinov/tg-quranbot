"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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
"""
from pyeo import elegant
from typing import final

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, Integer, String

from db.base import Base


@final
class PrayerAtUserGroup(Base):
    """Модель для группировки времени намаза у пользователя."""

    __tablename__ = 'prayers_at_user_groups'

    prayers_at_user_group_id = Column(String(), primary_key=True)


@final
class PrayerAtUser(Base):
    """Модель времени намаза у пользователя."""

    __tablename__ = 'prayers_at_user'

    prayer_at_user_id = Column(Integer(), primary_key=True)
    public_id = Column(String())
    user_id = Column(Integer(), ForeignKey('users.chat_id'), nullable=False)
    prayer_id = Column(Integer(), ForeignKey('prayers.prayer_id'))
    is_read = Column(Boolean())
    prayer_group_id = Column(String(), ForeignKey('prayers_at_user_groups.prayers_at_user_group_id'))
