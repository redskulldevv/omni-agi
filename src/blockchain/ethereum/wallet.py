from web3 import Web3
from eth_account import Account
import json
from typing import Dict, Optional, List
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class EthereumWallet:
    def __init__(self, rpc_url: str, private_key: Optional[str] = None):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(private_key) if private_key else None
        
    async def create_wallet(self) -> Dict[str, str]:
        """Create new Ethereum wallet"""
        try:
            account = Account.create()
            return {
                'address': account.address,
                'private_key': account.key.hex(),
                'message': 'Store private key securely!'
            }
        except Exception as e:
            logger.error(f"Error creating wallet: {e}")
            raise
            
    async def get_balance(self, address: Optional[str] = None) -> Dict[str, Decimal]:
        """Get ETH and token balances"""
        try:
            address = address or self.account.address
            eth_balance = self.w3.eth.get_balance(address)
            
            balances = {
                'ETH': Web3.from_wei(eth_balance, 'ether')
            }
            
            # Add common token balances
            tokens = {
                'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
                'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7'
            }
            
            for symbol, contract_address in tokens.items():
                try:
                    token_contract = self.w3.eth.contract(
                        address=contract_address,
                        abi=self.get_erc20_abi()
                    )
                    decimals = token_contract.functions.decimals().call()
                    balance = token_contract.functions.balanceOf(address).call()
                    balances[symbol] = Decimal(balance) / Decimal(10 ** decimals)
                except Exception as e:
                    logger.warning(f"Error getting {symbol} balance: {e}")
                    
            return balances
            
        except Exception as e:
            logger.error(f"Error getting balances: {e}")
            raise
            
    def get_erc20_abi(self) -> List:
        """Return basic ERC20 ABI"""
        return [
            {
                "constant": True,
                "inputs": [{"name": "owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]