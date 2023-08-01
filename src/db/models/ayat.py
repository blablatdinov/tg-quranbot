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
from typing import final

from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String

from db.base import Base


@final
class Ayat(Base):
    """Модель аята."""

    __tablename__ = 'ayats'

    ayat_id = Column(Integer(), primary_key=True)
    public_id = Column(String(), nullable=False)
    day = Column(Integer(), nullable=True)
    sura_id = Column(Integer(), ForeignKey('suras.sura_id'), nullable=False)
    audio_id = Column(String(), ForeignKey('files.file_id'), nullable=False)
    ayat_number = Column(String(length=10), nullable=False)
    content = Column(String(), nullable=False)  # noqa: WPS110
    arab_text = Column(String(), nullable=False)
    transliteration = Column(String(), nullable=False)
