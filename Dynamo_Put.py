from __future__ import print_function
import boto3
import uuid
import logging
import time
import hashlib
import config

def handler(event, context):
    logging.getLogger().setLevel(logging.INFO)
    logging.info('Dynamo_Put.handler')
    logging.info('event {}'.format(event))

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(config.dynamo_table)

    key = 's3://{}/{}'.format(event['bucket'], event['object'])

    key_md5 = hashlib.md5(key).hexdigest()

    item = {
        'uuid': key_md5,
        'S3_Path': key,
        'CreatedAtMs': millis_since_epoch()
    }
    item.update(event)

    resp = table.put_item(Item=item)

    print(resp)

def millis_since_epoch():
    return int(round(time.time()*1000))
