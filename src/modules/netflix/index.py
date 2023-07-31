import sys
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import requests
import logging
import json
from bs4 import BeautifulSoup

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def extract_content(html):
    """
    Remove html tags from an article's content
    """

    soup = BeautifulSoup(html, "html.parser")

    article = soup.find('article')

    for data in article(['style', 'script']):
        data.decompose()

    return ' '.join(article.stripped_strings)


def get_article_content(url):
    response = requests.get(url, allow_redirects=True)
    return extract_content(response.text)


if __name__ == "__main__":
    meta = json.load(open('data/netflix.json', 'r'))

    es = Elasticsearch(
        "https://localhost:9200",
        ca_certs="/home/seanlyons/Code/engcyclopedia/certs/ca/ca.crt",
        basic_auth=("elastic", "18_=+cO*7cqJq2YabgLb")
    )
    actions = []
    for m in meta:
        article_id = m['id']
        logger.info(f"preparing article {article_id}")
        content = get_article_content(m['url'])
        doc = {**m, "content": content}
        actions.append({
            '_op_type': 'update',
            '_index': 'articles',
            '_id': article_id,
            'doc': doc
        })

    bulk(es, actions)
