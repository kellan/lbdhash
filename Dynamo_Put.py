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

    s3_path = 's3://{}/{}'.format(event['bucket'], event['key'])

    key_md5 = hashlib.md5(s3_path).hexdigest()

    item = {
        'key_md5': key_md5,
        'S3_Path': s3_path,
        'CreatedAtMs': millis_since_epoch()
    }
    item.update(event)

    resp = table.put_item(Item=item)

    print(resp)

def millis_since_epoch():
    return int(round(time.time()*1000))
