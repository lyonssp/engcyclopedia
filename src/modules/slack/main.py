import time
import pandas as pd
from tqdm import tqdm
from trafilatura.sitemaps import sitemap_search
from trafilatura import fetch_url, extract, bare_extraction


def get_urls_from_sitemap(resource_url: str) -> list:
    """
    Get a list of urls from a sitemap with trafilatura
    """
    urls = sitemap_search(resource_url)
    #downloaded = fetch_url(resource_url, target_language='en')
    #result = bare_extraction(downloaded, output_format='python', include_links=True)

    return urls


def extract_article(url: str) -> dict:
    """
    Extract article from a url
    """
    downloaded = fetch_url(url)
    article = extract(downloaded, favor_precision=True)

    return article


def create_dataset(list_of_websites: list) -> pd.DataFrame:
    """
    Create a dataframe from a list of sitemaps that is passed to get_urls_from_sitemap
    """
    data = []
    for website in tqdm(list_of_websites, desc="Websites"):
        urls = get_urls_from_sitemap(website)
        print(urls)
        for url in tqdm(urls, desc="URLs"):
            d = {
                'url': url,
                "article": extract_article(url)
            }
            data.append(d)
            time.sleep(0.5)

    df = pd.DataFrame(data)
    df = df.drop_duplicates()
    df = df.dropna()

    return df


if __name__ == "__main__":
    # place your data sources here
    list_of_websites = [
        "https://slack.engineering/sitemap_index.xml"
        #"https://www.canva.dev/sitemap.xml"
        #"https://eng.wealthfront.com"
    ]

    df = create_dataset(list_of_websites)

    df.to_csv("dataset.csv", index=False)
