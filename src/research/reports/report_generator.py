# src/research/reports/report_generator.py

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ReportConfig:
    """Configuration for report generator"""
    templates_path: Optional[str] = None
    storage_path: Optional[str] = None
    max_history: int = 100
    default_type: str = 'research_report'
    formatting: Dict[str, Any] = None

    def __post_init__(self):
        if self.formatting is None:
            self.formatting = {
                'indent': 2,
                'line_length': 80,
                'timestamp_format': '%Y-%m-%d %H:%M:%S'
            }

class ReportGenerator:
    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()
        self._initialized = False
        self.report_templates = {}
        self.report_history = []

    async def initialize(self) -> None:
        """Initialize the report generator"""
        try:
            # Load report templates
            await self._load_templates()
            
            # Initialize storage
            self._initialized = True
            logger.info("Report Generator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Report Generator: {e}")
            raise

    async def _load_templates(self) -> None:
        """Load report templates from configuration"""
        try:
            self.report_templates = {
                'market_analysis': """
                # Market Analysis Report
                ## Overview
                {overview}
                
                ## Key Metrics
                {metrics}
                
                ## Trends
                {trends}
                
                ## Recommendations
                {recommendations}
                """,
                'research_report': """
                # Research Report
                ## Executive Summary
                {summary}
                
                ## Analysis
                {analysis}
                
                ## Findings
                {findings}
                
                ## Conclusions
                {conclusions}
                """,
                'portfolio_report': """
                # Portfolio Report
                ## Performance Overview
                {performance}
                
                ## Holdings
                {holdings}
                
                ## Risk Analysis
                {risk_analysis}
                
                ## Recommendations
                {recommendations}
                """
            }
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            raise

    async def generate_report(self, data: Dict[str, Any], report_type: Optional[str] = None) -> Dict[str, Any]:
        """Generate a report from data"""
        if not self._initialized:
            raise RuntimeError("Report Generator not initialized")
            
        try:
            report_type = report_type or self.config.default_type
            template = self.report_templates.get(report_type)
            if not template:
                raise ValueError(f"Unknown report type: {report_type}")
                
            # Generate report content
            content = await self._generate_content(data, template)
            
            # Generate summary
            summary = await self._generate_summary(content)
            
            report = {
                'type': report_type,
                'timestamp': datetime.now().strftime(self.config.formatting['timestamp_format']),
                'content': content,
                'summary': summary,
                'metadata': {
                    'source_data': list(data.keys()),
                    'template_used': report_type
                }
            }
            
            # Store in history
            self.report_history.append({
                'timestamp': report['timestamp'],
                'type': report_type,
                'summary': summary
            })
            
            # Trim history if needed
            if len(self.report_history) > self.config.max_history:
                self.report_history = self.report_history[-self.config.max_history:]
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            raise

    async def _generate_content(self, data: Dict[str, Any], template: str) -> str:
        """Generate report content from template"""
        try:
            # Process data into template sections
            sections = {}
            for key in data:
                if isinstance(data[key], dict):
                    sections[key] = json.dumps(
                        data[key],
                        indent=self.config.formatting['indent']
                    )
                elif isinstance(data[key], list):
                    sections[key] = "\n".join(f"- {item}" for item in data[key])
                else:
                    sections[key] = str(data[key])
                    
            # Fill template
            content = template.format(**sections)
            return content
            
        except Exception as e:
            logger.error(f"Failed to generate content: {e}")
            raise

    async def _generate_summary(self, content: str) -> str:
        """Generate summary of report content"""
        try:
            # Split content into sections
            sections = content.split("\n## ")
            
            # Extract key points
            summary_points = []
            for section in sections:
                if section.strip():
                    lines = section.strip().split("\n")
                    if lines:
                        summary_points.append(lines[0])
                        
            # Combine into summary
            summary = "\n".join(f"- {point}" for point in summary_points)
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            raise

    async def get_report_history(self, limit: Optional[int] = None) -> list:
        """Get recent report history"""
        if not self._initialized:
            raise RuntimeError("Report Generator not initialized")
        
        limit = limit or self.config.max_history
        return self.report_history[-limit:]

    async def cleanup(self) -> None:
        """Cleanup report generator resources"""
        try:
            self.report_history.clear()
            self.report_templates.clear()
            self._initialized = False
            logger.info("Report Generator cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up Report Generator: {e}")

