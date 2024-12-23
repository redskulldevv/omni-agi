# blockchain/solana/wallet.py

import token
from typing import Dict, Optional, Union
import base58
from solana.rpc.async_api import AsyncClient, Commitment
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana import Keypair
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import logging
import os
import json
from decimal import Decimal

from solana_agentkit.utils.keypair import (
    create_keypair,
    create_keypair_from_secret,
    keypair,
)
from solana_agentkit.utils.send_tx import send_transaction
from solana_agentkit.constants.constants import USDC_MINT, WSOL_MINT
from solana_agentkit.tools import transfer, TransferParams

logger = logging.getLogger(__name__)


class SolanaWallet:
    def __init__(self, rpc_url: str, private_key: Optional[str] = None):
        self.client = Client(rpc_url)
        self.keypair = self._initialize_keypair(private_key)

    def _initialize_keypair(self, private_key: Optional[str] = None) -> Keypair:
        """Initialize Solana keypair"""
        try:
            if private_key:
                # Use existing private key
                secret_key = base58.b58decode(private_key)
                return Keypair.from_secret_key(secret_key)
            else:
                # Generate new keypair
                return Keypair()
        except Exception as e:
            logger.error(f"Failed to initialize keypair: {e}")
            raise

    @staticmethod
    def generate_wallet() -> "SolanaWallet":
        private_key = os.urandom(32).hex()
        return SolanaWallet(private_key=private_key)

    def save_to_file(self, filepath: str):
        with open(filepath, "w") as file:
            json.dump({"private_key": self.private_key}, file)

    @staticmethod
    def load_from_file(filepath: str) -> "SolanaWallet":
        with open(filepath, "r") as file:
            data = json.load(file)
        return SolanaWallet(private_key=data["private_key"])

    async def get_balance(self) -> float:
        """Get wallet SOL balance"""
        try:
            response = await self.client.get_balance(
                self.keypair.public_key, commitment=Commitment("confirmed")
            )
            return response["result"]["value"] / 1e9  # Convert lamports to SOL
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            raise

    async def get_token_balance(self, token_address: str) -> Dict:
        """Get specific token balance"""
        try:
            # Implement token balance check
            pass
        except Exception as e:
            logger.error(f"Failed to get token balance: {e}")
            raise

    async def execute_transaction(self, transaction: Transaction) -> str:
        """Execute a Solana transaction"""
        try:
            # Sign transaction
            transaction.sign(self.keypair)

            # Send transaction
            response = await self.client.send_transaction(
                transaction, self.keypair, opts={"skip_preflight": True}
            )

            return response["result"]
        except Exception as e:
            logger.error(f"Failed to execute transaction: {e}")
            raise

    async def execute_trade(self, params: Dict) -> Dict:
        """Execute a trade with given parameters"""
        try:
            # Build transaction based on params
            transaction = Transaction()

            # Execute transaction
            tx_hash = await self.execute_transaction(transaction)

            return {"success": True, "tx_hash": tx_hash, "params": params}
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")
            return {"success": False, "error": str(e), "params": params}

    async def get_all_balances(self) -> Dict[str, Decimal]:
        """Get all token balances including SOL

        Returns:
            Dict mapping token symbol to balance
        """
        try:
            balances = {"SOL": await self.get_balance()}

            # Get USDC balance
            balances["USDC"] = await self.get_balance(USDC_MINT)

            # Get wSOL balance
            balances["wSOL"] = await self.get_balance(WSOL_MINT)

            return balances

        except Exception as e:
            logger.error(f"Error getting all balances: {e}")
            raise

    async def transfer(
        self,
        to_address: str,
        amount: Union[int, float, Decimal],
        token_mint: Optional[str] = None,
    ) -> str:
        """Transfer SOL or tokens

        Args:
            to_address: Recipient address
            amount: Amount to transfer
            token_mint: Optional token mint (if None, transfers SOL)

        Returns:
            Transaction signature
        """
        try:
            # Convert amount to proper integer value
            if not token_mint:
                # SOL transfer
                amount_lamports = int(Decimal(amount) * Decimal(1e9))

                transfer_params = TransferParams(
                    from_pubkey=self.keypair.public_key,
                    to_pubkey=to_address,
                    lamports=amount_lamports,
                )

                transaction = Transaction().add(transfer(transfer_params))

            else:
                # Token transfer
                token_account = await self._get_or_create_token_account(
                    token_mint, to_address
                )

                decimals = await self._get_token_decimals(token_mint)
                amount_raw = int(Decimal(amount) * Decimal(10**decimals))

                transaction = Transaction().add(
                    token.transfer(
                        self.keypair.public_key,
                        token_account,
                        amount_raw,
                        [self.keypair],
                    )
                )

            # Send transaction
            signature = await send_transaction(self.client, transaction, self.keypair)

            return signature

        except Exception as e:
            logger.error(f"Error transferring: {e}")
            raise

    async def _get_or_create_token_account(self, token_mint: str, owner: str) -> str:
        """Get existing token account or create new one"""
        token_accounts = await self.client.get_token_accounts_by_owner(
            owner=owner,
            opts={
                "mint": token_mint,
                "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
            },
        )

        if token_accounts.value:
            return token_accounts.value[0].pubkey

        # Create new account
        account = await self._create_token_account(token_mint, owner)
        return account

    async def _create_token_account(self, token_mint: str, owner: str) -> str:
        """Create new token account"""
        # Implementation depends on token program being used
        # This is a simplified version
        raise NotImplementedError()

    async def _get_token_decimals(self, token_mint: str) -> int:
        """Get token decimals"""
        mint_account = await self.client.get_account_info(token_mint)
        return mint_account.value.data["parsed"]["info"]["decimals"]

    @property
    def public_key(self) -> str:
        """Get wallet public key"""
        return str(self.keypair.public_key)
