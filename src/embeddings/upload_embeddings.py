import json

import boto3
import pinecone
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

bucket = "engcyclopedia-scrape-data"
blog_id = "airbnb"
hf_token = "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"
pinecone_api_key = "3b3a3c31-e934-461c-ac1b-02334c883265"


def main():
    pinecone.init(
        api_key=pinecone_api_key,
        environment='gcp-starter'
    )

    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket, Key=f"{blog_id}.json")
    body = json.loads(response['Body'].read())

    splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=128)
    for article in tqdm(body, desc="articles"):
        article_id = str(article["id"])  # casting because this seems to get interpreted as int
        contents = article["content"]
        docs = splitter.split_text(contents)
        embeddings = query(docs)
        pinecone_embeddings = [
            (
                f"{article_id}:{i}",
                emb,
                {
                    "article_id": article_id,
                    "blog_description": blog_id,
                    "article_url": article["url"],
                    "snippet": snippet(docs[i]),
                    "text": docs[i]
                }
            ) for i, emb in enumerate(embeddings)]
        # print(f"Sample embedding: {pinecone_embeddings[0]}")
        upload_embeddings(pinecone_embeddings)


def query(texts):
    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
    headers = {"Authorization": f"Bearer {hf_token}"}
    response = requests.post(api_url, headers=headers, json={"inputs": texts, "options": {"wait_for_model": True}})
    response.raise_for_status()
    return response.json()


def upload_embeddings(embeddings):
    index = pinecone.Index("engcyclopedia")
    index.upsert(vectors=embeddings)
    pass


def snippet(text):
    size = 50
    return text[:size] + "..." if len(text) > size else text


if __name__ == "__main__":
    main()
