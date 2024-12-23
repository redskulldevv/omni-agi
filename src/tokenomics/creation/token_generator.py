from dataclasses import dataclass
from typing import Dict, List
from solana.rpc.api import Client
from solana.transaction import Transaction
from spl.token.instructions import create_mint, initialize_mint


@dataclass
class TokenConfig:
    name: str
    symbol: str
    decimals: int
    initial_supply: int
    max_supply: int
    features: Dict[str, bool]


class TokenGenerator:
    def __init__(self, rpc_url: str):
        self.client = Client(rpc_url)
        self.mints = {}

    async def create_token(self, config: TokenConfig) -> str:
        try:
            # Create mint account
            mint_keypair = await self._create_mint_account()

            # Initialize mint with config
            await self._initialize_mint(
                mint_keypair,
                config.decimals,
                config.features.get("freeze_authority", True),
            )

            # Set up initial supply
            await self._mint_initial_supply(mint_keypair, config.initial_supply)

            return mint_keypair.public_key.to_string()
        except Exception as e:
            print(f"Error creating token: {e}")
            raise
