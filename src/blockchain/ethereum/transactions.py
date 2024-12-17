from datetime import time
from eth_account import Account
from web3 import Web3

# from zksync2.zksync_builder import ZkSyncBuilder
from typing import Dict, List, Optional, Union
import logging
from decimal import Decimal

# from zksync2.zksync_builder import ZkSyncBuilder
logger = logging.getLogger(__name__)


class ZkTransactions:
    def __init__(
        self, rpc_url: str, zksync_url: str, private_key: Optional[str] = None
    ):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        # self.zk_web3 = ZkSyncBuilder.build(zksync_url)
        self.account = Account.from_key(private_key) if private_key else None
        self.abis = self._load_abis()

    async def deposit_to_l2(
        self, amount: Union[int, float, Decimal], token_address: Optional[str] = None
    ) -> Dict[str, str]:
        """Deposit from L1 to L2"""
        try:
            if not self.account:
                raise ValueError("No account configured")

            # Handle ETH deposit
            if not token_address:
                deposit_tx = self.zk_web3.zksync.deposit_eth(
                    Web3.to_wei(amount, "ether")
                )
                return {
                    "transaction_hash": deposit_tx.hash.hex(),
                    "status": "pending",
                    "type": "eth_deposit",
                }

            # Handle token deposit
            token_contract = self.w3.eth.contract(
                address=token_address,
                abi=self.abis["usdc" if "USDC" in token_address.upper() else "weth"],
            )

            decimals = token_contract.functions.decimals().call()
            amount_wei = int(Decimal(amount) * Decimal(10**decimals))

            # Approve if needed
            allowance = token_contract.functions.allowance(
                self.account.address, self.zk_web3.zksync.main_contract.address
            ).call()

            if allowance < amount_wei:
                approve_tx = token_contract.functions.approve(
                    self.zk_web3.zksync.main_contract.address, amount_wei
                ).build_transaction(
                    {
                        "from": self.account.address,
                        "nonce": self.w3.eth.get_transaction_count(
                            self.account.address
                        ),
                    }
                )

                signed_approve = self.account.sign_transaction(approve_tx)
                self.w3.eth.send_raw_transaction(signed_approve.rawTransaction)

            # Deposit token
            deposit_tx = self.zk_web3.zksync.deposit_token(
                token_address, amount_wei, self.account.address
            )

            return {
                "transaction_hash": deposit_tx.hash.hex(),
                "status": "pending",
                "type": "token_deposit",
            }

        except Exception as e:
            logger.error(f"Error depositing to L2: {e}")
            raise

    async def swap_on_uniswap(
        self,
        token_in: str,
        token_out: str,
        amount_in: Union[int, float, Decimal],
        slippage: float = 0.005,  # 0.5%
    ) -> Dict[str, str]:
        """Swap tokens using Uniswap on zkSync"""
        try:
            if not self.account:
                raise ValueError("No account configured")

            router_contract = self.zk_web3.eth.contract(
                address=self.abis["uniswap_swap_router"]["address"],
                abi=self.abis["uniswap_swap_router"]["abi"],
            )

            # Get decimals
            token_in_contract = self.zk_web3.eth.contract(
                address=token_in,
                abi=self.abis["usdc" if "USDC" in token_in.upper() else "weth"],
            )
            decimals = token_in_contract.functions.decimals().call()
            amount_in_wei = int(Decimal(amount_in) * Decimal(10**decimals))

            # Get quote
            quote = router_contract.functions.getQuote(
                token_in, token_out, amount_in_wei
            ).call()

            min_amount_out = int(quote * (1 - slippage))

            # Build swap transaction
            swap_tx = router_contract.functions.swapExactTokensForTokens(
                amount_in_wei,
                min_amount_out,
                [token_in, token_out],
                self.account.address,
                int(time.time()) + 1800,  # 30 min deadline
            ).build_transaction(
                {
                    "from": self.account.address,
                    "nonce": self.zk_web3.eth.get_transaction_count(
                        self.account.address
                    ),
                }
            )

            # Sign and send
            signed_tx = self.account.sign_transaction(swap_tx)
            tx_hash = self.zk_web3.eth.send_raw_transaction(signed_tx.rawTransaction)

            return {
                "transaction_hash": tx_hash.hex(),
                "status": "pending",
                "type": "swap",
                "amount_in": str(amount_in),
                "expected_out": str(Decimal(quote) / Decimal(10**decimals)),
            }

        except Exception as e:
            logger.error(f"Error swapping on Uniswap: {e}")
            raise


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
        gas_price: Optional[int] = None,
    ) -> Dict[str, str]:
        """Send ETH transaction"""
        try:
            if not self.account:
                raise ValueError("No account configured")

            # Convert amount to Wei
            amount_wei = Web3.to_wei(amount, "ether")

            # Build transaction
            tx = {
                "nonce": self.w3.eth.get_transaction_count(self.account.address),
                "to": to_address,
                "value": amount_wei,
                "chainId": self.w3.eth.chain_id,
            }

            # Set gas parameters
            if gas_limit:
                tx["gas"] = gas_limit
            else:
                tx["gas"] = self.w3.eth.estimate_gas(tx)

            if gas_price:
                tx["gasPrice"] = gas_price
            else:
                tx["maxFeePerGas"] = (
                    self.w3.eth.max_priority_fee
                    + self.w3.eth.get_block("latest")["baseFeePerGas"]
                )
                tx["maxPriorityFeePerGas"] = self.w3.eth.max_priority_fee

            # Sign and send transaction
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            return {
                "transaction_hash": tx_hash.hex(),
                "from": self.account.address,
                "to": to_address,
                "amount": str(amount),
                "status": "pending",
            }

        except Exception as e:
            logger.error(f"Error sending ETH: {e}")
            raise

    async def send_token(
        self,
        token_address: str,
        to_address: str,
        amount: Union[int, float, Decimal],
        gas_limit: Optional[int] = None,
    ) -> Dict[str, str]:
        """Send ERC20 token transaction"""
        try:
            if not self.account:
                raise ValueError("No account configured")

            # Get token contract
            token_contract = self.w3.eth.contract(
                address=token_address, abi=self.get_token_abi()
            )

            # Get token decimals
            decimals = token_contract.functions.decimals().call()
            amount_wei = int(Decimal(amount) * Decimal(10**decimals))

            # Build transaction
            tx = token_contract.functions.transfer(
                to_address, amount_wei
            ).build_transaction(
                {
                    "from": self.account.address,
                    "nonce": self.w3.eth.get_transaction_count(self.account.address),
                    "maxFeePerGas": self.w3.eth.max_priority_fee
                    + self.w3.eth.get_block("latest")["baseFeePerGas"],
                    "maxPriorityFeePerGas": self.w3.eth.max_priority_fee,
                    "chainId": self.w3.eth.chain_id,
                }
            )

            if gas_limit:
                tx["gas"] = gas_limit
            else:
                tx["gas"] = self.w3.eth.estimate_gas(tx)

            # Sign and send transaction
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            return {
                "transaction_hash": tx_hash.hex(),
                "token_address": token_address,
                "from": self.account.address,
                "to": to_address,
                "amount": str(amount),
                "status": "pending",
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
                "transaction_hash": tx_hash,
                "status": "success" if tx_receipt["status"] == 1 else "failed",
                "block_number": tx_receipt["blockNumber"],
                "from": tx["from"],
                "to": tx["to"],
                "value": str(Web3.from_wei(tx["value"], "ether")),
                "gas_used": tx_receipt["gasUsed"],
                "gas_price": str(Web3.from_wei(tx["gasPrice"], "gwei")),
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
                    {"name": "amount", "type": "uint256"},
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function",
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function",
            },
        ]
