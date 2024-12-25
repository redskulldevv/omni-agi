# test_rpc_connection.py
from web3 import Web3
import asyncio
from blockchain.ethereum.wallet import EthereumWallet

async def main():
    wallet = EthereumWallet(
        rpc_url="https://sepolia.drpc.org",
        private_key="your-private-key"  # Optional
    )
    
    try:
        await wallet.initialize()
        balance = await wallet.get_balance()
        print(f"Balance: {balance} ETH")
    finally:
        await wallet.cleanup()

if __name__ == "__main__":
    asyncio.run(main())