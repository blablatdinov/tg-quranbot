from typing import Sequence


def generate_sql_placeholders(sequence: Sequence, elem_fields_count: int) -> str:
    """Сгенерировать плейсхолдеры для SQL запроса по элементам последовательности и кол-ву полей.

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
