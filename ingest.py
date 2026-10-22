import requests
import chromadb
from bs4 import BeautifulSoup

URLS = [
    "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/what-is-cloud-computing.html",
    "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/six-advantages-of-cloud-computing.html",
    "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/types-of-cloud-computing.html",
    "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/global-infrastructure.html",
    "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/security-and-compliance.html",
    "https://docs.aws.amazon.com/whitepapers/latest/aws-risk-and-compliance/shared-responsibility-model.html",
    "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/compute-services.html",
    "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/storage-services.html",
    "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/database.html",
    "https://docs.aws.amazon.com/aws-certification/latest/cloud-practitioner-02/cloud-practitioner-02.html",
]

def fetch_text(url):
    resp = requests.get(url, timeout=30)        # never wait forever
    resp.raise_for_status()                     # turn a 404/500 into an error instead of silently going on
    html = resp.content

    id = "main-col-body"
    soup = BeautifulSoup(html, "html.parser")
    div = soup.find(id = id)               # first element with that id, or None
    if div == None:
        raise(LookupError(id + " is not found in " + url))
    text = div.get_text(separator=" ")          # all text inside, tags removed

    clean_text = " ".join(text.split())

    return clean_text

def chunk_words(text, size=500, overlap=50): 
    chunk_list = []
    word_list = text.split()
    word_count = len(word_list)
    for n in range(0, word_count, size - overlap):
        chunk_list.append(" ".join(word_list[n:n + size]))
        if n + size >= word_count:
            break 
    return chunk_list

def store_chunk(chunks, url, col):
    
    id_list = []
    source_list = []
    for i, _ in enumerate(chunks):
        id_list.append(url + "_" + str(i))
        source_list.append({"source": url})

    # Alternative 1 liner - do the same for source_list
    # id_list = [url + "_" + str(i) for i, _ in enumerate(chunks)]

    col.upsert(
        ids=id_list,
        documents=chunks,
        metadatas=source_list
    )

if __name__ == "__main__":
    client = chromadb.PersistentClient(path="./data")
    col = client.get_or_create_collection(name="aws_docs")

    total_chunks = 0
    for url in URLS:
        clean_text = fetch_text(url)
        chunk_list = chunk_words(clean_text)
        total_chunks += len(chunk_list)
        store_chunk(chunk_list, url, col)

    print(col.count())
    print(total_chunks)
