from dataclasses import dataclass
from typing import Dict


@dataclass
class DistributionConfig:
    vesting_schedules: Dict[str, Dict]
    allocations: Dict[str, float]
    lockup_periods: Dict[str, int]


class TokenDistributor:
    def __init__(self, token_address: str):
        self.token_address = token_address
        self.distributions = {}
        self.vesting_schedules = {}

    async def setup_distribution(self, config: DistributionConfig) -> Dict:
        try:
            # Create vesting contracts
            vesting_accounts = await self._create_vesting_accounts(
                config.vesting_schedules
            )

            # Set up initial allocations
            distribution_accounts = await self._setup_allocations(config.allocations)

            # Configure lockups
            await self._setup_lockups(distribution_accounts, config.lockup_periods)

            return {
                "vesting_accounts": vesting_accounts,
                "distribution_accounts": distribution_accounts,
            }
        except Exception as e:
            print(f"Error setting up distribution: {e}")
            raise

    async def execute_distribution(self, distribution_id: str) -> Dict:
        try:
            distribution = self.distributions[distribution_id]

            # Check vesting schedules
            releasable = await self._calculate_releasable_amounts(distribution)

            # Execute transfers
            tx_hashes = await self._execute_transfers(releasable)

            return {
                "distribution_id": distribution_id,
                "released_amounts": releasable,
                "transactions": tx_hashes,
            }
        except Exception as e:
            print(f"Error executing distribution: {e}")
            raise

    async def _create_vesting_accounts(
        self, schedules: Dict[str, Dict]
    ) -> Dict[str, str]:
        vesting_accounts = {}

        for recipient, schedule in schedules.items():
            account = await self._create_vesting_account(recipient, schedule)
            vesting_accounts[recipient] = account

        return vesting_accounts

    async def _setup_allocations(self, allocations: Dict[str, float]) -> Dict[str, str]:
        accounts = {}

        for recipient, amount in allocations.items():
            account = await self._create_token_account(recipient)
            await self._transfer_initial_allocation(account, amount)
            accounts[recipient] = account

        return accounts
