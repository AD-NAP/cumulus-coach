import chromadb

client = chromadb.PersistentClient("./data")
col = client.get_collection(name="aws_docs")

def retrieve(query, k=3): 
    answer = col.query(query_texts=query, n_results=k)
    result = []
    for text, metadata , distance in zip(answer["documents"][0], answer["metadatas"][0], answer["distances"][0]):
        result.append({"text": text, "source": metadata.get("source"), "distance": distance})
    return result

if __name__ == "__main__":
    queries = [
        # on-topic: the docs answer these
        "What is the shared responsibility model?",
        "What are the six advantages of cloud computing?",
        "Which AWS services store data?",
        "What is Amazon S3?",
        "What does the customer manage under the shared responsibility model?",
        "What domains does the CLF-C02 exam cover?",
        "What is an Availability Zone?",
        "What is Amazon EC2 used for?",
        # near-topic: AWS words, but the docs can't answer
        "what is your favourite AWS colour?",
        "How much will AWS cost per month for my startup?",
        "Who founded AWS?",
        "How do I configure Kubernetes on Azure?",
        "What is the AWS stock price today?",
        "Is AWS better than Google Cloud?",
        # off-topic: nothing to do with AWS
        "What is a good pasta recipe?",
        "How do I tie a tie?",
        "Which football team is best in Singapore?",
        "What is the capital of France?",
    ]

    for query in queries:
        best = retrieve(query, k=1)[0]          # k=1: only the closest chunk
        print(f"{best['distance']:.3f}  {query}")