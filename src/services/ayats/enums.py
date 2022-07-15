import enum


class AyatPaginatorCallbackDataTemplate(str, enum.Enum):  # noqa: WPS600
    """Шаблоны для данных в кнопках с пагинацией по аятам.

    в ayat_text_search_template должен быть помещен search_query до дальнейшей передачи
    """

    ayat_search_template = 'get_ayat({ayat_id})'
    favorite_ayat_template = 'get_favorite_ayat({ayat_id})'
    ayat_text_search_template = 'search_text_ayat({ayat_id})'
