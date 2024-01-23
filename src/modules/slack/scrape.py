import logging
import sys
import time
from bs4 import BeautifulSoup
import pandas as pd
import requests
from tqdm import tqdm
from trafilatura.sitemaps import sitemap_search

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def get_urls_from_sitemap(resource_url: str) -> list:
    """
    Get a list of urls from a sitemap with trafilatura
    """
    urls = sitemap_search(resource_url)

    # filter out urls that are not articles
    tags_prefix = 'https://slack.engineering/tags'
    skip_pages = ['https://slack.engineering',
                  'https://slack.engineering/categories/uncategorized/']
    filtered = filter(lambda x: not x.startswith(tags_prefix), urls)
    filtered = filter(lambda x: x not in skip_pages, filtered)

    return list(filtered)


def extract_content(html):
    """
    Remove html tags from an article's content
    """

    soup = BeautifulSoup(html, "html.parser")

    article = soup.find('article')

    for data in article(['style', 'script']):
        data.decompose()

    return ' '.join(article.stripped_strings)

def id_from_url(url):
    return hash(url) % ((sys.maxsize + 1) * 2)

def extract_title(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.find('h1').text


def extract_subtitle(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.find('div', class_='carousel-item__content').text


def extract_thumbnail(html):
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find('img', class_='wp-post-image')
    return element['src']


def create_dataset(url: str) -> pd.DataFrame:
    cols = ['id',
            'url',
            'title',
            'subtitle',
            'image',
            'content',
            'publication',
            'date']

    data = []
    urls = get_urls_from_sitemap(url)
    for url in tqdm(urls, desc="URLs"):
        try:
            response = requests.get(url, allow_redirects=True)
            d = [id_from_url(url),
                 url,
                 extract_title(response.text),
                 extract_subtitle(response.text),
                 extract_thumbnail(response.text),
                 extract_content(response.text),
                 'slack',
                 ''
                 ]
            data.append(d)
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"Error for url {url}: {e}")

    df = pd.DataFrame(data, columns=cols)
    df = df.drop_duplicates()
    df = df.dropna()

    return df


if __name__ == "__main__":
    publisher = "slack"
    sitemap_url = "https://slack.engineering/sitemap_index.xml"

    with open(f'data/{publisher}.json', 'wb') as f:
        df = create_dataset(sitemap_url)
        df.to_json(f, orient="records")
