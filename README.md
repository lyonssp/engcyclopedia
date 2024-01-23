# Engcyclopedia

A natural language search engine for engineering blogs

## Scraping

```
pipenv run python src/modules/{module}/scrape.py
```

## Upload Scrape Data

```
aws-vault exec engcylopedia -- aws s3 cp data/{module}.json s3://engcyclopedia-scrape-data/{module}.json
```

## Upload Embeddings

```
aws-vault exec engcylopedia -- pipenv run python src/embeddings/upload_embeddings.py
```

Note: currently hard-coded to upload slack embeddings for testing
