from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from uuid import uuid4

# Services imports
from core.cognition.reasoning import ReasoningEngine
from core.personality.traits import PersonalityManager
from blockchain.solana.wallet import WalletService
from communication.social.analytics import SocialAnalytics

# Models


class Message(BaseModel):
    content: str
    sender: str
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AnalysisRequest(BaseModel):
    topic: str
    context: Optional[Dict[str, Any]] = None
    depth: Optional[str] = "medium"


class TransactionRequest(BaseModel):
    operation: str
    amount: float
    token: str
    destination: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# API Setup
app = FastAPI(
    title="AGI Agent API",
    description="API endpoints for autonomous agent interactions",
    version="1.0.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logger = logging.getLogger(__name__)

# Dependency for API key validation


async def verify_api_key(x_api_key: str = Header(...)):
    if not x_api_key or x_api_key != "your-api-key":  # Replace with actual verification
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


class AgentAPI:
    def __init__(
        self,
        reasoning_engine: ReasoningEngine,
        personality_manager: PersonalityManager,
        wallet_service: WalletService,
        social_analytics: SocialAnalytics,
    ):
        self.reasoning = reasoning_engine
        self.personality = personality_manager
        self.wallet = wallet_service
        self.analytics = social_analytics
        self.conversations: Dict[str, List[Dict]] = {}

    # Chat Endpoints
    @app.post("/v1/chat", response_model=Dict[str, Any])
    async def chat(self, message: Message, api_key: str = Depends(verify_api_key)):
        """Process chat messages and generate responses"""
        try:
            # Generate conversation ID if not provided
            conv_id = message.conversation_id or str(uuid4())

            # Store conversation context
            if conv_id not in self.conversations:
                self.conversations[conv_id] = []
            self.conversations[conv_id].append(
                {
                    "role": "user",
                    "content": message.content,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Generate response
            response = await self.reasoning.generate_response(
                message.content, context=self.conversations[conv_id]
            )

            # Store response
            self.conversations[conv_id].append(
                {
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return {
                "conversation_id": conv_id,
                "response": response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in chat endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Analysis Endpoints
    @app.post("/v1/analyze", response_model=Dict[str, Any])
    async def analyze(
        self,
        request: AnalysisRequest,
        background_tasks: BackgroundTasks,
        api_key: str = Depends(verify_api_key),
    ):
        """Analyze topics or market conditions"""
        try:
            # Start analysis
            analysis = await self.reasoning.analyze_topic(
                topic=request.topic, context=request.context, depth=request.depth
            )

            # Schedule background analytics
            background_tasks.add_task(
                self.analytics.track_analysis, topic=request.topic, result=analysis
            )

            return {"analysis": analysis, "timestamp": datetime.now().isoformat()}

        except Exception as e:
            logger.error(f"Error in analysis endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Blockchain Endpoints
    @app.post("/v1/transaction", response_model=Dict[str, Any])
    async def execute_transaction(
        self, request: TransactionRequest, api_key: str = Depends(verify_api_key)
    ):
        """Execute blockchain transactions"""
        try:
            # Validate transaction
            if request.amount <= 0:
                raise HTTPException(status_code=400, detail="Invalid amount")

            # Execute transaction
            transaction = await self.wallet.execute_transaction(
                operation=request.operation,
                amount=request.amount,
                token=request.token,
                destination=request.destination,
                metadata=request.metadata,
            )

            return {
                "transaction_id": transaction.id,
                "status": transaction.status,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in transaction endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Status and Analytics Endpoints
    @app.get("/v1/status")
    async def get_status(self, api_key: str = Depends(verify_api_key)):
        """Get agent status and metrics"""
        try:
            return {
                "status": "active",
                "uptime": "...",  # Implement uptime tracking
                "metrics": {
                    "conversations": len(self.conversations),
                    "transactions": await self.wallet.get_transaction_count(),
                    "analysis_requests": await self.analytics.get_request_count(),
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in status endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/v1/analytics/{timeframe}")
    async def get_analytics(
        self, timeframe: str, api_key: str = Depends(verify_api_key)
    ):
        """Get analytics for specified timeframe"""
        try:
            analytics_data = await self.analytics.get_analytics(timeframe)
            return {
                "timeframe": timeframe,
                "data": analytics_data,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in analytics endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Personality Management Endpoints
    @app.get("/v1/personality/traits")
    async def get_personality_traits(self, api_key: str = Depends(verify_api_key)):
        """Get current personality traits"""
        try:
            return await self.personality.get_traits()

        except Exception as e:
            logger.error(f"Error getting personality traits: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/v1/personality/adjust")
    async def adjust_personality(
        self, adjustments: Dict[str, float], api_key: str = Depends(verify_api_key)
    ):
        """Adjust personality traits"""
        try:
            return await self.personality.adjust_traits(adjustments)

        except Exception as e:
            logger.error(f"Error adjusting personality: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Health Check
    @app.get("/health")
    async def health_check():
        """Basic health check endpoint"""
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
