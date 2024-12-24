from web3 import Web3

rpc_url = "https://sepolia.drpc.org"  # Replace with your actual RPC URL

web3 = Web3(Web3.HTTPProvider(rpc_url))

if web3.is_connected():
    print(f"Connected to Ethereum node at {rpc_url}")
    print(f"Chain ID: {web3.eth.chain_id}")
else:
    print(f"Failed to connect to Ethereum node at {rpc_url}")