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
    queries = ["What is the shared responsibility model?",
               "What are the six advantages of cloud computing?",
               "Which AWS services store data?",
               "What is a good pasta recipe?",
               "what is your favourite AWS colour?"]

    for i, query in enumerate(queries):         # outer loop: one question at a time
        results = retrieve(query)
        print(f"Q{i}", query)
        for r in results:                       # inner loop: each chunk for this question
            print("  distance:", round(r["distance"], 3))
            print("  source:", r["source"])
            print("  text:", r["text"][:100])   # shorten only when printing
        print()