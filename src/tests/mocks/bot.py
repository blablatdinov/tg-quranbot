from aiogram import Bot, types


class BotMock(Bot):

    sended_messages: list[types.Message] = []

    def __init__(self) -> None:
        pass

    async def send_audio(self, chat_id, audio, reply_markup):
        return types.Message(**{  # noqa: WPS517
            'message_id': 12120,
            'from': {
                'id': 705810219,
                'is_bot_init': True,
                'first_name': 'Quran',
                'username': 'Quran_365_bot_init',
            },
            'chat': {
                'id': chat_id,
                'first_name': 'Алмаз',
                'last_name': 'Илалетдинов',
                'username': 'ilaletdinov',
                'type': 'private',
            },
            'date': 1582624476,
            'audio': {
                'duration': 0,
                'mime_type': 'audio/mpeg',
                'title': 'Остерегайтесь сект!',
                'performer': 'Шамиль Аялутдинов',
                'file_id': audio,
                'file_unique_id': 'AgAD-AcAAsLUeEo',
                'file_size': 29956029,
            },
        })

    async def send_message(self, chat_id, text, reply_markup):
        return types.Message(**{  # noqa: WPS517
            'message_id': 20810,
            'from': {
                'id': 358610865,
                'is_bot': False,
                'first_name': 'Алмаз',
                'last_name': 'Илалетдинов',
                'username': 'ilaletdinov',
                'language_code': 'ru',
            },
            'chat': {
                'id': chat_id,
                'first_name': 'Алмаз',
                'last_name': 'Илалетдинов',
                'username': 'ilaletdinov',
                'type': 'private',
            },
            'date': 1658397839,
            'text': text,
        })
