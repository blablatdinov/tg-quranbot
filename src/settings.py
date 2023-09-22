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
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol, final, overload

import attrs
from pyeo import elegant

from app_types.supports_bool import SupportsBool

BASE_DIR = Path(__file__).parent


@elegant
class Settings(Protocol):
    """Настройки."""

    def __getattr__(self, attr_name: str) -> str:
        """Получить аттрибут.

        :param attr_name: str
        """


@final
@attrs.define(frozen=True)
class CachedSettings(Settings):
    """Кеширующиеся настройки."""

    _origin: Settings
    _cached_values: dict[str, str] = {}

    def __getattr__(self, attr_name) -> str:
        """Получить аттрибут.

        :param attr_name: str
        :return: str
        """
        cached_value = self._cached_values.get(attr_name)
        if not cached_value:
            origin_value = getattr(self._origin, attr_name)
            self._cached_values[attr_name] = origin_value
            return origin_value
        return cached_value


@final
@elegant
@attrs.define(frozen=True)
class OsOrFileSettings(Settings):
    """Объект, который достает настройки из переменных окружения или файла."""

    _os_envs: Settings
    _env_file: Settings

    def __getattr__(self, attr_name):
        """Получить аттрибут.

        :param attr_name: str
        :return: str
        """
        try:
            return getattr(self._os_envs, attr_name)
        except ValueError:
            return getattr(self._os_envs, attr_name)


@final
@elegant
@attrs.define(frozen=True)
class EnvFileSettings(Settings):
    """Настройки из .env файла."""

    _path: Path

    @classmethod
    def from_filename(cls, file_path: str) -> Settings:
        """Конструктор для имени файла.

        :param file_path: str
        :return: Settings
        """
        return cls(Path(BASE_DIR / file_path))

    def __getattr__(self, attr_name):
        """Получить аттрибут.

        :param attr_name: str
        :return: str
        """
        if attr_name == 'BASE_DIR':
            return BASE_DIR
        return self._search_in_file(attr_name)

    def _search_in_file(self, attr_name) -> str:
        for line in self._path.read_text().strip().split('\n'):
            if '=' not in line:
                continue
            var_name, var_value = line.split('=')
            if var_name == attr_name:
                return var_value
        raise ValueError('{0} not defined'.format(attr_name))


@final
@elegant
@attrs.define(frozen=True)
class OsEnvSettings(Settings):
    """Настройки из переменных окружения."""

    def __getattr__(self, attr_name):
        """Получить аттрибут.

        :param attr_name: str
        :return: str
        :raises ValueError: имя не найдено
        """
        if attr_name == 'BASE_DIR':
            return BASE_DIR
        env_value = os.getenv(attr_name)
        if not env_value:
            raise ValueError
        return env_value


@final
@elegant
@attrs.define(frozen=True)
class DebugMode(SupportsBool):
    """Режим отладки."""

    _settings: Settings

    def __bool__(self) -> bool:
        """Приведение к булевому значению.

        :return: bool
        """
        return self._settings.DEBUG == 'on'


@final
@attrs.define(frozen=True)
class AdminChatIds(Sequence[int]):
    """Список идентификаторов администраторов."""

    _settings: Settings

    @overload
    def __getitem__(self, idx: int) -> int:
        """Тип для индекса.

        :param idx: int
        """

    @overload
    def __getitem__(self, idx: slice) -> Sequence[int]:
        """Тип для среза.

        :param idx: slice
        """

    def __getitem__(self, idx: int | slice) -> int | Sequence[int]:
        """Получить элемент.

        :param idx: int
        :return: int
        """
        return [
            int(chat_id.strip()) for chat_id in self._settings.ADMIN_CHAT_IDS.split(',')
        ][idx]

    def __len__(self) -> int:
        """Кол-во администраторов.

        :return: int
        """
        return len(self._settings.ADMIN_CHAT_IDS.split(','))

    def count(self, search_value: int) -> int:
        """Кол-во элементов.

        :param search_value: int
        :return: int
        """
        return [
            int(chat_id.strip()) for chat_id in self._settings.ADMIN_CHAT_IDS.split(',')
        ].count(search_value)
