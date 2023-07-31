import sys
from elasticsearch import Elasticsearch
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
    meta = json.load(open('data/airbnb.json', 'r'))

    es = Elasticsearch(
        "https://localhost:9200",
        ca_certs="/home/seanlyons/Code/engcyclopedia/certs/ca/ca.crt",
        basic_auth=("elastic", "18_=+cO*7cqJq2YabgLb")
    )
    for m in meta:
        logger.info(f"indexing article {m['id']}")
        content = get_article_content(m['url'])
        doc = {**m, "content": content}
        es.index(
            index="articles",
            id=m['id'],
            document=doc
        )
