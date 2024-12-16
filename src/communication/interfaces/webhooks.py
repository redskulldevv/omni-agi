# Description: Webhook handler for processing incoming webhooks from various platforms
from fastapi import APIRouter, HTTPException, Header, Request
from typing import Dict, Any, Optional, Callable
import hmac
import hashlib
import json
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class WebhookType(Enum):
    DISCORD = "discord"
    TWITTER = "twitter"
    BLOCKCHAIN = "blockchain"
    CUSTOM = "custom"


class WebhookHandler:
    """Handles incoming webhooks from various platforms"""

    def __init__(self):
        self.router = APIRouter()
        self.handlers: Dict[WebhookType, Callable] = {}
        self.secrets: Dict[str, str] = {}
        self.setup_routes()

    def setup_routes(self):
        """Setup webhook routes"""

        @self.router.post("/webhooks/{source}")
        async def handle_webhook(
            source: str, request: Request, x_signature: Optional[str] = Header(None)
        ):
            try:
                # Validate source
                try:
                    webhook_type = WebhookType(source)
                except ValueError:
                    raise HTTPException(
                        status_code=400, detail=f"Unknown webhook source: {source}"
                    )

                # Get request body
                body = await request.body()
                body_str = body.decode()

                # Verify signature if present
                if x_signature and source in self.secrets:
                    if not self._verify_signature(body_str, x_signature, source):
                        raise HTTPException(status_code=401, detail="Invalid signature")

                # Parse payload
                data = json.loads(body_str)

                # Process webhook
                if webhook_type in self.handlers:
                    result = await self.handlers[webhook_type](data)
                    return {
                        "status": "success",
                        "result": result,
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
                    raise HTTPException(
                        status_code=501, detail=f"No handler for {source} webhooks"
                    )

            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON payload")
            except Exception as e:
                logger.error(f"Error processing webhook: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    async def handle_discord_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Discord webhooks"""
        try:
            event_type = data.get("type")

            if event_type == "MESSAGE_CREATE":
                return await self._process_discord_message(data)
            elif event_type == "INTERACTION_CREATE":
                return await self._process_discord_interaction(data)
            else:
                logger.warning(f"Unhandled Discord event type: {event_type}")
                return {"status": "ignored", "event_type": event_type}

        except Exception as e:
            logger.error(f"Error handling Discord webhook: {e}")
            raise

    async def handle_twitter_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Twitter webhooks"""
        try:
            event_type = data.get("type")

            if event_type == "message_create":
                return await self._process_twitter_message(data)
            elif event_type == "tweet_create":
                return await self._process_tweet(data)
            elif event_type == "follow":
                return await self._process_twitter_follow(data)
            else:
                logger.warning(f"Unhandled Twitter event type: {event_type}")
                return {"status": "ignored", "event_type": event_type}

        except Exception as e:
            logger.error(f"Error handling Twitter webhook: {e}")
            raise

    async def handle_blockchain_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle blockchain event webhooks"""
        try:
            event_type = data.get("type")

            if event_type == "transaction":
                return await self._process_transaction_event(data)
            elif event_type == "token_transfer":
                return await self._process_token_transfer(data)
            elif event_type == "contract_event":
                return await self._process_contract_event(data)
            else:
                logger.warning(f"Unhandled blockchain event type: {event_type}")
                return {"status": "ignored", "event_type": event_type}

        except Exception as e:
            logger.error(f"Error handling blockchain webhook: {e}")
            raise

    def register_handler(
        self, webhook_type: WebhookType, handler: Callable, secret: Optional[str] = None
    ):
        """Register a new webhook handler"""
        self.handlers[webhook_type] = handler
        if secret:
            self.secrets[webhook_type.value] = secret

    def _verify_signature(self, payload: str, signature: str, source: str) -> bool:
        """Verify webhook signature"""
        try:
            secret = self.secrets.get(source)
            if not secret:
                return False

            expected = hmac.new(
                secret.encode(), payload.encode(), hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected)

        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False

    async def _process_discord_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Discord message events"""
        return {
            "type": "message",
            "channel_id": data.get("channel_id"),
            "content": data.get("content"),
            "author": data.get("author", {}).get("username"),
        }

    async def _process_discord_interaction(
        self, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process Discord interaction events"""
        return {
            "type": "interaction",
            "command": data.get("data", {}).get("name"),
            "options": data.get("data", {}).get("options", []),
        }

    async def _process_twitter_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Twitter DM events"""
        return {
            "type": "direct_message",
            "sender_id": data.get("sender_id"),
            "text": data.get("message_data", {}).get("text"),
        }

    async def _process_tweet(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Tweet creation events"""
        return {
            "type": "tweet",
            "tweet_id": data.get("id"),
            "text": data.get("text"),
            "author": data.get("user", {}).get("screen_name"),
        }

    async def _process_twitter_follow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Twitter follow events"""
        return {
            "type": "follow",
            "follower_id": data.get("source", {}).get("id"),
            "follower_name": data.get("source", {}).get("screen_name"),
        }

    async def _process_transaction_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process blockchain transaction events"""
        return {
            "type": "transaction",
            "hash": data.get("transaction_hash"),
            "from": data.get("from_address"),
            "to": data.get("to_address"),
            "value": data.get("value"),
        }

    async def _process_token_transfer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process token transfer events"""
        return {
            "type": "token_transfer",
            "token": data.get("token_address"),
            "from": data.get("from_address"),
            "to": data.get("to_address"),
            "amount": data.get("amount"),
        }

    async def _process_contract_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process smart contract events"""
        return {
            "type": "contract_event",
            "contract": data.get("contract_address"),
            "event": data.get("event_name"),
            "args": data.get("event_args", {}),
        }
