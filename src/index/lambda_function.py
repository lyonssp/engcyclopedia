import boto3
import json
import os
import requests
from requests_aws4auth import AWS4Auth


def lambda_handler(event, context):
    bucket = os.getenv('BUCKET_NAME')
    search_endpoint = os.getenv('SEARCH_ENDPOINT')
    region = os.getenv('AWS_REGION')

    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key,
                       region, service, session_token=credentials.token)

    index = 'articles'
    search_url = f"{search_endpoint}/_cat/indices"

    s3 = boto3.client('s3')

    # Make the signed HTTP request
    r = requests.get(search_url, auth=awsauth)

    response = s3.list_objects_v2(Bucket=bucket)
    contents = response['Contents']

    bucket_results = {}
    for obj in contents:
        response = s3.get_object(Bucket=bucket, Key=obj['Key'])
        body = json.loads(response['Body'].read())
        bucket_results[obj['Key']] = len(body)

    return {
        'statusCode': 200,
        'body': {
            "bucket_results": bucket_results,
            "search_result": r.text
        },
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }
