import enum


class AyatCallbackTemplate(str, enum.Enum):  # noqa: WPS600
    """Шаблон для метаинформации кнопки."""

    get_ayat = 'getAyat({0})'
    get_favorite_ayat = 'getFAyat({0})'
    get_search_ayat = 'getSAyat({0})'
