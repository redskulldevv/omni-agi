from web3 import Web3
from eth_account import Account
import json
import os
from typing import Dict, Optional
from decimal import Decimal
import logging
from zksync2.module.module_builder import ZkSyncBuilder

logger = logging.getLogger(__name__)


class ZkWallet:
    def __init__(
        self, rpc_url: str, zksync_url: str, private_key: Optional[str] = None
    ):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.zk_web3 = ZkSyncBuilder.build(zksync_url)
        self.account = Account.from_key(private_key) if private_key else None
        self.abis = self._load_abis()

    def _load_abis(self) -> Dict:
        """Load all ABIs from the abis folder"""
        abis = {}
        abis_path = os.path.join(os.path.dirname(__file__), "abis")

        for filename in os.listdir(abis_path):
            if filename.endswith(".json"):
                with open(os.path.join(abis_path, filename), "r") as f:
                    abis[filename[:-5]] = json.load(f)

        return abis

    async def get_l2_balance(
        self, token_address: Optional[str] = None, address: Optional[str] = None
    ) -> Decimal:
        """Get balance on zkSync"""
        try:
            address = address or self.account.address

            if token_address:
                token_contract = self.zk_web3.eth.contract(
                    address=token_address,
                    abi=self.abis[
                        "usdc" if "USDC" in token_address.upper() else "weth"
                    ],
                )
                balance = token_contract.functions.balanceOf(address).call()
                decimals = token_contract.functions.decimals().call()
                return Decimal(balance) / Decimal(10**decimals)
            else:
                balance = self.zk_web3.eth.get_balance(address)
                return Web3.from_wei(balance, "ether")

        except Exception as e:
            logger.error(f"Error getting L2 balance: {e}")
            raise
