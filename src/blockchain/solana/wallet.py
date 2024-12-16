# blockchain/solana/wallet.py

import token
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction

from solana_agentkit.utils.keypair import create_keypair, create_keypair_from_secret, keypair
from solana_agentkit.types.publickey import PublicKeyOrStr
from solana_agentkit.types.account import Account
from solana_agentkit.utils.send_tx import send_transaction
from solana_agentkit.constants.constants import USDC_MINT, WSOL_MINT
from solana_agentkit.tools import transfer, TransferParams
import base58
from typing import Dict, Optional, List, Union
from decimal import Decimal
import logging
import asyncio
import os
import json

logger = logging.getLogger(__name__)

class SolanaWallet:
    def __init__(
        self,
        rpc_url: str,
        keypair: Optional[keypair] = None,
        secret_key: Optional[str] = None,
        private_key: Optional[str] = None
    ):
        """Initialize Solana wallet
        
        Args:
            rpc_url: Solana RPC URL
            keypair: Optional existing Keypair
            secret_key: Optional secret key to generate Keypair
            private_key: Optional private key to generate Keypair
        """
        self.client = AsyncClient(rpc_url)
        
        if keypair:
            self.keypair = keypair
        elif secret_key:
            self.keypair = create_keypair_from_secret(secret_key)
        elif private_key:
            self.private_key = private_key
        else:
            self.keypair = create_keypair()
            
        self.pubkey = str(self.keypair.public_key)
        
    @staticmethod
    def generate_wallet() -> 'SolanaWallet':
        private_key = os.urandom(32).hex()
        return SolanaWallet(private_key=private_key)

    def save_to_file(self, filepath: str):
        with open(filepath, 'w') as file:
            json.dump({"private_key": self.private_key}, file)

    @staticmethod
    def load_from_file(filepath: str) -> 'SolanaWallet':
        with open(filepath, 'r') as file:
            data = json.load(file)
        return SolanaWallet(private_key=data['private_key'])

    async def get_balance(
        self,
        token_mint: Optional[str] = None,
        address: Optional[str] = None
    ) -> Decimal:
        """Get SOL or token balance
        
        Args:
            token_mint: Optional token mint address
            address: Optional address to check (defaults to wallet address)
        
        Returns:
            Balance as Decimal
        """
        try:
            address = address or self.pubkey
            
            if not token_mint:
                # Get SOL balance
                balance = await self.client.get_balance(address)
                return Decimal(balance.value) / Decimal(1e9)
            
            # Get token balance
            token_accounts = await self.client.get_token_accounts_by_owner(
                owner=address,
                opts={
                    "mint": token_mint,
                    "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
                }
            )
            
            if not token_accounts.value:
                return Decimal(0)
                
            balance = int(token_accounts.value[0].account.data["parsed"]["info"]["tokenAmount"]["amount"])
            decimals = int(token_accounts.value[0].account.data["parsed"]["info"]["tokenAmount"]["decimals"])
            
            return Decimal(balance) / Decimal(10 ** decimals)
            
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            raise
            
    async def get_all_balances(self) -> Dict[str, Decimal]:
        """Get all token balances including SOL
        
        Returns:
            Dict mapping token symbol to balance
        """
        try:
            balances = {
                "SOL": await self.get_balance()
            }
            
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
        token_mint: Optional[str] = None
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
                    lamports=amount_lamports
                )
                
                transaction = Transaction().add(
                    transfer(transfer_params)
                )
                
            else:
                # Token transfer
                token_account = await self._get_or_create_token_account(
                    token_mint,
                    to_address
                )
                
                decimals = await self._get_token_decimals(token_mint)
                amount_raw = int(Decimal(amount) * Decimal(10 ** decimals))
                
                transaction = Transaction().add(
                    token.transfer(
                        self.keypair.public_key,
                        token_account,
                        amount_raw,
                        [self.keypair]
                    )
                )
                
            # Send transaction
            signature = await send_transaction(
                self.client,
                transaction,
                self.keypair
            )
            
            return signature
            
        except Exception as e:
            logger.error(f"Error transferring: {e}")
            raise
            
    async def _get_or_create_token_account(
        self,
        token_mint: str,
        owner: str
    ) -> str:
        """Get existing token account or create new one"""
        token_accounts = await self.client.get_token_accounts_by_owner(
            owner=owner,
            opts={
                "mint": token_mint,
                "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
            }
        )
        
        if token_accounts.value:
            return token_accounts.value[0].pubkey
            
        # Create new account
        account = await self._create_token_account(token_mint, owner)
        return account
        
    async def _create_token_account(
        self,
        token_mint: str,
        owner: str
    ) -> str:
        """Create new token account"""
        # Implementation depends on token program being used
        # This is a simplified version
        raise NotImplementedError()
        
    async def _get_token_decimals(self, token_mint: str) -> int:
        """Get token decimals"""
        mint_account = await self.client.get_account_info(token_mint)
        return mint_account.value.data["parsed"]["info"]["decimals"]
        
    def get_public_key(self) -> str:
        """Get wallet public key"""
        return self.pubkey