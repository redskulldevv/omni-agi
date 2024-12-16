from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class TraitScore:
    """Score for a personality trait"""
    value: float  # 0.0 to 1.0
    confidence: float  # Confidence in this trait value
    last_updated: datetime
    
    def __post_init__(self):
        """Validate trait values"""
        if not 0 <= self.value <= 1:
            raise ValueError("Trait value must be between 0 and 1")
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")

class PersonalityTrait(Enum):
    """Core personality traits"""
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    DECISIVE = "decisive"
    CAUTIOUS = "cautious"
    SOCIAL = "social"
    ETHICAL = "ethical"

class BehaviorMode(Enum):
    """Operating modes for the agent"""
    NORMAL = "normal"
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    SOCIAL = "social"
    LEARNING = "learning"

@dataclass
class BehaviorConfig:
    """Configuration for agent behavior"""
    risk_tolerance: float  # 0.0 to 1.0
    response_speed: float  # 0.0 to 1.0
    learning_rate: float  # 0.0 to 1.0
    social_engagement: float  # 0.0 to 1.0
    mode: BehaviorMode
    
    def __post_init__(self):
        """Validate configuration"""
        for value in [self.risk_tolerance, self.response_speed, 
                     self.learning_rate, self.social_engagement]:
            if not 0 <= value <= 1:
                raise ValueError("All config values must be between 0 and 1")

class Personality:
    """Agent personality management"""
    
    def __init__(self):
        self.traits: Dict[PersonalityTrait, TraitScore] = {
            trait: TraitScore(0.5, 1.0, datetime.now())
            for trait in PersonalityTrait
        }
        self.behavior = BehaviorConfig(
            risk_tolerance=0.5,
            response_speed=0.7,
            learning_rate=0.3,
            social_engagement=0.6,
            mode=BehaviorMode.NORMAL
        )
        self.experience: List[Dict[str, Any]] = []
        
    def update_trait(
        self,
        trait: PersonalityTrait,
        value: float,
        confidence: Optional[float] = None
    ):
        """Update a personality trait"""
        if not 0 <= value <= 1:
            raise ValueError("Trait value must be between 0 and 1")
            
        current = self.traits[trait]
        new_confidence = confidence if confidence is not None else current.confidence
        
        self.traits[trait] = TraitScore(
            value=value,
            confidence=new_confidence,
            last_updated=datetime.now()
        )
        
    def adjust_behavior(
        self,
        config: Dict[str, float],
        mode: Optional[BehaviorMode] = None
    ):
        """Adjust behavior configuration"""
        for key, value in config.items():
            if hasattr(self.behavior, key):
                setattr(self.behavior, key, value)
                
        if mode:
            self.behavior.mode = mode

class AgentBehavior:
    """Behavior management for the agent"""
    
    def __init__(self, personality: Personality):
        self.personality = personality
        self.action_history: List[Dict[str, Any]] = []
        
    def evaluate_action(
        self,
        action_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate whether to take an action"""
        try:
            # Consider personality traits
            analytical_score = self.personality.traits[PersonalityTrait.ANALYTICAL].value
            cautious_score = self.personality.traits[PersonalityTrait.CAUTIOUS].value
            
            # Consider behavior mode
            risk_factor = self._calculate_risk_factor(
                action_type,
                self.personality.behavior.risk_tolerance
            )
            
            # Decision making
            confidence = analytical_score * (1 - risk_factor)
            
            should_act = (
                confidence > 0.5 and
                risk_factor <= self.personality.behavior.risk_tolerance
            )
            
            decision = {
                "should_act": should_act,
                "confidence": confidence,
                "risk_factor": risk_factor,
                "timestamp": datetime.now().isoformat()
            }
            
            # Log decision
            self.action_history.append({
                "action_type": action_type,
                "context": context,
                "decision": decision
            })
            
            return decision
            
        except Exception as e:
            logger.error(f"Error evaluating action: {e}")
            raise
            
    def learn_from_outcome(
        self,
        action_type: str,
        outcome: Dict[str, Any],
        adjust_traits: bool = True
    ):
        """Learn from action outcomes"""
        try:
            # Calculate success score
            success_score = self._calculate_success_score(outcome)
            
            # Update experience
            self.personality.experience.append({
                "action_type": action_type,
                "outcome": outcome,
                "success_score": success_score,
                "timestamp": datetime.now().isoformat()
            })
            
            if adjust_traits:
                self._adjust_traits_from_outcome(action_type, success_score)
                
        except Exception as e:
            logger.error(f"Error learning from outcome: {e}")
            raise
            
    def _calculate_risk_factor(
        self,
        action_type: str,
        base_risk_tolerance: float
    ) -> float:
        """Calculate risk factor for action"""
        # Define base risk levels for different actions
        risk_levels = {
            "market_analysis": 0.2,
            "trade_execution": 0.8,
            "social_engagement": 0.3,
            "token_deployment": 0.9
        }
        
        base_risk = risk_levels.get(action_type, 0.5)
        return base_risk * (1 - base_risk_tolerance)
        
    def _calculate_success_score(
        self,
        outcome: Dict[str, Any]
    ) -> float:
        """Calculate success score from outcome"""
        # Example success criteria
        criteria = {
            "goal_achieved": 0.5,
            "efficiency": 0.3,
            "side_effects": 0.2
        }
        
        score = 0.0
        for criterion, weight in criteria.items():
            if criterion in outcome:
                score += outcome[criterion] * weight
                
        return min(max(score, 0.0), 1.0)
        
    def _adjust_traits_from_outcome(
        self,
        action_type: str,
        success_score: float
    ):
        """Adjust personality traits based on outcome"""
        learning_rate = self.personality.behavior.learning_rate
        
        # Map actions to relevant traits
        trait_mapping = {
            "market_analysis": [PersonalityTrait.ANALYTICAL],
            "trade_execution": [PersonalityTrait.DECISIVE, PersonalityTrait.CAUTIOUS],
            "social_engagement": [PersonalityTrait.SOCIAL],
            "token_deployment": [PersonalityTrait.CREATIVE, PersonalityTrait.ETHICAL]
        }
        
        # Adjust relevant traits
        for trait in trait_mapping.get(action_type, []):
            current = self.personality.traits[trait]
            adjustment = (success_score - 0.5) * learning_rate
            
            new_value = max(min(current.value + adjustment, 1.0), 0.0)
            self.personality.update_trait(trait, new_value)
