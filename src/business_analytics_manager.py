"""
BusinessAnalyticsManager - Handles analytics and KPI tracking for Business Infinity
"""
from typing import Dict, Any
import logging

class BusinessAnalyticsManager:
    def __init__(self, analytics_engine, logger=None):
        self.analytics_engine = analytics_engine
        self.logger = logger or logging.getLogger(__name__)

    async def get_business_analytics(self) -> Dict[str, Any]:
        return await self.analytics_engine.generate_business_report()

    async def record_decision(self, decision_result: Dict[str, Any]):
        await self.analytics_engine.record_decision(decision_result)

    async def generate_performance_report(self):
        return await self.analytics_engine.generate_performance_report()
