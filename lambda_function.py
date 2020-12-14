import json

import time
import boto3
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection

# AmazonS3ReadOnlyAccess

# AmazonRekognitionFullAccess

# s3://layer.lambda.aws/elasticsearch.zip



es_endpoint = 'search-photos-tmekumoyygkksr5uqzxqoqwavi.us-east-1.es.amazonaws.com'  # without 'https://'

rekognition = boto3.client('rekognition')
credentials = boto3.Session().get_credentials()
es = Elasticsearch(
    hosts = [{'host': es_endpoint, 'port':443}],
    http_auth = AWS4Auth(credentials.access_key, credentials.secret_key, 'us-east-1', 'es', session_token=credentials.token),
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)

def detect_label(s3_bucket, object_key):
    response = rekognition.detect_labels(
        Image={
            'S3Object': {
                'Bucket': s3_bucket,
                'Name': object_key
            }
        },
        MaxLabels=10
    )
    labels = []
    for label in response['Labels']:
        labels.append(label['Name'])
    return labels



def get_photo_info(object_key, s3_bucket, labels):
    return {
        "objectKey": object_key,
        "bucket": s3_bucket,
        "createdTimestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "labels": labels
    }
    
def index_photo(photo_info):
    es.index(index='photos', doc_type = 'photo', id = photo_info['objectKey'], body = photo_info)
    




def lambda_handler(event, context):
    print(event)
    # print(es.get(index='photos', doc_type = 'photo', id='photo.jpg'))
    records = event['Records']
    
    for record in records:
        s3_bucket = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        # rekognition
        labels = detect_label(s3_bucket, object_key)
        photo_info = get_photo_info(object_key, s3_bucket, labels)
        # es
        index_photo(photo_info)
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }