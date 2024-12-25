# The MIT License (MIT).
#
# Copyright (c) 2023-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

"""Config from string."""

from typing import final, override

import attrs
import yaml
from cron_validator import CronValidator  # type: ignore [import-untyped]

from main.exceptions import InvalidaCronError, InvalidConfigError
from main.services.revive_config.revive_config import ConfigDict, ReviveConfig


@final
@attrs.define(frozen=True)
class StrReviveConfig(ReviveConfig):
    """Config from string."""

    _config: str

    @override
    def parse(self) -> ConfigDict:
        """Parse config."""
        parsed_config: ConfigDict | None = yaml.safe_load(self._config)
        if not parsed_config:
            raise InvalidConfigError
        if parsed_config.get('cron'):
            # TODO: notify repository owner
            try:
                CronValidator.parse(parsed_config['cron'])
            except ValueError as err:
                msg = 'Cron expression: "{0}" has invalid format'.format(parsed_config['cron'])
                raise InvalidaCronError(msg) from err
        return parsed_config
