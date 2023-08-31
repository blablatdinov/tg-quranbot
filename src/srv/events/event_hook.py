import asyncio
import json
from typing import Protocol, final
import enum

import aioamqp
import attrs
from databases import Database
from eljson.json_doc import JsonDoc
from pyeo import elegant

from app_types.runable import SyncRunable
from settings import Settings
from srv.events.recieved_event import ReceivedEvent


class EventCatchStatus(enum.Enum):

    unprocessed = 0
    processed = 1


@elegant
class EventHook(Protocol):

    async def catch(self): ...


@final
@attrs.define(frozen=True)
@elegant
class EventHookApp(SyncRunable):

    _event_hook: EventHook

    def run(self, args: list[str]) -> int:
        asyncio.run(self._event_hook.catch())
        return 0


@final
@elegant
class RbmqEventHook(EventHook):

    def __init__(self, settings: Settings, pgsql: Database, *events: tuple[str, int, type[ReceivedEvent]]):
        self._settings = settings
        self._events = events
        self._pgsql = pgsql

    async def catch(self):
        await self._pgsql.connect()
        transport, protocol = await aioamqp.connect()
        channel = await protocol.channel()
        await channel.queue_declare(queue_name='my_queue')
        await channel.basic_consume(self._callback, queue_name='my_queue')
        print("Waiting for messages...")
        try:
            while True:
                await asyncio.sleep(1)
        finally:
            await protocol.close()
            transport.close()

    async def _callback(self, channel, body: bytes, envelope, properties):
        body_json = JsonDoc.from_string(body.decode('utf-8'))
        from pprint import pprint
        pprint(json.loads(body.decode('utf-8')))
        for event in self._events:
            print(body_json.path('$.event_name'))
            if body_json.path('$.event_name')[0] == event[0]:
                await event[2](body_json, self._pgsql).process()
                await channel.basic_client_ack(envelope.delivery_tag)
                return
