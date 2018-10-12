from bs4 import BeautifulSoup
import requests
import re
import sys

url_prefix = "https://etherscan.io"

address = sys.argv[1]

contractAddress = "/address/" + address
url = url_prefix + contractAddress

page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
link = soup.find(title = "Creator TxHash")
tx_hash = link.string
url = url_prefix + "/tx/" + tx_hash

page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
link = soup.find(title = "Number of Blocks Mined Since")
blockNumber = link.parent.a.string
url = url_prefix + "/block/" + blockNumber

page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
links = soup.find_all(class_=re.compile("col-sm-3 hidden2-su-xs"))
for link in links:
    if link.string == "Hash:":
        block_hash = link.next_sibling.next_sibling.string
        break

print("Block: ", block_hash)
print("Transaction: ", tx_hash)
