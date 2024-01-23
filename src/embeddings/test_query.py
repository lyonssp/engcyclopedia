import json

import boto3
import pinecone
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter

hf_token = "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"
pinecone_api_key = "3b3a3c31-e934-461c-ac1b-02334c883265"


def main():
    pinecone.init(
        api_key=pinecone_api_key,
        environment='gcp-starter'
    )

    query = "load testing"
    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
    headers = {"Authorization": f"Bearer {hf_token}"}
    response = requests.post(api_url, headers=headers, json={"inputs": [query], "options": {"wait_for_model": True}})
    embedded = response.json()[0]

    index = pinecone.Index("engcyclopedia")
    query_result = index.query(vector=embedded, top_k=10, include_metadata=True)
    print(query_result)


if __name__ == "__main__":
    main()
