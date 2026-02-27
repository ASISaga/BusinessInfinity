"""
Business Analytics Engine

This module provides business analytics, KPI tracking, and performance
monitoring for Business Infinity. It integrates with AOS storage to
maintain business metrics and generate insights.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class MetricType(Enum):
    """Types of business metrics"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    CUSTOMER = "customer"
    STRATEGIC = "strategic"
    PERFORMANCE = "performance"


@dataclass
class BusinessMetric:
    """Business metric data structure"""
    name: str
    value: float
    unit: str
    metric_type: MetricType
    timestamp: datetime
    target: Optional[float] = None
    trend: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class BusinessAnalyticsEngine:
    """
    Business Analytics Engine for KPIs, metrics, and performance tracking
    
    Provides:
    - KPI definition and tracking
    - Performance metrics calculation
    - Business intelligence reporting
    - Trend analysis and forecasting
    - Decision impact analysis
    """
    
    def __init__(self, storage_manager, config):
        self.storage_manager = storage_manager
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self.metrics_store = {}
        self.kpis = {}
        self.performance_history = []
        self.decision_outcomes = []
        
        # Initialize standard KPIs
        self._initialize_standard_kpis()
    
    def _initialize_standard_kpis(self):
        """Initialize standard business KPIs"""
        standard_kpis = {
            # Financial KPIs
            "revenue_growth": {
                "name": "Revenue Growth Rate",
                "type": MetricType.FINANCIAL,
                "unit": "percent",
                "target": 20.0,
                "description": "Year-over-year revenue growth percentage"
            },
            "profit_margin": {
                "name": "Profit Margin",
                "type": MetricType.FINANCIAL,
                "unit": "percent",
                "target": 15.0,
                "description": "Net profit margin percentage"
            },
            "burn_rate": {
                "name": "Monthly Burn Rate",
                "type": MetricType.FINANCIAL,
                "unit": "currency",
                "target": 50000.0,
                "description": "Monthly cash consumption rate"
            },
            
            # Operational KPIs
            "productivity_index": {
                "name": "Team Productivity Index",
                "type": MetricType.OPERATIONAL,
                "unit": "index",
                "target": 85.0,
                "description": "Overall team productivity score"
            },
            "process_efficiency": {
                "name": "Process Efficiency",
                "type": MetricType.OPERATIONAL,
                "unit": "percent",
                "target": 90.0,
                "description": "Operational process efficiency percentage"
            },
            
            # Customer KPIs
            "customer_acquisition_cost": {
                "name": "Customer Acquisition Cost",
                "type": MetricType.CUSTOMER,
                "unit": "currency",
                "target": 100.0,
                "description": "Average cost to acquire a new customer"
            },
            "customer_lifetime_value": {
                "name": "Customer Lifetime Value",
                "type": MetricType.CUSTOMER,
                "unit": "currency",
                "target": 1000.0,
                "description": "Average customer lifetime value"
            },
            "customer_satisfaction": {
                "name": "Customer Satisfaction Score",
                "type": MetricType.CUSTOMER,
                "unit": "score",
                "target": 85.0,
                "description": "Customer satisfaction score out of 100"
            },
            
            # Strategic KPIs
            "market_share": {
                "name": "Market Share",
                "type": MetricType.STRATEGIC,
                "unit": "percent",
                "target": 10.0,
                "description": "Market share percentage in target market"
            },
            "innovation_index": {
                "name": "Innovation Index",
                "type": MetricType.STRATEGIC,
                "unit": "index",
                "target": 80.0,
                "description": "Innovation capability and output index"
            }
        }
        
        self.kpis = standard_kpis
    
    async def record_metric(self, name: str, value: float, unit: str, 
                          metric_type: MetricType, context: Dict[str, Any] = None) -> bool:
        """
        Record a business metric value
        
        Args:
            name: Metric name
            value: Metric value
            unit: Unit of measurement
            metric_type: Type of metric
            context: Optional context information
            
        Returns:
            bool: Success status
        """
        try:
            metric = BusinessMetric(
                name=name,
                value=value,
                unit=unit,
                metric_type=metric_type,
                timestamp=datetime.utcnow(),
                context=context
            )
            
            # Add target if this is a known KPI
            if name in self.kpis:
                metric.target = self.kpis[name].get("target")
            
            # Store metric
            if name not in self.metrics_store:
                self.metrics_store[name] = []
            
            self.metrics_store[name].append(metric)
            
            # Calculate trend if we have historical data
            if len(self.metrics_store[name]) > 1:
                metric.trend = self._calculate_trend(self.metrics_store[name][-2:])
            
            # Persist to storage
            await self._persist_metric(metric)
            
            self.logger.info(f"Recorded metric: {name} = {value} {unit}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record metric {name}: {e}")
            return False
    
    async def record_decision(self, decision_result: Dict[str, Any]) -> bool:
        """
        Record a business decision and its context for future analysis
        
        Args:
            decision_result: Decision result from workflow engine
            
        Returns:
            bool: Success status
        """
        try:
            decision_record = {
                "id": decision_result.get("id"),
                "status": decision_result.get("status"),
                "decision": decision_result.get("decision"),
                "confidence": decision_result.get("confidence", 0.0),
                "participants": decision_result.get("participating_agents", []),
                "timestamp": decision_result.get("timestamp"),
                "context": decision_result.get("context", {}),
                "outcome": None,  # To be updated later
                "impact_metrics": {}  # To be populated with actual impact
            }
            
            self.decision_outcomes.append(decision_record)
            
            # Persist decision record
            await self._persist_decision(decision_record)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record decision: {e}")
            return False
    
    async def generate_business_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive business analytics report
        
        Returns:
            Dict containing business analytics and insights
        """
        try:
            report = {
                "report_date": datetime.utcnow().isoformat(),
                "company_info": {
                    "name": self.config.company_name,
                    "industry": self.config.industry,
                    "stage": self.config.business_stage
                },
                "kpi_dashboard": await self._generate_kpi_dashboard(),
                "performance_trends": await self._generate_performance_trends(),
                "decision_analysis": await self._generate_decision_analysis(),
                "insights": await self._generate_business_insights(),
                "recommendations": await self._generate_recommendations()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate business report: {e}")
            return {"error": str(e)}
    
    async def generate_performance_report(self) -> Dict[str, Any]:
        """
        Generate focused performance report
        
        Returns:
            Dict containing performance metrics and analysis
        """
        try:
            # Calculate performance scores for each category
            financial_score = await self._calculate_category_score(MetricType.FINANCIAL)
            operational_score = await self._calculate_category_score(MetricType.OPERATIONAL)
            customer_score = await self._calculate_category_score(MetricType.CUSTOMER)
            strategic_score = await self._calculate_category_score(MetricType.STRATEGIC)
            
            # Overall performance score
            overall_score = (financial_score + operational_score + customer_score + strategic_score) / 4
            
            report = {
                "report_date": datetime.utcnow().isoformat(),
                "overall_performance": {
                    "score": overall_score,
                    "grade": self._score_to_grade(overall_score),
                    "trend": "improving"  # TODO: Calculate actual trend
                },
                "category_scores": {
                    "financial": financial_score,
                    "operational": operational_score,
                    "customer": customer_score,
                    "strategic": strategic_score
                },
                "top_performers": await self._get_top_performing_metrics(),
                "areas_for_improvement": await self._get_improvement_areas(),
                "action_items": await self._generate_action_items()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance report: {e}")
            return {"error": str(e)}
    
    async def _generate_kpi_dashboard(self) -> Dict[str, Any]:
        """Generate KPI dashboard data"""
        dashboard = {}
        
        for kpi_name, kpi_config in self.kpis.items():
            if kpi_name in self.metrics_store:
                latest_metric = self.metrics_store[kpi_name][-1]
                dashboard[kpi_name] = {
                    "name": kpi_config["name"],
                    "current_value": latest_metric.value,
                    "target": kpi_config.get("target"),
                    "unit": kpi_config["unit"],
                    "trend": latest_metric.trend,
                    "performance": self._calculate_kpi_performance(latest_metric, kpi_config),
                    "last_updated": latest_metric.timestamp.isoformat()
                }
        
        return dashboard
    
    async def _generate_performance_trends(self) -> Dict[str, Any]:
        """Generate performance trends analysis"""
        trends = {}
        
        for metric_name, metrics_list in self.metrics_store.items():
            if len(metrics_list) >= 2:
                # Calculate trend over last 30 days
                recent_metrics = [m for m in metrics_list 
                                if m.timestamp >= datetime.utcnow() - timedelta(days=30)]
                
                if recent_metrics:
                    trends[metric_name] = {
                        "direction": self._calculate_trend_direction(recent_metrics),
                        "change_rate": self._calculate_change_rate(recent_metrics),
                        "volatility": self._calculate_volatility(recent_metrics)
                    }
        
        return trends
    
    async def _generate_decision_analysis(self) -> Dict[str, Any]:
        """Generate decision analysis"""
        if not self.decision_outcomes:
            return {"total_decisions": 0, "analysis": "No decisions recorded yet"}
        
        total_decisions = len(self.decision_outcomes)
        approved_decisions = sum(1 for d in self.decision_outcomes if d["status"] == "approved")
        avg_confidence = sum(d.get("confidence", 0) for d in self.decision_outcomes) / total_decisions
        
        return {
            "total_decisions": total_decisions,
            "approval_rate": approved_decisions / total_decisions,
            "average_confidence": avg_confidence,
            "decision_quality_trend": "stable"  # TODO: Calculate actual trend
        }
    
    async def _generate_business_insights(self) -> List[str]:
        """Generate business insights based on current data"""
        insights = []
        
        # Sample insights - in production, these would be ML/AI generated
        insights.append("Revenue growth is tracking above target, indicating strong market demand")
        insights.append("Customer acquisition costs are rising, consider optimizing marketing channels")
        insights.append("Operational efficiency has room for improvement through process automation")
        
        return insights
    
    async def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable business recommendations"""
        recommendations = []
        
        # Sample recommendations - in production, these would be AI/ML generated
        recommendations.append({
            "category": "Financial",
            "priority": "High",
            "recommendation": "Focus on improving profit margins through cost optimization",
            "expected_impact": "5-10% margin improvement"
        })
        
        recommendations.append({
            "category": "Customer",
            "priority": "Medium", 
            "recommendation": "Implement customer success program to improve retention",
            "expected_impact": "15% improvement in customer lifetime value"
        })
        
        return recommendations
    
    def _calculate_trend(self, metrics: List[BusinessMetric]) -> str:
        """Calculate trend direction from recent metrics"""
        if len(metrics) < 2:
            return "stable"
        
        current = metrics[-1].value
        previous = metrics[-2].value
        
        if current > previous * 1.05:  # 5% threshold
            return "increasing"
        elif current < previous * 0.95:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_kpi_performance(self, metric: BusinessMetric, kpi_config: Dict[str, Any]) -> str:
        """Calculate KPI performance vs target"""
        target = kpi_config.get("target")
        if not target:
            return "no_target"
        
        performance_ratio = metric.value / target
        
        if performance_ratio >= 1.0:
            return "exceeding"
        elif performance_ratio >= 0.9:
            return "meeting"
        elif performance_ratio >= 0.75:
            return "approaching"
        else:
            return "below"
    
    async def _calculate_category_score(self, category: MetricType) -> float:
        """Calculate performance score for a metric category"""
        category_metrics = []
        
        for kpi_name, kpi_config in self.kpis.items():
            if kpi_config["type"] == category and kpi_name in self.metrics_store:
                latest_metric = self.metrics_store[kpi_name][-1]
                target = kpi_config.get("target")
                
                if target:
                    score = min(latest_metric.value / target * 100, 100)
                    category_metrics.append(score)
        
        return sum(category_metrics) / len(category_metrics) if category_metrics else 50.0
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _calculate_trend_direction(self, metrics: List[BusinessMetric]) -> str:
        """Calculate overall trend direction"""
        if len(metrics) < 2:
            return "stable"
        
        values = [m.value for m in metrics]
        slope = (values[-1] - values[0]) / len(values)
        
        if slope > 0:
            return "upward"
        elif slope < 0:
            return "downward"
        else:
            return "stable"
    
    def _calculate_change_rate(self, metrics: List[BusinessMetric]) -> float:
        """Calculate rate of change"""
        if len(metrics) < 2:
            return 0.0
        
        return (metrics[-1].value - metrics[0].value) / metrics[0].value
    
    def _calculate_volatility(self, metrics: List[BusinessMetric]) -> float:
        """Calculate metric volatility"""
        if len(metrics) < 2:
            return 0.0
        
        values = [m.value for m in metrics]
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        
        return variance ** 0.5 / mean if mean != 0 else 0.0
    
    async def _get_top_performing_metrics(self) -> List[str]:
        """Get list of top performing metrics"""
        # Simplified implementation
        return ["revenue_growth", "customer_satisfaction", "innovation_index"]
    
    async def _get_improvement_areas(self) -> List[str]:
        """Get areas that need improvement"""
        # Simplified implementation
        return ["customer_acquisition_cost", "process_efficiency", "burn_rate"]
    
    async def _generate_action_items(self) -> List[Dict[str, Any]]:
        """Generate actionable improvement items"""
        return [
            {
                "item": "Optimize marketing spend to reduce customer acquisition cost",
                "owner": "CMO",
                "timeline": "30 days",
                "priority": "High"
            },
            {
                "item": "Implement process automation to improve operational efficiency", 
                "owner": "COO",
                "timeline": "60 days",
                "priority": "Medium"
            }
        ]
    
    async def _persist_metric(self, metric: BusinessMetric):
        """Persist metric to AOS storage"""
        # TODO: Implement persistence using AOS storage manager
        pass
    
    async def _persist_decision(self, decision_record: Dict[str, Any]):
        """Persist decision record to AOS storage"""
        # TODO: Implement persistence using AOS storage manager
        pass