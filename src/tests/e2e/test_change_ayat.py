import json
import time

import pytest
import pika


@pytest.mark.usefixtures('bot_process', 'clear_db')
def test_change_ayat(db_query_vals):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='my_queue')
    channel.basic_publish(
        exchange='',
        routing_key='my_queue',
        body=json.dumps({
            'event_id': 'some_id',
            'event_version': 1,
            'event_name': 'Ayat.Changed',
            'event_time': '392409283',
            'producer': 'some producer',
            'data': {
                'public_id': '0acec6b6-4b3c-4ce9-8d11-3985f52a1c03',
                'day': 2,
                'audio_id': 'a2ed8d0e-ce4b-4994-9a12-e36482263cb7',
                'ayat_number': '1-3',
                'content': 'Updated content',
                'arab_text': 'Updated arab text',
                'transliteration': 'Updated arab transliteration',
            },
        }).encode('utf-8'),
    )

    time.sleep(5)

    assert db_query_vals('SELECT * FROM ayats WHERE ayat_id = 1') == [
        (
            1,
            '0acec6b6-4b3c-4ce9-8d11-3985f52a1c03',
            2,
            1,
            'a2ed8d0e-ce4b-4994-9a12-e36482263cb7',
            '1-3',
            'Updated content',
            'Updated arab text',
            'Updated arab transliteration'
        ),
    ]
