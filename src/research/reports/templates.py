from typing import Dict, List
import jinja2

MARKET_REPORT_TEMPLATE = """
# Market Analysis Report
## {{ report_date }}

### Market Overview
- Current Market Cap: ${{ '{:,.2f}'.format(market_cap) }}
- 24h Volume: ${{ '{:,.2f}'.format(volume_24h) }}
- Market Sentiment: {{ sentiment }}

### Key Metrics
{% for metric in key_metrics %}
- {{ metric.name }}: {{ metric.value }}
{% endfor %}

### Market Trends
{% for trend in trends %}
#### {{ trend.name }}
- Direction: {{ trend.direction }}
- Strength: {{ trend.strength }}
- Duration: {{ trend.duration }}
{% endfor %}

### Opportunities
{% for opportunity in opportunities %}
- {{ opportunity }}
{% endfor %}

### Risks
{% for risk in risks %}
- {{ risk }}
{% endfor %}
"""

INVESTMENT_REPORT_TEMPLATE = """
# Investment Analysis Report
## {{ report_date }}

### Portfolio Performance
- Total Value: ${{ '{:,.2f}'.format(portfolio_value) }}
- Period Return: {{ '{:.2f}%'.format(period_return) }}
- Risk-Adjusted Return: {{ '{:.2f}'.format(risk_adjusted_return) }}

### Position Analysis
{% for position in positions %}
#### {{ position.token }}
- Allocation: {{ '{:.2f}%'.format(position.allocation) }}
- ROI: {{ '{:.2f}%'.format(position.roi) }}
- Risk Score: {{ position.risk_score }}
{% endfor %}

### Recommendations
{% for recommendation in recommendations %}
- {{ recommendation }}
{% endfor %}
"""


class TemplateManager:
    def __init__(self):
        self.env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        self.templates = {
            "market_report": self.env.from_string(MARKET_REPORT_TEMPLATE),
            "investment_report": self.env.from_string(INVESTMENT_REPORT_TEMPLATE),
        }

    def render_template(self, template_name: str, data: Dict) -> str:
        if template_name not in self.templates:
            raise ValueError(f"Template {template_name} not found")
        return self.templates[template_name].render(**data)
