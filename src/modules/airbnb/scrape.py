import sys
import logging

from lib.scrape.medium import MediumScraper

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

if __name__ == "__main__":
    publisher = "airbnb"
    archive_url = "https://medium.com/airbnb-engineering/archive"
    scraper = MediumScraper(publisher, archive_url)

    with open(f'data/{publisher}.json', 'wb') as f:
        scraper.scrape_to_json(f)
