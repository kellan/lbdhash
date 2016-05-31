from __future__ import print_function
import boto3
import os
import sys
import uuid
from PIL import Image
import hashlib
import pprint
import logging
import json

import dhash
import exif
import config

#
# trigger via SNS with
#{"default":"SNS requires this",
#  "bucket":"kellanio-alestic-lambda-example",
#  "object":"jazz-thailand.JPEG"}
#

def handler(event, context):
    logging.getLogger().setLevel(logging.INFO)
    logging.info('Img_Dhash.handler')
    logging.info('event {}'.format(event))

    if 'Records' in event:
        for record in event['Records']:
            logging.info('looking at {}'.format(record))
            if 'aws:sns' == record['EventSource']:
                handle_sns(record['Sns'], context)
            else:
                logger.info('not an sns event')
                pprint.pprint(event)
    elif 'bucket' in event:
        # invoked directly: aws lambda invoke --function-name Img_DhashPy --region us-west-2 --payload '{"bucket":"kellanio-alestic-lambda-example","key":"jazz-thailand.JPEG"}'
        return hash_photo(event['bucket'], event['key'])

def handle_sns(sns_event, context):
    logging.info('handle_sns')
    bucket, key = sns_event['Message'].split(' ')
    photo_hash = hash_photo(bucket, key)
    logging.info('photo_hash {}'.format(photo_hash['dhash']))

    sns = boto3.client('sns')
    logging.info('attempting to publish')

    sns.publish(
        TopicArn=config.output_sns_topic,
        Message=json.dumps(photo_hash))


def hash_photo(bucket, key):
    s3_client = boto3.client('s3')

    #bucket = 'kellanio-alestic-lambda-example'
    #key = 'jazz-thailand.JPEG'
    download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)

    s3_client.download_file(bucket, key, download_path)
    image = Image.open(download_path)
    image_dhash = dhash.dhash(image)
    image_sha256 = hashlib.sha256(open(download_path, 'rb').read()).hexdigest()

    data =  {'sha256': image_sha256, 'dhash': image_dhash, 'format': img.format}

    if img.format == 'JPEG':
        exif_data = exif.get_exif_data(image)
        taken_date = exif_data.get('DateTime', '')
        lat, lon = exif.get_lat_lon(exif_data)
        camera = exif.get_camera(exif_data)
        data.update({'date_taken':taken_date, 'lat':lat, 'lon':lon, 'camera':camera})

    return data
