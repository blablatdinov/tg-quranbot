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
import datetime
import json
import time

import pika
import pytest

from settings.env_file_settings import EnvFileSettings


@pytest.mark.usefixtures('_bot_process', '_clear_db')
def test(db_query_vals):
    settings = EnvFileSettings.from_filename('../.env')
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost',
        port=5672,
        credentials=pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS),
    ))
    channel = connection.channel()
    channel.queue_declare(queue='my_queue')
    channel.basic_publish(
        exchange='',
        routing_key='my_queue',
        body=json.dumps({
            'event_id': 'some_id',
            'event_version': 1,
            'event_name': 'Prayers.Created',
            'event_time': '392409283',
            'producer': 'some producer',
            'data': {
                'name': 'fajr',
                'time': '5:36',
                'city_id': '4075504b-4b6f-4978-bf9c-8ecd5ecf9192',
                'day': '2023-01-02',
            },
        }).encode('utf-8'),
    )

    time.sleep(5)

    assert db_query_vals('SELECT name, time, city_id, day FROM prayers ORDER BY prayer_id DESC LIMIT 1') == [
        ('fajr', datetime.time(5, 36), '4075504b-4b6f-4978-bf9c-8ecd5ecf9192', datetime.date(2023, 1, 2)),
    ]
