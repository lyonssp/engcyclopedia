import boto3
import json
import os
import requests
from requests import HTTPError
from requests_aws4auth import AWS4Auth


def lambda_handler(event, context):
    blog_id = event['blog_id']

    bucket = os.getenv('BUCKET_NAME')
    search_endpoint = os.getenv('SEARCH_ENDPOINT')
    region = os.getenv('AWS_REGION')

    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key,
                       region, service, session_token=credentials.token)

    search_index = 'articles'

    s3 = boto3.client('s3')

    response = s3.get_object(Bucket=bucket, Key=f"{blog_id}.json")
    body = json.loads(response['Body'].read())

    bulk_line_items = []
    print(f"Indexing {len(body)} articles")
    for article in body:
        bulk_line_items.append({"index": {"_index": search_index, "_id": article['id']}})
        bulk_line_items.append(article)

    # note: newline required at end of request body
    request_body = '\n'.join(json.dumps(d) for d in bulk_line_items) + "\n"
    bulk_url = f"{search_endpoint}/{search_index}/_bulk?pretty"
    r = requests.post(bulk_url, auth=awsauth, data=request_body, headers={"Content-Type": "application/x-ndjson"})

    print(f"Bulk index response: {r.status_code} {r.text}")
    r.raise_for_status()

    return {
        'statusCode': 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }
