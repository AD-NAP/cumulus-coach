import requests
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

    soup = BeautifulSoup(html, "html.parser")
    div = soup.find(id="main-col-body")               # first element with that id, or None
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

result = []
# for url in URLS:
#     result.append(fetch_text(url))

# for text in result:
#     print(len(text.split()), 'words')
#     print(text[:200])

print(chunk_words("w0 w1 w2 w3 w4 w5 w6 w7 w8 w9", size=4, overlap=1))