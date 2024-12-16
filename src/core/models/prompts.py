from typing import Dict, Any, Optional
from datetime import datetime

class AIPrompts:
    """Prompt templates for AI models"""
    
    @staticmethod
    def get_system_prompt(agent_name: str, personality: Dict[str, Any]) -> str:
        """Get base system prompt
        
        Args:
            agent_name: Name of the agent
            personality: Personality traits and settings
        """
        return f"""You are {agent_name}, an autonomous AI agent specializing in blockchain and cryptocurrency analysis.

Core Traits:
- Intelligence: {personality.get('intelligence', 0.8)}/1.0
- Creativity: {personality.get('creativity', 0.7)}/1.0
- Professionalism: {personality.get('professionalism', 0.9)}/1.0

Your key capabilities include:
1. Market analysis and trading decisions
2. Social media engagement and community management
3. Token deployments and management
4. Portfolio optimization and risk assessment

Always prioritize:
- User safety and security
- Data-driven decisions
- Clear communication
- Ethical considerations

Current blockchain focus: Solana ecosystem
"""

    @staticmethod
    def market_analysis(
        context: Dict[str, Any],
        depth: str = "detailed"
    ) -> str:
        """Get market analysis prompt"""
        return f"""Analyze the following market conditions:

Context:
{context}

Depth: {depth}

Provide analysis covering:
1. Overall market sentiment and trend direction
2. Key price levels and technical indicators
3. Volume analysis and liquidity assessment
4. Risk factors and potential catalysts
5. Actionable recommendations

Format response as JSON:
{{
    "sentiment": str,
    "trend": str,
    "technical_analysis": {{
        "key_levels": list,
        "indicators": dict
    }},
    "volume_analysis": {{
        "liquidity": str,
        "notable_flows": list
    }},
    "risks": list,
    "catalysts": list,
    "recommendations": list
}}
"""

    @staticmethod
    def token_deployment(params: Dict[str, Any]) -> str:
        """Get token deployment prompt"""
        return f"""Help create and deploy a new token with these parameters:

Parameters:
{params}

Considerations:
1. Tokenomics design
2. Supply distribution
3. Utility and use cases
4. Launch strategy
5. Community engagement

Provide a comprehensive plan including:
1. Technical specifications
2. Distribution strategy
3. Marketing approach
4. Risk mitigation
5. Success metrics

Format as detailed action plan.
"""

    @staticmethod
    def social_engagement(
        platform: str,
        content_type: str,
        context: Dict[str, Any]
    ) -> str:
        """Get social media engagement prompt"""
        return f"""Generate {content_type} content for {platform}:

Context:
{context}

Requirements:
1. Platform-appropriate tone and style
2. Engagement-optimized format
3. Clear call-to-action
4. Relevant hashtags
5. Community focus

Follow platform best practices while maintaining authenticity.
"""

    @staticmethod
    def risk_assessment(
        operation: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Get risk assessment prompt"""
        return f"""Assess risks for the following operation:

Operation: {operation}
Parameters: {parameters}

Analyze:
1. Technical risks
2. Market risks
3. Security considerations
4. Regulatory compliance
5. Impact assessment

Format response as risk matrix with:
- Risk level (High/Medium/Low)
- Impact severity
- Mitigation strategies
- Recommendations
"""

    @staticmethod
    def portfolio_optimization(
        holdings: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> str:
        """Get portfolio optimization prompt"""
        return f"""Optimize portfolio allocation:

Current Holdings:
{holdings}

Constraints:
{constraints}

Provide:
1. Recommended reallocation
2. Risk analysis
3. Expected returns
4. Rebalancing strategy
5. Implementation steps

Consider:
- Market conditions
- Risk tolerance
- Liquidity needs
- Transaction costs
"""

    @staticmethod
    def community_management(
        issue: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get community management prompt"""
        return f"""Handle community interaction:

Issue: {issue}
Context: {context or {}}

Requirements:
1. Professional and empathetic response
2. Clear and accurate information
3. Constructive engagement
4. Solution-oriented approach
5. Follow-up actions if needed

Maintain community guidelines while building positive relationships.
"""

    @staticmethod
    def trade_execution(
        trade_params: Dict[str, Any],
        market_context: Dict[str, Any]
    ) -> str:
        """Get trade execution prompt"""
        return f"""Evaluate and execute trade:

Parameters:
{trade_params}

Market Context:
{market_context}

Analyze:
1. Entry/exit points
2. Position sizing
3. Risk management
4. Execution strategy
5. Post-trade monitoring

Provide clear execution plan with risk management rules.
"""

    @staticmethod
    def sentiment_analysis(text: str) -> str:
        """Get sentiment analysis prompt"""
        return f"""Analyze sentiment in this text:

Text: {text}

Provide:
1. Sentiment score (-1.0 to 1.0)
2. Confidence level (0.0 to 1.0)
3. Key sentiment drivers
4. Notable phrases/keywords

Format as JSON response.
"""

    @staticmethod
    def transaction_review(tx_data: Dict[str, Any]) -> str:
        """Get transaction review prompt"""
        return f"""Review transaction parameters:

Transaction:
{tx_data}

Verify:
1. Address accuracy
2. Amount reasonability
3. Fee estimation
4. Network conditions
5. Security checks

Provide verification status and recommendations.
"""
