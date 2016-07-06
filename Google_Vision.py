from __future__ import print_function
import boto3
import base64
import uuid, hashlib, pprint, logging, json

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

DISCOVERY_URL='https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'

def handler(event, context):
    logging.getLogger().setLevel(logging.INFO)
    logging.info('Google_Vision.handler')
    logging.info('event {}'.format(event))

    if 'Records' in event:
        message = extract_sns_message(event, context)
    else:
        # else called directly
        message = event

    download_path = fetch_photo(message['bucket'], message['key'])
    logging.info("downloaded {}/{} to {}".format(message['bucket'], message['key'], download_path))
    response = google_all_seeing_eye_dwim(download_path)
    logging.info("detect face response: {}".format(response))

def google_all_seeing_eye_dwim(download_path, max_results=10):
    try:
        image = open(download_path, 'rb')
        image_content = image.read()
    except IOError as err:
        logging.error("Failed to read image {}: {}").format(download_path, err)
        return

    batch_request = [{
        'image': {
            'content': base64.b64encode(image_content).decode('UTF-8')
        },
        'features': [{
            'type': 'FACE_DETECTION',
            'maxResults': max_results,
        },
        {
            'type': 'LABEL_DETECTION',
            'maxResults': max_results,
        },
        {
            'type': 'IMAGE_PROPERTIES',
            'maxResults': max_results,
        },
        {
            'type': 'SAFE_SEARCH_DETECTION',
            'maxResults': max_results,
        }]
    }]

    service = get_vision_service()
    request = service.images().annotate(body={
        'requests': batch_request,
    })
    response = request.execute()
    return response

def fetch_photo(bucket, key):
    s3_client = boto3.client('s3')

    download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
    data = {}

    try:
        s3_client.download_file(bucket, key, download_path)
    except IOError as err:
        logging.error("Failed to download image {}/{} with {}").format(bucket, key, err)
        return

    return download_path

def get_vision_service():
    credentials = GoogleCredentials.from_stream('./application_default_credentials.json')
    return discovery.build('vision', 'v1', credentials=credentials,
                           discoveryServiceUrl=DISCOVERY_URL)

def extract_sns_message(event, context):
    for record in event['Records']:
        logging.info('looking at {}'.format(record))
        if 'aws:sns' == record['EventSource']:
            message = json.loads(record['Sns']['Message'])
            return message
