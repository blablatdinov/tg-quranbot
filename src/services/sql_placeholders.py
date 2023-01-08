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
from typing import Sequence


def generate_sql_placeholders(sequence: Sequence, elem_fields_count: int) -> str:
    """Сгенерировать плейсхолдеры для SQL запроса по элементам последовательности и кол-ву полей.

    >>> generate_sql_placeholders(['a', 'b', 'c'], 4)
    ... '($1, $2, $3, $4), ($5, $6, $7, $8), ($9, $10, $11, $12)'

    :param sequence: Sequence
    :param elem_fields_count: int
    :return: str
    """
    placeholders_list = [
        '${0}'.format(elem_field_num)
        for elem_field_num in range(1, (len(sequence) * elem_fields_count) + 1)
    ]
    placeholder_rows = []
    for index in range(0, len(placeholders_list), elem_fields_count):
        placeholders_for_row = placeholders_list[index:index + elem_fields_count]
        placeholder_rows.append('({0})'.format(', '.join(placeholders_for_row)))
    return ', '.join(placeholder_rows)
