# src/blockchain/ethereum/wallet.py

import logging
from typing import Dict, Optional
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import asyncio

logger = logging.getLogger(__name__)

class EthereumWallet:
    def __init__(
        self,
        rpc_url: str,
        private_key: Optional[str] = None,
        zksync_url: Optional[str] = None,
    ):
        if not rpc_url:
            raise ValueError("RPC URL is required")
            
        # Initialize Web3
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Initialize account
        if private_key:
            try:
                # Format private key correctly
                clean_key = self._format_private_key(private_key)
                self.account = Account.from_key(clean_key)
                self.address = self.account.address
                logger.info(f"Account initialized with address: {self.address}")
            except Exception as e:
                logger.error(f"Error initializing account: {e}")
                raise
        else:
            logger.warning("No private key provided, creating new account")
            self.account = self.web3.eth.account.create()
            self.address = self.account.address
        
        # Initialize zksync if URL provided
        self.zksync_enabled = bool(zksync_url)
        if self.zksync_enabled:
            self.zksync_web3 = Web3(Web3.HTTPProvider(zksync_url))
            
        self._initialized = False
        self._loop = asyncio.get_event_loop()

    def _format_private_key(self, key: str) -> str:
        """Format private key to correct format"""
        try:
            # Remove '0x' prefix if present
            clean_key = key.lower().strip()
            if clean_key.startswith('0x'):
                clean_key = clean_key[2:]
                
            # Ensure key is 64 characters (32 bytes) of hex
            if len(clean_key) != 64:
                raise ValueError("Private key must be 32 bytes")
                
            # Verify it's valid hex
            try:
                int(clean_key, 16)
            except ValueError:
                raise ValueError("Private key must be hexadecimal")
                
            return f"0x{clean_key}"
            
        except Exception as e:
            logger.error(f"Error formatting private key: {e}")
            raise ValueError(f"Invalid private key format: {str(e)}")

    async def initialize(self) -> None:
        """Initialize the wallet and verify connection"""
        try:
            # Check connection
            if not await self._check_connection():
                raise ConnectionError("Failed to connect to Ethereum node")
                
            # Verify account
            if not self.web3.is_address(self.address):
                raise ValueError(f"Invalid Ethereum address: {self.address}")
                
            # Check balance to verify account access
            balance = await self.get_balance()
            logger.info(f"Account balance: {balance} ETH")
                
            self._initialized = True
            logger.info(f"Ethereum wallet initialized for address: {self.address}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Ethereum wallet: {e}")
            raise

    async def _check_connection(self) -> bool:
        """Check connection to Ethereum node"""
        try:
            logger.info(f"Checking connection to Ethereum node at {self.web3.provider.endpoint_uri}")
            connected = await self._loop.run_in_executor(
                None, 
                self.web3.is_connected
            )
            if connected:
                # Get network info
                network_chain_id = await self._loop.run_in_executor(
                    None,
                    lambda: self.web3.eth.chain_id
                )
                logger.info(f"Connected to network with chain ID: {network_chain_id}")
            else:
                logger.error("Failed to connect to Ethereum node")
            return connected
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False

    async def get_balance(self) -> float:
        """Get ETH balance for wallet address"""
        if not self._initialized:
            raise RuntimeError("Wallet not initialized")
            
        try:
            balance_wei = await self._loop.run_in_executor(
                None,
                self.web3.eth.get_balance,
                self.address
            )
            
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
            
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            raise

    async def get_l2_balance(self, address: str) -> float:
        """Get L2 balance"""
        try:
            if not self._initialized:
                raise RuntimeError("Wallet not initialized")

            balance = self.zksync_web3.eth.get_balance(address)
            return Web3.from_wei(balance, "ether")
        except Exception as e:
            logger.error(f"Error getting L2 balance: {e}")
            return 0.0

    async def execute_trade(self, trade_params: Dict) -> Dict:
        """Execute a trade"""
        try:
            # Implement trade execution logic
            pass
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            raise

    async def cleanup(self) -> None:
        """Cleanup wallet resources"""
        try:
            self._initialized = False
            logger.info("Ethereum wallet cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up wallet: {e}")

# Example usage:
async def test_wallet():
    try:
        # Test with various key formats
        test_cases = [
            "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            None  # Should create new wallet
        ]
        
        for key in test_cases:
            print(f"\nTesting with key: {key}")
            try:
                wallet = EthereumWallet(
                    rpc_url="https://sepolia.drpc.org",
                    private_key=key
                )
                await wallet.initialize()
                print(f"Created wallet with address: {wallet.address}")
            except Exception as e:
                print(f"Failed to create wallet: {e}")
                
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_wallet())