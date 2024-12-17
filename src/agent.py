import asyncio
import logging
from typing import Dict, List

# Core services
from communication.social.twitter import TwitterService
from blockchain.solana.wallet import SolanaWallet
from blockchain.ethereum.wallet import ZkWallet
from utils.config import Config
from utils.security import Security, SecurityError

# Existing imports
from models import Claude, Groq
from blockchain.solana import Trades, Tokens
from investment.portfolio import Allocation, RiskManagement
from investment.analysis import MarketAnalysis, SentimentAnalysis
from tokenomics.creation import TokenGenerator
from tokenomics.liquidity import PoolManagement
from dealflow.sourcing import ProjectScanner
from dealflow.evaluation import TeamAnalysis, TechAnalysis
from community.engagement import DiscordManager
from research.market_research import TrendAnalysis
from utils.logger import setup_logger

logger = logging.getLogger(__name__)


class AIVentureCapitalist:
    """
    Multi-chain AI Venture Capitalist agent with enhanced security and social features.
    """

    def __init__(self, config_path: str):
        # Load configuration
        self.config = Config(config_path)
        self.security = Security(self.config.security_settings)
        self.logger = setup_logger("ai_vc_agent")

        # Initialize core components
        self._initialize_wallets()
        self._initialize_core_components()
        self._initialize_investment_components()
        self._initialize_community_components()

        # State management
        self.active_investments: Dict = {}
        self.deal_pipeline: List = []
        self.performance_metrics: Dict = {}

    def _initialize_wallets(self):
        """Initialize multi-chain wallet infrastructure"""
        try:
            # Initialize wallet with security checks
            solana_config = self.security.decrypt_config(
                self.config.get("solana_wallet_config")
            )
            ethereum_config = self.security.decrypt_config(
                self.config.get("ethereum_wallet_config")
            )

            self.solana_wallet = SolanaWallet(
                config=solana_config, security_provider=self.security
            )

            self.zk_wallet = ZkWallet(
                config=ethereum_config, security_provider=self.security
            )

            self.logger.info("Multi-chain wallets initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize wallets: {e}")
            raise

    def _initialize_core_components(self):
        """Initialize core AI and blockchain components"""
        try:
            # AI Models
            self.claude = Claude(
                api_key=self.security.decrypt_key(self.config.get("claude_api_key"))
            )
            self.groq = Groq(
                api_key=self.security.decrypt_key(self.config.get("groq_api_key"))
            )

            # Trading and Tokens
            self.solana_trades = Trades(self.solana_wallet)
            self.tokens = Tokens()

            self.logger.info("Core components initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize core components: {e}")
            raise

    def _initialize_investment_components(self):
        """Initialize investment and analysis components"""
        try:
            # Portfolio Management
            self.portfolio = Allocation(self.config.get("portfolio_config"))
            self.risk_manager = RiskManagement(self.config.get("risk_config"))

            # Analysis
            self.market_analysis = MarketAnalysis()
            self.sentiment_analysis = SentimentAnalysis()

            # Deal Flow
            self.project_scanner = ProjectScanner()
            self.team_analyzer = TeamAnalysis()
            self.tech_analyzer = TechAnalysis()

            # Token Management
            self.token_generator = TokenGenerator()
            self.pool_manager = PoolManagement()

            self.logger.info("Investment components initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize investment components: {e}")
            raise

    def _initialize_community_components(self):
        """Initialize community and social components with enhanced security"""
        try:
            # Initialize Twitter service with security
            twitter_config = self.security.decrypt_config(
                self.config.get("twitter_config")
            )
            self.twitter_service = TwitterService(
                config=twitter_config, security_provider=self.security
            )

            # Initialize other community components
            self.discord_manager = DiscordManager(
                config=self.security.decrypt_config(self.config.get("discord_config"))
            )
            self.trend_analyzer = TrendAnalysis()

            self.logger.info("Community components initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize community components: {e}")
            raise

    async def execute_cross_chain_investment(self, decision: Dict):
        """Execute investment decisions across multiple chains"""
        try:
            chain = decision.get("chain", "solana")

            # Select appropriate wallet based on chain
            wallet = self.solana_wallet if chain == "solana" else self.zk_wallet

            # Verify transaction security
            if not self.security.verify_transaction(decision, wallet):
                raise SecurityError("Transaction failed security verification")

            if decision["action"] == "invest":
                tx_hash = await wallet.execute_investment(
                    token=decision["token"],
                    amount=decision["amount"],
                    strategy=decision["strategy"],
                )

                # Log transaction with security audit
                await self.security.audit_transaction(
                    tx_hash=tx_hash, wallet=wallet, action="invest", details=decision
                )

            elif decision["action"] == "exit":
                tx_hash = await wallet.execute_exit(
                    token=decision["token"], strategy=decision["strategy"]
                )

                await self.security.audit_transaction(
                    tx_hash=tx_hash, wallet=wallet, action="exit", details=decision
                )

            # Notify through social channels
            await self._notify_investment_action(decision)

        except Exception as e:
            self.logger.error(f"Failed to execute cross-chain investment: {e}")
            await self.security.log_security_event(
                event_type="investment_failure",
                details={"error": str(e), "decision": decision},
            )

    async def _analyze_market(self):
        """Analyze market conditions with security checks"""
        try:
            # Verify data sources
            if not self.security.verify_data_sources(
                [self.market_analysis, self.sentiment_analysis]
            ):
                raise SecurityError("Data source verification failed")

            market_data = await self.market_analysis.get_market_overview()
            sentiment_data = await self.sentiment_analysis.analyze_social_sentiment()

            # Analyze with security context
            with self.security.analysis_context() as context:
                investment_decision = await self.groq.analyze(
                    prompt="market_analysis",
                    data={
                        "market": market_data,
                        "sentiment": sentiment_data,
                        "current_portfolio": self.active_investments,
                        "security_context": context,
                    },
                )

            if investment_decision.get("action_required"):
                await self.execute_cross_chain_investment(investment_decision)

        except Exception as e:
            self.logger.error(f"Market analysis error: {e}")
            await self.security.handle_analysis_error(e)

    async def _notify_investment_action(self, decision: Dict):
        """Notify stakeholders through secure channels"""
        try:
            # Prepare secure notification
            notification = self.security.prepare_notification(decision)

            await asyncio.gather(
                self.twitter_service.post_update(notification),
                self.discord_manager.send_update(notification),
            )

            # Log social engagement
            await self.security.log_social_activity(
                {
                    "platform": ["twitter", "discord"],
                    "action": "investment_notification",
                    "details": notification,
                }
            )

        except Exception as e:
            self.logger.error(f"Failed to notify investment action: {e}")
            await self.security.handle_notification_error(e)

    async def run(self):
        """Main agent loop with security monitoring"""
        self.logger.info("Starting AI VC Agent")

        # Start security monitoring
        security_monitor = asyncio.create_task(
            self.security.monitor_agent_activity(self)
        )

        while True:
            try:
                await asyncio.gather(
                    self._analyze_market(),
                    self._manage_portfolio(),
                    self._scan_opportunities(),
                    self._manage_community(),
                    self._monitor_performance(),
                    security_monitor,  # Await security monitoring task
                )
                await asyncio.sleep(self.config.get("loop_interval", 60))
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                await self.security.handle_critical_error(e)
                await asyncio.sleep(10)


if __name__ == "__main__":
    config_path = "config/agent_config.yaml"
    agent = AIVentureCapitalist(config_path)

    asyncio.run(agent.run())
