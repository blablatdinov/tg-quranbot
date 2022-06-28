import json
from typing import Union


def get_start_message_query(message: str) -> Union[int, dict[str, str], None]:
    splitted_message = message.split(' ')
    if len(splitted_message) == 1:
        return None
    return json.loads(' '.join(splitted_message[1:]))

