from __future__ import print_function
import boto3
import base64
import cStringIO
import uuid, hashlib, pprint, logging, json
from PIL import Image
import thumb
import config

def handler(event, context):
    logging.getLogger().setLevel(logging.INFO)
    logging.info('Thumb_B64.handler')
    logging.info('event {}'.format(event))

    do_sns = False

    if 'Records' in event:
        message = extract_sns_message(event, context)
        do_sns = True
    else:
        # else called directly
        message = event

    download_path = fetch_photo(message['bucket'], message['key'])
    image = Image.open(download_path)
    image = thumb.square_thumb(image, 320)
    buffer = cStringIO.StringIO()
    image.save(buffer, format="JPEG")
    thumb_b64_str = base64.b64encode(buffer.getvalue())
    logging.info("as b64 {}".format(thumb_b64_str))

    message['thumb_b64'] = thumb_b64_str

    if do_sns:
        sns = boto3.client('sns')
        logging.info('attempting to publish to {}'.format(config.output_sns_topic))

        sns.publish(
            TopicArn=config.output_sns_topic,
            Message=json.dumps(message))
    else:
        return message


def fetch_photo(bucket, key):
    s3_client = boto3.client('s3')

    download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
    data = {}

    try:
        logging.info("download {}/{} to {}".format(bucket, key, download_path))
        s3_client.download_file(bucket, key, download_path)
    except IOError as err:
        logging.error("Failed to download image {}/{} with {}").format(bucket, key, err)
        return

    return download_path

def extract_sns_message(event, context):
    for record in event['Records']:
        logging.info('looking at {}'.format(record))
        if 'aws:sns' == record['EventSource']:
            message = json.loads(record['Sns']['Message'])
            return message
