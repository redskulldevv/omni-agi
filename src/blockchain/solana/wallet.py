from typing import Dict, Optional, Union
from solders.keypair import Keypair # type: ignore
from solders.pubkey import Pubkey # type: ignore
from solders.system_program import transfer, TransferParams
from solders.transaction import Transaction # type: ignore
from solana.rpc.types import TxOpts
from solana.rpc.async_api import AsyncClient
import base58
import logging
import os
import json
from solana.rpc.commitment import Commitment
from decimal import Decimal

# Additional imports
from solders.hash import Hash # type: ignore
from solders.message import MessageV0 # type: ignore
from solders.transaction import VersionedTransaction # type: ignore

# Define constants
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # Solana USDC mint
WSOL_MINT = "So11111111111111111111111111111111111111112"   # Wrapped SOL mint
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"

logger = logging.getLogger(__name__)

class SolanaWallet:
    def __init__(self, 
                 rpc_url: str,
                 keypair: Optional[Keypair] = None,
                 commitment: Commitment = Commitment("confirmed")):
        self.client = AsyncClient(rpc_url, commitment)
        self.keypair = keypair or Keypair()
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize the wallet and verify connection"""
        try:
            # Test connection
            await self.client.is_connected()
            # Get initial balance
            await self.get_balance()
            self._initialized = True
        except Exception as e:
            print(f"Failed to initialize SolanaWallet: {str(e)}")
            raise
    def _initialize_keypair(self, private_key: Optional[str] = None) -> Keypair:
        """Initialize Solana keypair"""
        try:
            if (private_key):
                # Use existing private key
                secret_key = base58.b58decode(private_key)
                return Keypair.from_bytes(secret_key)
            else:
                # Generate new keypair
                return Keypair()
        except Exception as e:
            logger.error(f"Failed to initialize keypair: {e}")
            raise

    @staticmethod
    def generate_wallet() -> "SolanaWallet":
        """Generate a new wallet"""
        private_key = os.urandom(32).hex()
        return SolanaWallet(private_key=private_key)

    def save_to_file(self, filepath: str):
        """Save wallet to file"""
        with open(filepath, "w") as file:
            json.dump({"private_key": self.private_key}, file)

    @staticmethod
    def load_from_file(filepath: str) -> "SolanaWallet":
        """Load wallet from file"""
        with open(filepath, "r") as file:
            data = json.load(file)
        return SolanaWallet(private_key=data["private_key"])

    async def get_balance(self, token_mint: Optional[str] = None) -> float:
        """Get wallet SOL balance or token balance"""
        try:
            if not token_mint:
                # Get SOL balance
                response = await self.client.get_balance(self.keypair.pubkey())
                return float(response.value) / 1e9  # Convert lamports to SOL
            else:
                # Get token balance
                token_account = await self._get_or_create_token_account(
                    token_mint, str(self.keypair.pubkey())
                )
                response = await self.client.get_token_account_balance(token_account)
                return float(response.value.amount) / (10 ** response.value.decimals)
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            raise

    async def get_all_balances(self) -> Dict[str, Decimal]:
        """Get all token balances including SOL"""
        try:
            balances = {"SOL": Decimal(str(await self.get_balance()))}

            # Get USDC balance
            balances["USDC"] = Decimal(str(await self.get_balance(USDC_MINT)))

            # Get wSOL balance
            balances["wSOL"] = Decimal(str(await self.get_balance(WSOL_MINT)))

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
        """Transfer SOL or tokens"""
        try:
            # Convert amount to proper integer value
            if not token_mint:
                # SOL transfer
                amount_lamports = int(Decimal(str(amount)) * Decimal(1e9))
                
                transfer_params = TransferParams(
                    from_pubkey=self.keypair.pubkey(),
                    to_pubkey=Pubkey.from_string(to_address),
                    lamports=amount_lamports
                )
                
                transaction = Transaction().add(transfer(transfer_params))

            else:
                # Token transfer implementation would go here
                # This requires additional SPL token program integration
                raise NotImplementedError("Token transfers not yet implemented")

            # Send transaction
            opts = TxOpts(skip_preflight=True)
            signature = await self.client.send_transaction(
                transaction, self.keypair, opts=opts
            )
            
            return str(signature)

        except Exception as e:
            logger.error(f"Error transferring: {e}")
            raise

    async def _get_or_create_token_account(self, token_mint: str, owner: str) -> str:
        """Get existing token account or create new one"""
        try:
            token_accounts = await self.client.get_token_accounts_by_owner(
                Pubkey.from_string(owner),
                {"mint": token_mint, "programId": TOKEN_PROGRAM_ID},
            )
            
            if token_accounts.value:
                return str(token_accounts.value[0].pubkey)
                
            # Create new account if none exists
            # This would require implementing token account creation
            raise NotImplementedError("Token account creation not yet implemented")
            
        except Exception as e:
            logger.error(f"Error with token account: {e}")
            raise

    @property
    def public_key(self) -> str:
        """Get wallet public key"""
        return str(self.keypair.pubkey())

    async def close(self):
        await self.client.close()

# Example usage of solders library
sender = Keypair()  # let's pretend this account actually has SOL to send
receiver = Keypair()
ix = transfer(
    TransferParams(
        from_pubkey=sender.pubkey(), to_pubkey=receiver.pubkey(), lamports=1_000_000
    )
)
blockhash = Hash.default()  # replace with a real blockhash using get_latest_blockhash
msg = MessageV0.try_compile(
    payer=sender.pubkey(),
    instructions=[ix],
    address_lookup_table_accounts=[],
    recent_blockhash=blockhash,
)
tx = VersionedTransaction(msg, [sender])