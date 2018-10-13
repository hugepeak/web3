import sys
from web3 import Web3, HTTPProvider

# print usage
def print_usage():
    print("\nusage: python main.py contract_address",
          "--host https://mainnet.infura.io/<YOUR_API_KEY>\n")
    exit()

# check inputs
if len(sys.argv) != 4 \
        or sys.argv[1] == "-h" \
        or sys.argv[1] == "--help" \
        or sys.argv[2] != "--host":
    print_usage()

# get web3
web3 = Web3(HTTPProvider(sys.argv[3]))
if not web3.isConnected():
    print("Web3 is not connected, please check your connection.")
    exit()

# check and read in contract address
if web3.isAddress(sys.argv[1]):
    contract_address = web3.toChecksumAddress(sys.argv[1])
else:
    print("\nInvalid contract address!")
    print_usage()

# check if a block contains a contract address or not
def has_address(address, block_number):
    if web3.eth.getCode(address, block_number):
        return True
    else:
        return False

# binary search to find the first block that contains the contract.
# if a block contains a contract and the previous block doesn't, then
# this block is the one that the contract was deployed.
def binary_search(start, end, address):
    if start > end:
        return -1
    mid = int(start + (end - start) / 2)

    if has_address(address, mid):
        if not has_address(address, mid - 1):
            return mid
        else:
           return binary_search(start, mid - 1, address)
    else:
        return binary_search(mid + 1, end, address)
    

def main():

    # get the lastest block number
    latest = web3.eth.blockNumber

    # get the contract deployed block number
    if latest:
        block_number = binary_search(1, latest, contract_address)
    else:
       print("No valid blocks!\n")
       exit()

    # get the corresponding block hash
    if block_number:
        block_hash = web3.eth.getBlock(block_number).hash
    else:
        print("Contract not in blockchain!\n")
        exit()
    
    # get the count of transactions in the block
    transaction_count = web3.eth.getBlockTransactionCount(block_number)
    if not transaction_count:
        print("No valid transactions in the block!\n")
        exit()

    # loop over the transactions to find the corresponding one
    for i in range(transaction_count):
        
        # get the transaction by the index in the block
        transaction = web3.eth.getTransactionFromBlock(block_number, i)

        # get the transaction hash
        hash = transaction["hash"]

        # get the transaction receipt from hash to retrieve contract address
        transaction_receipt = web3.eth.waitForTransactionReceipt(hash)

        # compare address to location the corresponding transaction
        if transaction_receipt["contractAddress"] == contract_address:
            transaction_hash = transaction_receipt["transactionHash"]
            break

    if block_hash:
        print("\nBlock: ", block_hash.hex())
    else:
        print("\nNo block hash found!")
    if transaction_hash:
        print("Transaction: ", transaction_hash.hex())
    else:
        print("\nNo transaction hash available yet!")

if __name__ == "__main__":
    main()
