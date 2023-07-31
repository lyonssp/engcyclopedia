import sys
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import logging
import json

from tqdm import tqdm

from lib.scrape.scrape import MediumScraper

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

if __name__ == "__main__":
    publisher = "pinterest"
    archive_url = "https://medium.com/pinterest-engineering/archive"

    scraper = MediumScraper(publisher, archive_url)

    meta = json.load(open(f'data/{publisher}.json', 'r'))

    es = Elasticsearch(
        "https://localhost:9200",
        ca_certs="/home/seanlyons/Code/engcyclopedia/certs/ca/ca.crt",
        basic_auth=("elastic", "18_=+cO*7cqJq2YabgLb")
    )

    for m in tqdm(meta):
        article_id = m['id']
        content = scraper.scrape_article_content(m['url'])
        doc = {**m, "content": content}
        es.index(
            index="articles",
            id=m['id'],
            document=m
        )

    """
    actions = []
    for m in tqdm(meta):
        article_id = m['id']
        content = scraper.scrape_article_content(m['url'])
        doc = {**m, "content": content}
        actions.append({
            '_op_type': 'update',
            '_index': 'articles',
            '_id': article_id,
            'doc': doc
        })

    bulk(es, actions)
    """
