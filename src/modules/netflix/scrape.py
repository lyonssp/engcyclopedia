import sys
import logging

from src.lib.scrape.scrape import MediumScraper

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

if __name__ == "__main__":
    publisher = "netflix"
    archive_url = "https://netflixtechblog.com/archive"
    scraper = MediumScraper(publisher, archive_url)

    with open('data/netflix.json', 'wb') as f:
        scraper.scrape_to_json(f)
