# Engcyclopedia

A search engine for engineering blogs

## Setup

Start a local elasticsearch instance

```
docker-compose up
```

## Scraping

```
pipenv run python src/modules/{module}/scrape.py
```

## Indexing

```
pipenv run python src/modules/{module}/index.py
```
