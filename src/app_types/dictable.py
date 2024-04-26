from typing import Protocol, final

import attrs
import ujson
from pyeo import elegant


class Dictable(Protocol):

    def to_dict(self) -> dict: ...


@final
@attrs.define(frozen=True)
@elegant
class FkDict(Dictable):

    _origin: dict

    def to_dict(self) -> dict:
        return self._origin


@final
@attrs.define(frozen=True)
@elegant
class JsonDict(Dictable):

    _raw_json: str

    def to_dict(self) -> dict:
        return ujson.loads(self._raw_json)
