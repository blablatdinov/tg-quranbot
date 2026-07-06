# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

# flake8: noqa: WPS202
from typing import final

from exceptions.base_exception import BaseAppError


@final
class SuraNotFoundError(BaseAppError):
    """Исключение, вызываемое при отсутствии нужной суры."""

    user_message = 'Сура не найдена'


@final
class AyatNotFoundError(BaseAppError):
    """Исключение, вызываемое при отсутствии нужного аята."""

    user_message = 'Аят не найден'


@final
class BotFileNotFoundError(BaseAppError):
    """Файл не найден."""


@final
class CityNotSupportedError(BaseAppError):
    """Исключение, вызываемое если при поиске города, он не нашелся в БД."""

    user_message = 'Такой город не обслуживается'


@final
class UserHasNotCityIdError(BaseAppError):
    """Исключение, вызываемое если пользователь без установленного города запросил времена намазов."""

    user_message = 'Вы не указали город, отправьте местоположение или воспользуйтесь поиском'


@final
class AyatHaveNotNeighborsError(BaseAppError):
    """Исключение, вызываемое при попытке сгенерить клавиатуру для аята без соседей."""

    admin_message = 'У аята нет соседей'


@final
class UserHasNotFavoriteAyatsError(BaseAppError):
    """Исключение, вызываемое при попытке получить избранные аяты, пользователем, у которого их нет."""

    user_message = 'Вы еще не добавляли аятов в избранное'


@final
class TelegramFileIdNotFilledError(BaseAppError):
    """Идентификатор файла не заполнен."""


@final
class UserHasNotSearchQueryError(BaseAppError):
    """Пользователь пагинируется по аятам в поиске, но не имеет запроса в кэше."""
