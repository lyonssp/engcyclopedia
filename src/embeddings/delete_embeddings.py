import pinecone

pinecone_api_key = "3b3a3c31-e934-461c-ac1b-02334c883265"


def main():
    pinecone.init(
        api_key=pinecone_api_key,
        environment='gcp-starter'
    )
    index = pinecone.Index("engcyclopedia")
    index.delete(delete_all=True)


if __name__ == "__main__":
    main()
