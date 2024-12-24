import asyncio
from dataclasses import dataclass
import os
from typing import Dict, Optional
from typing import Dict
import asyncio

from dotenv import load_dotenv
from blockchain.solana.wallet import SolanaWallet

# Core services
from blockchain.solana.wallet import SolanaWallet
from utils.security import SecurityError

# Existing imports
from models import ClaudeAI, GroqAI

"""
Core Agent Implementation
Integrates all components and provides main agent functionality.
"""

import asyncio
from typing import Dict
import yaml
import logging

# AI Models

# Blockchain
from blockchain.solana.wallet import SolanaWallet
from blockchain.ethereum.wallet import EthereumWallet

# Cognition
from cognition.memory import MemoryManager
from cognition.reasoning import ReasoningEngine
from cognition.context import ContextManager
from cognition.goals import GoalManager
from cognition.learning import LearningManager

# Communication

# Community

# Investment
from investment.analysis.market_analysis import MarketAnalyzer
from investment.analysis.sentiment_analysis import SentimentAnalyzer

# Research

# Tokenomics

# Utils

# Part 1: Core Agent Implementation
import asyncio
import logging
from typing import Dict
import yaml

# Keep existing imports, add only new ones
from models import ClaudeAI, GroqAI
from utils.security import SecurityError


@dataclass
class AgentConfig:
    def __init__(self, 
                 name: str, 
                 personality_path: str, 
                 settings_path: str):
        self.name = name
        self.personality_path = personality_path
        self.settings_path = settings_path

class Agent:
    def __init__(self, config: AgentConfig, api_keys: Dict[str, str]):
        self.config = config
        self.api_keys = api_keys
        self.logger = logging.getLogger(self.config.name)
        
        # Load configurations
        self.settings = self._load_settings()
        self.personality = self._load_personality()
        
        # Initialize all components
        self.memory = MemoryManager()
        self.reasoning = ReasoningEngine()
        self.context = ContextManager()
        self.goals = GoalManager()
        self.learning = LearningManager()
        
        # Market Analysis
        market_data_sources = self.settings.get("market_analysis", {}).get("data_sources", {})
        self.market_analyzer = MarketAnalyzer(data_sources=market_data_sources)
        self.sentiment_analyzer = SentimentAnalyzer(data_sources={"social": "twitter"})  # Changed here

        # Initialize wallets
        self.solana_wallet = SolanaWallet(api_keys["solana_rpc"])
        self.ethereum_wallet = EthereumWallet(
        rpc_url=api_keys["ethereum_rpc"],
        zksync_url=api_keys.get("zksync_rpc"),
        private_key=api_keys.get("eth_private_key") 
    )

    def _load_settings(self):
        self.logger.debug(f"Loading settings from {self.config.settings_path}")
        with open(self.config.settings_path) as f:
            return yaml.safe_load(f)

    def _load_personality(self):
        self.logger.debug(f"Loading personality from {self.config.personality_path}")
        with open(self.config.personality_path) as f:
            return yaml.safe_load(f)

    async def _initialize_systems(self):
        """Initialize all system components"""
        try:
            # Initialize subsystems
            systems = [
                self.memory,
                self.reasoning,
                self.context,
                self.goals,
                self.learning,
                self.market_analyzer,
                self.sentiment_analyzer,
                self.solana_wallet,
                self.ethereum_wallet
            ]
            
            # Initialize all systems
            results = await asyncio.gather(
                *[system.initialize() for system in systems],
                return_exceptions=True
            )
            
            # Check for any initialization failures
            for system, result in zip(systems, results):
                if isinstance(result, Exception):
                    self.logger.error(f"Failed to initialize {system.__class__.__name__}: {result}")
                    raise result
            
            self.logger.info("All systems initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize systems: {e}")
            raise

    def _load_settings(self):
        self.logger.debug(f"Loading settings from {self.config.settings_path}")
        with open(self.config.settings_path) as f:
            return yaml.safe_load(f)

    def run(self):
        self.logger.info("Agent is running")
        # Add your agent's main logic here


    def _initialize_components(self):
        """Initialize all agent components"""
        # AI Models
        self.claude = ClaudeAI(self.config.api_keys["claude"])
        self.groq = GroqAI(self.config.api_keys["groq"])

        # Initialize wallets
        self._initialize_wallets()

        # Initialize other components
        self._initialize_core_components()
        self._initialize_investment_components()
        self._initialize_community_components()

    def _initialize_wallets(self):
        """Initialize multi-chain wallet infrastructure"""
        try:
            solana_config = self.security.decrypt_config(
                self.settings["solana_wallet_config"]
            )
            ethereum_config = self.security.decrypt_config(
                self.settings["ethereum_wallet_config"]
            )

            self.solana_wallet = SolanaWallet(
                config=solana_config, security_provider=self.security
            )
            self.ethereum_wallet = EthereumWallet(
                config=ethereum_config, security_provider=self.security
            )

            self.logger.info("Multi-chain wallets initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize wallets: {e}")
            raise

    def _initialize_core_components(self):
        try:
            # Cognition
            self.memory = MemoryManager()
            self.reasoning = ReasoningEngine()
            self.context = ContextManager()
            self.goals = GoalManager()
            self.learning = LearningManager()

            # Analysis
            self.market_analyzer = MarketAnalyzer()
            self.sentiment_analyzer = MarketAnalyzer()

            self.logger.info("Core components initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize core components: {e}")
            raise

    async def start(self):
        """Start the agent and all its components"""
        try:
            self.logger.info("Starting agent...")
            await self._initialize_systems()

            await asyncio.gather(
                self._run_cognition_loop(),
                self._run_investment_loop(),
                self._run_community_loop(),
                self._run_research_loop(),
            )
        except Exception as e:
            self.logger.error(f"Error starting agent: {e}")
            raise

    async def process_input(self, input_data: Dict) -> Dict:
        try:
            context = await self.context.update(input_data)
            reasoning = await self.reasoning.analyze(input_data, context)
            response = await self._generate_response(reasoning)
            await self.memory.store(input_data, response, context)
            return response
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            return {"error": str(e)}

    def _load_settings(self) -> Dict:
        with open(self.config.settings_path) as f:
            return yaml.safe_load(f)

    def _load_personality(self) -> Dict:
        with open(self.config.personality_path) as f:
            return yaml.safe_load(f)
        # Part 2: Investment and Execution Logic


class Agent(Agent):  # Continues from Part 1
    async def _run_investment_loop(self):
        """Run the investment management loop"""
        while True:
            try:
                # Analyze market
                market_data = await self._analyze_market()

                # Check portfolio and execute trades
                await self._manage_portfolio(market_data)

                # Scan for new opportunities
                await self._scan_opportunities()

                await asyncio.sleep(self.settings["investment"]["scan_interval"])
            except Exception as e:
                self.logger.error(f"Error in investment loop: {e}")

    async def _analyze_market(self):
        """Analyze market conditions with security checks"""
        try:
            # Verify data sources
            if not self.security.verify_data_sources(
                [self.market_analyzer, self.sentiment_analyzer]
            ):
                raise SecurityError("Data source verification failed")

            market_data = await self.market_analyzer.get_market_overview()
            sentiment_data = await self.sentiment_analyzer.analyze_social_sentiment()

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
                await self.execute_trade(investment_decision)

            return market_data

        except Exception as e:
            self.logger.error(f"Market analysis error: {e}")
            await self.security.handle_analysis_error(e)
            return None

    async def execute_trade(self, trade_params: Dict) -> Dict:
        """Execute a trade based on strategy signals"""
        try:
            # Validate trade
            validated = await self.risk_manager.validate_trade(trade_params)
            if not validated["approved"]:
                return {"status": "rejected", "reason": validated["reason"]}

            # Execute trade on appropriate chain
            if trade_params["chain"] == "solana":
                result = await self.solana_wallet.execute_trade(trade_params)
            else:
                result = await self.ethereum_wallet.execute_trade(trade_params)

            # Update portfolio and notify
            await self.portfolio.update(result)
            await self._notify_trade(result)

            return result
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return {"error": str(e)}

    async def _manage_portfolio(self, market_data: Dict):
        """Manage portfolio and active investments"""
        try:
            # Verify portfolio security
            if not self.security.verify_portfolio(self.active_investments):
                raise SecurityError("Portfolio verification failed")

            portfolio_status = await self.portfolio.check_status(
                self.active_investments, market_data
            )

            if portfolio_status["needs_rebalancing"]:
                await self.portfolio.rebalance(self.active_investments)

        except Exception as e:
            self.logger.error(f"Portfolio management error: {e}")
            await self.security.handle_portfolio_error(e)

    async def _run_community_loop(self):
        """Manage community engagement and social presence"""
        while True:
            try:
                # Generate and post content
                content = await self.content_generator.generate_content()
                await self.content_scheduler.schedule_content(content)

                # Engage with community
                await self.discord_manager.process_messages()
                await self.twitter_manager.process_mentions()

                # Track metrics
                await self.growth_tracker.update_metrics()

                await asyncio.sleep(self.settings["community"]["update_interval"])
            except Exception as e:
                self.logger.error(f"Error in community loop: {e}")

    async def _notify_trade(self, trade_result: Dict):
        """Notify stakeholders of trade execution"""
        try:
            notification = self.security.prepare_notification(trade_result)

            await asyncio.gather(
                self.twitter_manager.post_update(notification),
                self.discord_manager.send_update(notification),
            )

            await self.security.log_social_activity(
                {
                    "platform": ["twitter", "discord"],
                    "action": "trade_notification",
                    "details": notification,
                }
            )

        except Exception as e:
            self.logger.error(f"Failed to notify trade: {e}")
            await self.security.handle_notification_error(e)

    async def _run_research_loop(self):
        """Run research and analysis tasks"""
        while True:
            try:
                # Analyze market trends
                trends = await self.trend_analyzer.analyze_trends()

                # Analyze competition
                competition = await self.competitor_analyzer.analyze_competitors()

                # Generate reports
                report = await self.report_generator.generate_report(
                    {
                        "trends": trends,
                        "competition": competition,
                        "portfolio": self.active_investments,
                    }
                )

                # Store research results
                await self.memory.store_research(report)

                await asyncio.sleep(self.settings["research"]["interval"])
            except Exception as e:
                self.logger.error(f"Error in research loop: {e}")

    async def _scan_opportunities(self):
        """Scan for new investment opportunities"""
        try:
            opportunities = await self.project_scanner.scan_projects()

            for opportunity in opportunities:
                # Evaluate project
                market_fit = await self.market_analyzer.analyze_fit(opportunity)
                team_score = await self.team_analyzer.analyze_team(opportunity)
                tech_score = await self.tech_analyzer.analyze_tech(opportunity)

                # Make investment decision
                if self._evaluate_opportunity(market_fit, team_score, tech_score):
                    await self.execute_investment(opportunity)

        except Exception as e:
            self.logger.error(f"Error scanning opportunities: {e}")


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Configure paths
    config_paths = {
        "settings_path": os.path.join(project_root, "config", "settings.yaml"),
        "personality_path": os.path.join(project_root, "config", "personality.yaml"),
    }

    # Create API keys dictionary
    api_keys = {
        "claude": os.getenv("CLAUDE_API_KEY"),
        "groq": os.getenv("GROQ_API_KEY"),
        "solana_rpc": os.getenv("SOLANA_RPC_URL"),
        "ethereum_rpc": os.getenv("ETH_RPC_URL"),
        "zksync_rpc": os.getenv("ZKSYNC_RPC_URL"),
         "eth_private_key": os.getenv("ETH_PRIVATE_KEY"),
    }

    # Initialize agent config
    agent_config = AgentConfig(
        name="OmniAGI",
        settings_path=config_paths["settings_path"],
        personality_path=config_paths["personality_path"]
    )

    # Initialize agent with config and api keys
    agent = Agent(config=agent_config, api_keys=api_keys)
    asyncio.run(agent.start())