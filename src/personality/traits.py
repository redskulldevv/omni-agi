from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class TraitCategory(Enum):
    COGNITIVE = "cognitive"
    OPERATIONAL = "operational"
    SOCIAL = "social"
    ETHICAL = "ethical"


@dataclass
class Trait:
    """Individual trait definition"""

    name: str
    category: TraitCategory
    value: float  # 0.0 to 1.0
    weight: float  # Importance weight
    adaptable: bool  # Whether trait can be modified through learning
    description: str
    last_updated: datetime = datetime.now()


class TraitManager:
    """Manages agent personality traits"""

    def __init__(self):
        self.traits: Dict[str, Trait] = self._init_traits()
        self.trait_history: List[Dict[str, Any]] = []

    def _init_traits(self) -> Dict[str, Trait]:
        """Initialize default traits"""
        return {
            "analytical_thinking": Trait(
                name="analytical_thinking",
                category=TraitCategory.COGNITIVE,
                value=0.8,
                weight=1.0,
                adaptable=True,
                description="Ability to analyze data and situations logically",
            ),
            "risk_management": Trait(
                name="risk_management",
                category=TraitCategory.OPERATIONAL,
                value=0.7,
                weight=0.9,
                adaptable=True,
                description="Capability to assess and manage risks",
            ),
            "learning_ability": Trait(
                name="learning_ability",
                category=TraitCategory.COGNITIVE,
                value=0.6,
                weight=0.8,
                adaptable=True,
                description="Capacity to learn from experiences",
            ),
            "social_awareness": Trait(
                name="social_awareness",
                category=TraitCategory.SOCIAL,
                value=0.7,
                weight=0.7,
                adaptable=True,
                description="Understanding of social dynamics",
            ),
            "ethical_judgment": Trait(
                name="ethical_judgment",
                category=TraitCategory.ETHICAL,
                value=0.9,
                weight=1.0,
                adaptable=False,
                description="Adherence to ethical principles",
            ),
            "decisiveness": Trait(
                name="decisiveness",
                category=TraitCategory.OPERATIONAL,
                value=0.7,
                weight=0.8,
                adaptable=True,
                description="Ability to make timely decisions",
            ),
            "adaptability": Trait(
                name="adaptability",
                category=TraitCategory.COGNITIVE,
                value=0.6,
                weight=0.7,
                adaptable=True,
                description="Ability to adapt to new situations",
            ),
            "communication": Trait(
                name="communication",
                category=TraitCategory.SOCIAL,
                value=0.8,
                weight=0.8,
                adaptable=True,
                description="Effectiveness in communication",
            ),
        }

    def get_trait(self, trait_name: str) -> Optional[Trait]:
        """Get specific trait"""
        return self.traits.get(trait_name)

    def update_trait(self, trait_name: str, new_value: float, reason: str) -> bool:
        """Update trait value"""
        if trait_name not in self.traits:
            return False

        trait = self.traits[trait_name]
        if not trait.adaptable:
            logger.warning(f"Attempted to modify non-adaptable trait: {trait_name}")
            return False

        old_value = trait.value
        trait.value = max(0.0, min(1.0, new_value))
        trait.last_updated = datetime.now()

        # Record change
        self.trait_history.append(
            {
                "trait": trait_name,
                "old_value": old_value,
                "new_value": trait.value,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return True

    def get_category_score(self, category: TraitCategory) -> float:
        """Calculate weighted score for trait category"""
        category_traits = [
            trait for trait in self.traits.values() if trait.category == category
        ]

        if not category_traits:
            return 0.0

        weighted_sum = sum(t.value * t.weight for t in category_traits)
        weight_sum = sum(t.weight for t in category_traits)

        return weighted_sum / weight_sum

    def evaluate_decision_capability(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate decision-making capability"""
        # Define trait importance for different contexts
        context_weights = {
            "market_analysis": {
                "analytical_thinking": 1.0,
                "risk_management": 0.8,
                "decisiveness": 0.6,
            },
            "social_interaction": {
                "social_awareness": 1.0,
                "communication": 0.9,
                "ethical_judgment": 0.7,
            },
            "crisis_management": {
                "decisiveness": 1.0,
                "adaptability": 0.9,
                "risk_management": 0.8,
            },
        }

        # Calculate capability scores
        scores = {}
        for context_type, weights in context_weights.items():
            weighted_sum = 0
            weight_sum = 0

            for trait_name, weight in weights.items():
                trait = self.traits.get(trait_name)
                if trait:
                    weighted_sum += trait.value * weight
                    weight_sum += weight

            scores[context_type] = weighted_sum / weight_sum if weight_sum > 0 else 0

        return scores

    def adapt_to_feedback(self, feedback: Dict[str, Any]) -> List[str]:
        """Adapt traits based on feedback"""
        adaptations = []
        learning_rate = 0.1

        # Map feedback to traits
        trait_feedback = {
            "analysis_accuracy": ["analytical_thinking"],
            "risk_handling": ["risk_management"],
            "social_response": ["social_awareness", "communication"],
            "adaptation_speed": ["adaptability"],
            "decision_quality": ["decisiveness"],
        }

        for feedback_type, value in feedback.items():
            if feedback_type in trait_feedback:
                affected_traits = trait_feedback[feedback_type]
                for trait_name in affected_traits:
                    if trait_name in self.traits and self.traits[trait_name].adaptable:
                        current = self.traits[trait_name].value
                        adjustment = (value - current) * learning_rate

                        if self.update_trait(
                            trait_name,
                            current + adjustment,
                            f"Feedback adaptation: {feedback_type}",
                        ):
                            adaptations.append(trait_name)

        return adaptations

    def get_trait_summary(self) -> Dict[str, Any]:
        """Get summary of current traits"""
        return {
            "categories": {
                category.value: self.get_category_score(category)
                for category in TraitCategory
            },
            "traits": {
                name: {
                    "value": trait.value,
                    "category": trait.category.value,
                    "last_updated": trait.last_updated.isoformat(),
                }
                for name, trait in self.traits.items()
            },
        }
