import time

from aiogram import types

from integrations.nats_integration import MessageBrokerInterface


class UpdatesLogRepositoryInterface(object):
    """Интерфейс для работы с хранилищем пакетов от телеграма."""

    async def save_callback_query(self, callback_query: types.CallbackQuery):
        """Сохранить информацию о нажатии на кнопку.

        :param callback_query: types.CallbackQuery
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def save_messages(self, messages: list[types.Message]):
        """Массовое сохранение сообщений.

        :param messages: list[types.Message]
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def save_messages_with_trigger_message(self, messages: list[types.Message], trigger_message_id: int):
        """Массовое сохранение сообщений.

        :param messages: list[types.Message]
        :param trigger_message_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class UpdatesLogRepository(UpdatesLogRepositoryInterface):

    def __init__(self, message_broker: MessageBrokerInterface):
        self._message_broker = message_broker

    async def save_callback_query(self, callback_query: types.CallbackQuery):
        """Сохранить информацию о нажатии на кнопку.

        :param callback_query: types.CallbackQuery
        """
        await self._message_broker.send(
            {
                'json': callback_query.to_python(),
                'timestamp': str(int(time.time())),
            },
            'Button.Pushed',
            1,
        )

    async def save_messages(self, messages: list[types.Message]):
        """Массовое сохранение сообщений.

        :param messages: list[types.Message]
        """
        await self._message_broker.send(
            {
                'messages': [
                    {
                        'message_json': message.to_python(),
                        'is_unknown': False,
                        'trigger_message_id': None,
                    }
                    for message in messages
                ],
            },
            'Messages.Created',
            1,
        )

    async def save_messages_with_trigger_message(self, messages: list[types.Message], trigger_message_id: int):
        """Массовое сохранение сообщений.

        :param messages: list[types.Message]
        :param trigger_message_id: int
        :raises NotImplementedError: if not implemented
        """
        await self._message_broker.send(
            {
                'messages': [
                    {
                        'message_json': message.to_python(),
                        'is_unknown': False,
                        'trigger_message_id': trigger_message_id if trigger_message_id != message.message_id else None,
                    }
                    for message in messages
                ],
            },
            'Messages.Created',
            1,
        )
