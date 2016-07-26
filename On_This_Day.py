from __future__ import print_function

import boto3, logging
from boto3.dynamodb.conditions import Key, Attr
import config

# aws lambda update-function-code --region us-east-1 --function-name On_This_Day --zip-file fileb://On_This_Day.zip


def handler(event, context):
    logging.getLogger().setLevel(logging.INFO)
    logging.info('On_This_Day.handler')
    logging.info('event {}'.format(event))
    logging.info('context {}'.format(context))

    s3_client = boto3.client('s3')

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(config.dynamo_table)

    if 'Records' in event:
        message = extract_sns_message(event, context)
    else:
        # else called directly
        message = event

    args = {
        #FilterExpression=Attr('month_day').eq('05-01')
        #'FilterExpression':'month_day=:md',
        'KeyConditionExpression':'month_day=:md',
        'ExpressionAttributeValues':{':md':message['this_day']},
        'ReturnConsumedCapacity': 'INDEXES',
        'IndexName': 'month_day-index'
    }

    resp = table.query(**args)

    logging.info(resp)

    out = {'Items':[]}

    if 'Items' in resp:
        for item in resp['Items']:
            url = s3_client.generate_presigned_url('get_object',
                Params = {'Bucket': item['bucket'], 'Key': item['object_key']},
                ExpiresIn=172800
            )
            item['url_presigned'] = url
            out['Items'].append(item)

        return out


def extract_sns_message(event, context):
    for record in event['Records']:
        logging.info('looking at {}'.format(record))
        if 'aws:sns' == record['EventSource']:
            message = json.loads(record['Sns']['Message'])
            return message
