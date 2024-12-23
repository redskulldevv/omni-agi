from dataclasses import dataclass
from typing import Dict, List, Optional
from decimal import Decimal
import pandas as pd

@dataclass
class DistributionConfig:
    treasury_share: float
    staking_share: float
    team_share: float
    community_share: float
    distribution_interval: int

class RevenueDistributor:
    def __init__(self, config: DistributionConfig):
        self.config = config
        self.pending_distributions = {}
        self.distribution_history = pd.DataFrame()

    async def distribute_revenue(self, revenue: Dict) -> Dict:
        """Distribute collected revenue according to configuration"""
        try:
            distribution = self._calculate_distribution(revenue["total"])
            
            # Process distributions to different stakeholders
            tx_hashes = await self._process_distributions(distribution)
            
            await self._update_distribution_history(distribution, tx_hashes)
            
            return {
                "distribution": distribution,
                "transactions": tx_hashes,
                "timestamp": pd.Timestamp.now()
            }
        except Exception as e:
            print(f"Error distributing revenue: {e}")
            raise

    def _calculate_distribution(self, total_amount: float) -> Dict:
        """Calculate distribution amounts for each stakeholder"""
        return {
            "treasury": total_amount * self.config.treasury_share,
            "staking": total_amount * self.config.staking_share,
            "team": total_amount * self.config.team_share,
            "community": total_amount * self.config.community_share
        }

    async def process_staking_rewards(self) -> Dict:
        """Process and distribute staking rewards"""
        try:
            pending_rewards = await self._get_pending_staking_rewards()
            
            # Calculate rewards for each staker
            distributions = self._calculate_staking_distributions(
                pending_rewards["total"]
            )
            
            # Process distributions
            tx_hashes = await self._distribute_staking_rewards(distributions)
            
            return {
                "total_distributed": pending_rewards["total"],
                "distributions": distributions,
                "transactions": tx_hashes
            }
        except Exception as e:
            print(f"Error processing staking rewards: {e}")
            raise

    async def get_distribution_metrics(self) -> Dict:
        """Get metrics about revenue distribution"""
        return {
            "total_distributed": self._calculate_total_distributed(),
            "distribution_by_type": self._group_distributions(),
            "staking_metrics": await self._get_staking_metrics(),
            "treasury_metrics": await self._get_treasury_metrics()
        }

    async def _distribute_staking_rewards(self, distributions: Dict) -> List[str]:
        """Process the actual distribution of staking rewards"""
        tx_hashes = []
        for address, amount in distributions.items():
            try:
                tx_hash = await self._send_reward(address, amount)
                tx_hashes.append(tx_hash)
            except Exception as e:
                print(f"Error distributing to {address}: {e}")
                continue
        return tx_hashes