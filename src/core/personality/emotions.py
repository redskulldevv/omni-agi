from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from datetime import datetime
import logging
import random

logger = logging.getLogger(__name__)


class EmotionType(Enum):
    """Base emotions the agent can experience"""

    OPTIMISTIC = "optimistic"
    CAUTIOUS = "cautious"
    EXCITED = "excited"
    CONCERNED = "concerned"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    NEUTRAL = "neutral"
    CURIOUS = "curious"
    FOCUSED = "focused"
    REFLECTIVE = "reflective"


@dataclass
class EmotionalState:
    """Current emotional state"""

    primary: EmotionType
    intensity: float  # 0.0 to 1.0
    secondary: Optional[EmotionType] = None
    timestamp: datetime = datetime.now()
    triggers: List[str] = None

    def __post_init__(self):
        """Validate emotional state"""
        if not 0 <= self.intensity <= 1:
            raise ValueError("Emotion intensity must be between 0 and 1")
        if self.triggers is None:
            self.triggers = []


class EmotionManager:
    """Manages agent's emotional states and responses"""

    def __init__(self):
        self.current_state = EmotionalState(primary=EmotionType.NEUTRAL, intensity=0.5)
        self.state_history: List[EmotionalState] = []
        self.emotion_triggers: Dict[EmotionType, Set[str]] = self._init_triggers()

    def _init_triggers(self) -> Dict[EmotionType, Set[str]]:
        """Initialize emotion triggers"""
        return {
            EmotionType.OPTIMISTIC: {
                "positive_market_trend",
                "successful_trade",
                "community_growth",
                "strong_metrics",
            },
            EmotionType.CAUTIOUS: {
                "market_volatility",
                "risk_alert",
                "uncertainty",
                "complex_situation",
            },
            EmotionType.EXCITED: {
                "breakthrough",
                "major_opportunity",
                "exceptional_performance",
                "innovation",
            },
            EmotionType.CONCERNED: {
                "market_downturn",
                "risk_exposure",
                "negative_feedback",
                "system_issues",
            },
            EmotionType.CONFIDENT: {
                "consistent_success",
                "validated_strategy",
                "strong_performance",
                "positive_feedback",
            },
            EmotionType.UNCERTAIN: {
                "ambiguous_data",
                "conflicting_signals",
                "unknown_variables",
                "new_situation",
            },
            EmotionType.CURIOUS: {
                "new_pattern",
                "unusual_activity",
                "learning_opportunity",
                "market_anomaly",
            },
            EmotionType.FOCUSED: {
                "critical_task",
                "complex_analysis",
                "important_decision",
                "time_sensitive",
            },
        }

    async def update_emotional_state(
        self, triggers: List[str], context: Optional[Dict] = None
    ) -> EmotionalState:
        """Update emotional state based on triggers and context"""
        try:
            # Count trigger matches for each emotion
            emotion_matches = {
                emotion: len(triggers & trigger_set)
                for emotion, trigger_set in self.emotion_triggers.items()
            }

            # Get primary emotion
            primary_emotion = max(emotion_matches.items(), key=lambda x: x[1])[0]

            # Calculate intensity based on match count and context
            base_intensity = min(
                emotion_matches[primary_emotion] / max(len(triggers), 1), 1.0
            )

            # Adjust intensity based on context
            intensity = self._adjust_intensity(base_intensity, context)

            # Get secondary emotion if any
            emotion_matches.pop(primary_emotion)
            secondary_emotion = (
                max(emotion_matches.items(), key=lambda x: x[1])[0]
                if any(emotion_matches.values())
                else None
            )

            # Create new state
            new_state = EmotionalState(
                primary=primary_emotion,
                intensity=intensity,
                secondary=secondary_emotion,
                triggers=triggers,
            )

            # Record state change
            self._record_state_change(new_state)

            return new_state

        except Exception as e:
            logger.error(f"Error updating emotional state: {e}")
            raise

    def _adjust_intensity(
        self, base_intensity: float, context: Optional[Dict] = None
    ) -> float:
        """Adjust emotion intensity based on context"""
        if not context:
            return base_intensity

        adjustments = {
            "market_impact": 0.2,
            "time_pressure": 0.15,
            "risk_level": 0.25,
            "confidence": 0.2,
        }

        intensity = base_intensity
        for factor, weight in adjustments.items():
            if factor in context:
                intensity += context[factor] * weight

        return min(max(intensity, 0.0), 1.0)

    def _record_state_change(self, new_state: EmotionalState):
        """Record emotional state change"""
        self.state_history.append(self.current_state)
        self.current_state = new_state

    def get_response_modulation(self) -> Dict[str, float]:
        """Get response modulation based on current emotional state"""
        modulations = {
            "confidence_level": 0.5,
            "risk_tolerance": 0.5,
            "response_speed": 0.5,
            "detail_focus": 0.5,
        }

        # Adjust based on primary emotion
        emotion_adjustments = {
            EmotionType.OPTIMISTIC: {"confidence_level": 0.2, "risk_tolerance": 0.1},
            EmotionType.CAUTIOUS: {"risk_tolerance": -0.2, "detail_focus": 0.2},
            EmotionType.CONFIDENT: {"confidence_level": 0.3, "response_speed": 0.1},
            EmotionType.UNCERTAIN: {"confidence_level": -0.2, "detail_focus": 0.2},
        }

        # Apply adjustments
        if self.current_state.primary in emotion_adjustments:
            adjustments = emotion_adjustments[self.current_state.primary]
            for param, adjustment in adjustments.items():
                modulations[param] += adjustment * self.current_state.intensity

        # Ensure bounds
        return {key: min(max(value, 0.0), 1.0) for key, value in modulations.items()}

    def get_emotional_expression(self) -> str:
        """Get appropriate emotional expression for current state"""
        expressions = {
            EmotionType.OPTIMISTIC: [
                "I'm seeing positive opportunities here.",
                "The outlook appears favorable.",
                "I'm optimistic about these developments.",
            ],
            EmotionType.CAUTIOUS: [
                "We should proceed carefully.",
                "Let's consider all angles first.",
                "I recommend a measured approach.",
            ],
            EmotionType.EXCITED: [
                "This is a remarkable opportunity!",
                "I'm very enthusiastic about this.",
                "The potential here is exceptional!",
            ],
            EmotionType.CONCERNED: [
                "We need to be mindful of the risks.",
                "I'm noticing some concerning patterns.",
                "This requires careful consideration.",
            ],
        }

        if self.current_state.primary in expressions:
            options = expressions[self.current_state.primary]
            return random.choice(options)

        return "I understand and will analyze this carefully."

    def get_emotion_history(self, limit: Optional[int] = None) -> List[EmotionalState]:
        """Get emotion history with optional limit"""
        history = self.state_history
        if limit:
            history = history[-limit:]
        return history
