import sys
import requests
import logging
import time
from bs4 import BeautifulSoup


class MediumScraper():
    def __init__(self, publisher, archive_url) -> None:

        self._logger = logging.getLogger()
        self._logger.setLevel(logging.INFO)
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        self._publisher = publisher
        self._archive_url = archive_url

    def _extract_content(self, html):
        """
        Remove html tags from an article's content
        """

        soup = BeautifulSoup(html, "html.parser")

        article = soup.find('article')

        for data in article(['style', 'script']):
            data.decompose()

        return ' '.join(article.stripped_strings)

    def _get_img(self, img_url, dest_folder, dest_filename):
        ext = img_url.split('.')[-1]
        if len(ext) > 4:
            ext = 'jpg'
        dest_filename = f'{dest_filename}.{ext}'
        with open(f'{dest_folder}/{dest_filename}', 'wb') as f:
            f.write(requests.get(img_url, allow_redirects=False).content)
        return dest_filename

    def _get_article_metadata(self, year, month):
        article_counter = 0
        url = f"{self._archive_url}/{year}/{month:02d}"

        self._logger.info(f"scraping {url}")

        response = requests.get(url, allow_redirects=True)

        if response.status_code > 299:
            self._logger.info(
                f"skipping url for bad status code: url={url} status_code={response.status_code}")
            return None

        # requests for months with no blog posts return the archive
        # page for the given year or the archive main page if the year has no blog posts
        if response.url == f"{self._archive_url}/{year}":
            self._logger.info(f"no blog posts for {url}")
            return None

        data = []
        page = response.content
        soup = BeautifulSoup(page, 'html.parser')

        articles = soup.find_all(
            "div",
            class_="postArticle postArticle--short js-postArticle js-trackPostPresentation js-trackPostScrolls")

        for article in articles:
            title = article.find("h3", class_="graf--title")
            if title is None:
                continue

            title = title.contents[0]

            article_counter += 1
            article_id = f'{self._publisher}-{year}-{month:02d}-{article_counter:02d}'

            subtitle = article.find("h4", class_="graf--subtitle")
            subtitle = subtitle.contents[0] if subtitle is not None else ''

            image = article.find("img", class_="graf-image")
            image = '' if image is None else self._get_img(
                image['src'], 'images', f'{article_id}')

            article_url = article.find_all("a")[3]['href'].split('?')[0]

            data.append([article_id,
                        article_url,
                        title,
                        subtitle,
                        image,
                        self._publisher,
                        '{0}-{1:02d}'.format(year, month)])

        return data

    def scrape_to_json(self, writer):
        # we will miss articles published on leap day for now
        years = range(2023, 2024)
        months = range(1, 13)

        self._logger.info("=== dates dimensions ===")
        self._logger.info(f"years: {years}")
        self._logger.info(f"months: {months}")

        data = []
        for year in years:
            for month in months:
                scraped = self._get_article_metadata(year, month)
                if scraped is not None:
                    data.extend(scraped)

                time.sleep(2)

        cols = ['id',
                'url',
                'title',
                'subtitle',
                'image',
                'publication',
                'date']

        df = pd.DataFrame(data, columns=cols)
        df.to_json(writer, orient='records')

        return data

    def scrape_article_content(self, url):
        response = requests.get(url, allow_redirects=True)
        return self._extract_content(response.text)
