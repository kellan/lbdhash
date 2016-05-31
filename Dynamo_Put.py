from __future__ import print_function
import boto3
import uuid
import logging
import time
import hashlib
import json
import config

def handler(event, context):
    logging.getLogger().setLevel(logging.INFO)
    logging.info('Dynamo_Put.handler')
    logging.info('event {}'.format(event))

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(config.dynamo_table)

    if 'Records' in event:
        message = extract_sns_message(event, context)
    else:
        # else called directly
        message = event

    s3_path = 's3://{}/{}'.format(message['bucket'], message['key'])

    key_md5 = hashlib.md5(s3_path).hexdigest()

    item = {
        'path_md5': key_md5,
        's3_path': s3_path,
        'record_created_ms': millis_since_epoch()
    }

    for floats in ('lat', 'lon'):
        if message[floats] and isinstance(message[floats], float):
            message[floats] = int(round(message[floats]*1000))

    message['object'] = message.pop('key') # rename, key is confusing in dynamodb land

    if 'date_taken' in message:
        message['date_taken_raw'] = message.pop('date_taken') # rename, TODO parse later


    item.update(message)

    resp = table.put_item(Item=item)

    print(resp)

def extract_sns_message(event, context):
    for record in event['Records']:
        logging.info('looking at {}'.format(record))
        if 'aws:sns' == record['EventSource']:
            message = json.loads(record['Sns']['Message'])
            return message


def millis_since_epoch():
    return int(round(time.time()*1000))
