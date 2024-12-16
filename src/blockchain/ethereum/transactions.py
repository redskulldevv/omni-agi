from web3 import Web3
from eth_account.messages import encode_defunct
from typing import Dict, List, Optional, Union
import logging
import json
from decimal import Decimal

logger = logging.getLogger(__name__)

class EthereumTransactions:
    def __init__(self, rpc_url: str, private_key: Optional[str] = None):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = None
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key)
            
    async def send_eth(
        self,
        to_address: str,
        amount: Union[int, float, Decimal],
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None
    ) -> Dict[str, str]:
        """Send ETH transaction"""
        try:
            if not self.account:
                raise ValueError("No account configured")
                
            # Convert amount to Wei
            amount_wei = Web3.to_wei(amount, 'ether')
            
            # Build transaction
            tx = {
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'to': to_address,
                'value': amount_wei,
                'chainId': self.w3.eth.chain_id
            }
            
            # Set gas parameters
            if gas_limit:
                tx['gas'] = gas_limit
            else:
                tx['gas'] = self.w3.eth.estimate_gas(tx)
                
            if gas_price:
                tx['gasPrice'] = gas_price
            else:
                tx['maxFeePerGas'] = self.w3.eth.max_priority_fee + self.w3.eth.get_block('latest')['baseFeePerGas']
                tx['maxPriorityFeePerGas'] = self.w3.eth.max_priority_fee
                
            # Sign and send transaction
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return {
                'transaction_hash': tx_hash.hex(),
                'from': self.account.address,
                'to': to_address,
                'amount': str(amount),
                'status': 'pending'
            }
            
        except Exception as e:
            logger.error(f"Error sending ETH: {e}")
            raise
            
    async def send_token(
        self,
        token_address: str,
        to_address: str,
        amount: Union[int, float, Decimal],
        gas_limit: Optional[int] = None
    ) -> Dict[str, str]:
        """Send ERC20 token transaction"""
        try:
            if not self.account:
                raise ValueError("No account configured")
                
            # Get token contract
            token_contract = self.w3.eth.contract(
                address=token_address,
                abi=self.get_token_abi()
            )
            
            # Get token decimals
            decimals = token_contract.functions.decimals().call()
            amount_wei = int(Decimal(amount) * Decimal(10 ** decimals))
            
            # Build transaction
            tx = token_contract.functions.transfer(
                to_address,
                amount_wei
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'maxFeePerGas': self.w3.eth.max_priority_fee + self.w3.eth.get_block('latest')['baseFeePerGas'],
                'maxPriorityFeePerGas': self.w3.eth.max_priority_fee,
                'chainId': self.w3.eth.chain_id
            })
            
            if gas_limit:
                tx['gas'] = gas_limit
            else:
                tx['gas'] = self.w3.eth.estimate_gas(tx)
                
            # Sign and send transaction
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return {
                'transaction_hash': tx_hash.hex(),
                'token_address': token_address,
                'from': self.account.address,
                'to': to_address,
                'amount': str(amount),
                'status': 'pending'
            }
            
        except Exception as e:
            logger.error(f"Error sending token: {e}")
            raise
            
    async def get_transaction_status(self, tx_hash: str) -> Dict[str, str]:
        """Get transaction status and details"""
        try:
            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            tx = self.w3.eth.get_transaction(tx_hash)
            
            return {
                'transaction_hash': tx_hash,
                'status': 'success' if tx_receipt['status'] == 1 else 'failed',
                'block_number': tx_receipt['blockNumber'],
                'from': tx['from'],
                'to': tx['to'],
                'value': str(Web3.from_wei(tx['value'], 'ether')),
                'gas_used': tx_receipt['gasUsed'],
                'gas_price': str(Web3.from_wei(tx['gasPrice'], 'gwei'))
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction status: {e}")
            raise
            
    def get_token_abi(self) -> List:
        """Return basic ERC20 transfer ABI"""
        return [
            {
                "constant": False,
                "inputs": [
                    {"name": "recipient", "type": "address"},
                    {"name": "amount", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
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