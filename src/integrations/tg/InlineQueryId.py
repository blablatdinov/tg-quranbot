from typing import SupportsInt, final, override

import attrs
from pyeo import elegant

from app_types.update import Update
from integrations.tg.exceptions.update_parse_exceptions import InlineQueryNotFoundError
from services.ErrRedirectJsonPath import ErrRedirectJsonPath
from services.JsonPathValue import JsonPathValue


@final
@attrs.define(frozen=True)
@elegant
class InlineQueryId(SupportsInt):
    """Идентификатор инлайн поиска."""

    _update: Update

    @override
    def __int__(self) -> int:
        """Числовое представление.

        :return: int
        """
        return int(
            ErrRedirectJsonPath(
                JsonPathValue(
                    self._update.asdict(),
                    '$..inline_query.id',
                ),
                InlineQueryNotFoundError(),
            ).evaluate(),
        )
