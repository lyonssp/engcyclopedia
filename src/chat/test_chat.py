import pinecone
import requests
from pinecone import QueryResponse

hf_token = "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"
pinecone_api_key = "3b3a3c31-e934-461c-ac1b-02334c883265"


def main():
    pinecone.init(
        api_key=pinecone_api_key,
        environment='gcp-starter'
    )

    query = """
    I am working on a load testing project and I am trying to figure out how to get the most out of my load testing.
    
    Our domain requires our systems handle a lot of parallel requests and we are interested in learning about
    what sorts of architectural patterns will allow us to design load tests that will reflect our user traffic.
    """
    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
    headers = {"Authorization": f"Bearer {hf_token}"}
    response = requests.post(api_url, headers=headers, json={"inputs": [query], "options": {"wait_for_model": True}})
    embedded = response.json()[0]

    index = pinecone.Index("engcyclopedia")
    query_result = index.query(vector=embedded, top_k=10, include_metadata=True)
    print(make_prompt(query_result, query))


def make_prompt(response: QueryResponse, query: str):
    prompt = f"""
    background:

    I am going to provide several chunks of text and I want you to use that context to answer the question.
    
    Metadata will be provided for each blog passage with the following fields:
   
    url: the url of the original article, to be used for citations
    text: text from a passage in an article, to be used finding information relevant to the chat

    samples:
    """

    for i, result in enumerate(response.get('matches')):
        metadata = result['metadata']
        prompt += f"""
        
        url: {metadata['article_url']}
        text: {metadata['text']}
        
        """

    prompt += f"""
    query:
    
    {query} 
    """
    return prompt


if __name__ == "__main__":
    main()
