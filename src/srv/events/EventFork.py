from typing import final, override

import attrs
from eljson.json import Json
from pyeo import elegant

from srv.events.recieved_event import ReceivedEvent


@elegant
@attrs.define(frozen=True)
@final
class EventFork(ReceivedEvent):
    """Событие."""

    _name: str
    _version: int
    _origin: ReceivedEvent

    @override
    async def process(self, json_doc: Json) -> None:
        """Обработать событие.

        :param json_doc: Json
        """
        name_match = json_doc.path('$.event_name')[0] == self._name
        version_match = json_doc.path('$.event_version')[0] == self._version
        if name_match and version_match:
            await self._origin.process(json_doc)
