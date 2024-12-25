# src/blockchain/ethereum/wallet.py

import logging
from typing import Dict, Optional, Tuple
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import asyncio
from web3.types import Wei

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

        # Store initialization parameters
        self.rpc_url = rpc_url
        self.zksync_url = zksync_url
        self._private_key = None
        self._initialized = False
        
        # Initialize Web3
        try:
            self.web3 = Web3(Web3.HTTPProvider(rpc_url))
            self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        except Exception as e:
            logger.error(f"Failed to initialize Web3: {e}")
            raise
        
        # Initialize account
        try:
            if private_key:
                clean_key = self._format_private_key(private_key)
                self._private_key = clean_key
                self.account = Account.from_key(clean_key)
                self.address = self.account.address
                logger.info(f"Account initialized with address: {self.address}")
            else:
                logger.warning("No private key provided, creating new account")
                self.account = self.web3.eth.account.create()
                self.address = self.account.address
                self._private_key = self.account._private_key.hex()
        except Exception as e:
            logger.error(f"Error initializing account: {e}")
            raise

        # Initialize zksync if URL provided
        self.zksync_enabled = bool(zksync_url)
        if self.zksync_enabled:
            try:
                self.zksync_web3 = Web3(Web3.HTTPProvider(zksync_url))
            except Exception as e:
                logger.error(f"Failed to initialize zkSync: {e}")
                self.zksync_enabled = False
                
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

    async def _check_connection(self) -> Tuple[bool, Optional[int]]:
        """Check connection to Ethereum node and get chain ID"""
        try:
            connected = await self._loop.run_in_executor(
                None, 
                self.web3.is_connected
            )
            
            if connected:
                chain_id = await self._loop.run_in_executor(
                    None,
                    lambda: self.web3.eth.chain_id
                )
                logger.info(f"Connected to network with chain ID: {chain_id}")
                return True, chain_id
            else:
                logger.error("Failed to connect to Ethereum node")
                return False, None
                
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False, None

    async def _check_account(self) -> bool:
        """Verify account and get initial balance"""
        try:
            # Verify address format
            if not self.web3.is_address(self.address):
                logger.error(f"Invalid Ethereum address: {self.address}")
                return False

            # Get balance without requiring initialization
            balance_wei = await self._loop.run_in_executor(
                None,
                self.web3.eth.get_balance,
                self.address
            )
            
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            logger.info(f"Initial balance: {balance_eth} ETH")
            return True
            
        except Exception as e:
            logger.error(f"Account check failed: {e}")
            return False

    async def initialize(self) -> None:
        """Initialize the wallet"""
        try:
            # Check connection first
            connected, chain_id = await self._check_connection()
            if not connected:
                raise ConnectionError(f"Failed to connect to Ethereum node at {self.rpc_url}")

            # Verify account
            if not await self._check_account():
                raise ValueError("Failed to verify account")

            # Initialize zkSync if enabled
            if self.zksync_enabled:
                zk_connected = await self._loop.run_in_executor(
                    None,
                    self.zksync_web3.is_connected
                )
                if not zk_connected:
                    logger.warning("Failed to connect to zkSync node")
                    self.zksync_enabled = False

            self._initialized = True
            logger.info("Ethereum wallet initialized successfully")
            
        except Exception as e:
            self._initialized = False
            logger.error(f"Failed to initialize wallet: {e}")
            raise

    async def get_balance(self) -> float:
        """Get ETH balance for wallet address"""
        try:
            balance_wei = await self._loop.run_in_executor(
                None,
                self.web3.eth.get_balance,
                self.address
            )
            
            return float(self.web3.from_wei(balance_wei, 'ether'))
            
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            raise

    async def cleanup(self) -> None:
        """Cleanup wallet resources"""
        try:
            # Close web3 connections
            if hasattr(self.web3.provider, 'close'):
                await self._loop.run_in_executor(
                    None,
                    self.web3.provider.close
                )
            
            if self.zksync_enabled and hasattr(self.zksync_web3.provider, 'close'):
                await self._loop.run_in_executor(
                    None,
                    self.zksync_web3.provider.close
                )
                
            self._initialized = False
            logger.info("Ethereum wallet cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error cleaning up wallet: {e}")

# Example usage:
async def test_wallet():
    """Test wallet functionality"""
    try:
        # Initialize wallet
        wallet = EthereumWallet(
            rpc_url="https://sepolia.drpc.org",  # Goerli testnet
            private_key="0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"  # Example key
        )
        
        print(f"\nInitializing wallet...")
        await wallet.initialize()
        
        print(f"\nWallet address: {wallet.address}")
        
        balance = await wallet.get_balance()
        print(f"Balance: {balance} ETH")
        
        await wallet.cleanup()
        print("\nWallet cleaned up successfully")
        
    except Exception as e:
        print(f"\nTest failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_wallet())