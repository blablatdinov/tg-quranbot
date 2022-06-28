import json
from typing import Union, Optional

from pydantic import BaseModel, ValidationError


class StartMessageMeta(BaseModel):
    referrer: Optional[int] = None


def get_start_message_query(message: str) -> StartMessageMeta:
    try:
        splitted_message = message.split(' ')
        if len(splitted_message) == 1:
            return StartMessageMeta(referrer=None)

        # new format
        message_raw_meta = ' '.join(splitted_message[1:])
        try:
            return StartMessageMeta.parse_raw(message_raw_meta)
        except ValidationError:
            return StartMessageMeta(referrer=int(splitted_message[1]))
    except Exception as e:
        return StartMessageMeta(referrer=None)
