"""
Business Analytics Manager

Manages business analytics, KPIs, and performance metrics
using the AOS monitoring and ML infrastructure.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from AgentOperatingSystem import AgentOperatingSystem
from AgentOperatingSystem.monitoring import SystemMonitor
from core.config import BusinessInfinityConfig

# Create placeholder class for monitoring
class SystemMonitor:
    def __init__(self):
        pass
    async def get_metrics(self):
        return {
            "uptime_percentage": 99.5,
            "avg_response_time_ms": 150,
            "error_rate_percentage": 0.05
        }

class MetricType(Enum):
    """Types of business metrics."""
    FINANCIAL = "financial"
    OPERATIONAL = "operational" 
    CUSTOMER = "customer"
    EMPLOYEE = "employee"
    TECHNOLOGY = "technology"
    STRATEGIC = "strategic"


class BusinessMetric:
    """Business metric definition and tracking."""
    
    def __init__(self, 
                 metric_id: str,
                 name: str,
                 metric_type: MetricType,
                 unit: str,
                 target_value: float,
                 description: str = None):
        self.metric_id = metric_id
        self.name = name
        self.metric_type = metric_type
        self.unit = unit
        self.target_value = target_value
        self.description = description
        self.current_value = 0.0
        self.historical_values = []
        self.last_updated = None

    def update_value(self, value: float, timestamp: datetime = None):
        """Update metric value."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        self.current_value = value
        self.historical_values.append({
            "value": value,
            "timestamp": timestamp
        })
        self.last_updated = timestamp

    def get_trend(self, days: int = 30) -> str:
        """Get trend over specified number of days."""
        if len(self.historical_values) < 2:
            return "insufficient_data"
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_values = [
            entry for entry in self.historical_values
            if entry["timestamp"] >= cutoff_date
        ]
        
        if len(recent_values) < 2:
            return "insufficient_data"
        
        first_value = recent_values[0]["value"]
        last_value = recent_values[-1]["value"]
        
        if last_value > first_value * 1.05:
            return "increasing"
        elif last_value < first_value * 0.95:
            return "decreasing"
        else:
            return "stable"

    def get_performance_status(self) -> str:
        """Get performance status relative to target."""
        if self.current_value >= self.target_value * 0.95:
            return "excellent"
        elif self.current_value >= self.target_value * 0.85:
            return "good"
        elif self.current_value >= self.target_value * 0.70:
            return "fair"
        else:
            return "poor"


class BusinessAnalyticsManager:
    """
    Manages business analytics and performance metrics using AOS infrastructure.
    
    Provides:
    - KPI tracking and monitoring
    - Performance analytics
    - Business intelligence dashboards
    - Predictive analytics
    """
    
    def __init__(self, aos: AgentOperatingSystem, config: BusinessInfinityConfig, logger: logging.Logger):
        """Initialize Business Analytics Manager."""
        self.aos = aos
        self.config = config
        self.logger = logger
        
        # Metrics registry
        self.metrics: Dict[str, BusinessMetric] = {}
        self.metric_categories: Dict[MetricType, List[str]] = {}
        
        # Analytics data
        self.kpi_dashboard = {}
        self.performance_summaries = {}
        self.analytics_reports = {}
        
        # Background tasks
        self._collection_task = None
        self._analysis_task = None

    async def initialize(self):
        """Initialize analytics manager."""
        try:
            self.logger.info("Initializing Business Analytics Manager...")
            
            # Initialize business metrics
            await self._initialize_business_metrics()
            
            # Ensure AOS has required system monitor
            if not hasattr(self.aos, 'system_monitor'):
                self.aos.system_monitor = SystemMonitor()
            
            # Set up metric categories
            await self._setup_metric_categories()
            
            # Start background tasks
            if self.config.analytics_config.get("collection_enabled", True):
                self._collection_task = asyncio.create_task(self._collection_loop())
                self._analysis_task = asyncio.create_task(self._analysis_loop())
            
            self.logger.info("Business Analytics Manager initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Business Analytics Manager: {e}")
            raise

    async def _initialize_business_metrics(self):
        """Initialize core business metrics."""
        
        # Financial Metrics
        financial_metrics = [
            BusinessMetric("revenue_growth", "Revenue Growth", MetricType.FINANCIAL, "percentage", 20.0, "Year-over-year revenue growth"),
            BusinessMetric("profit_margin", "Profit Margin", MetricType.FINANCIAL, "percentage", 25.0, "Net profit margin"),
            BusinessMetric("customer_acquisition_cost", "Customer Acquisition Cost", MetricType.FINANCIAL, "dollars", 100.0, "Cost to acquire new customer"),
            BusinessMetric("customer_lifetime_value", "Customer Lifetime Value", MetricType.FINANCIAL, "dollars", 1000.0, "Average customer lifetime value")
        ]
        
        # Operational Metrics
        operational_metrics = [
            BusinessMetric("system_uptime", "System Uptime", MetricType.OPERATIONAL, "percentage", 99.9, "System availability percentage"),
            BusinessMetric("response_time", "Average Response Time", MetricType.OPERATIONAL, "milliseconds", 200.0, "Average API response time"),
            BusinessMetric("error_rate", "Error Rate", MetricType.OPERATIONAL, "percentage", 0.1, "System error rate"),
            BusinessMetric("deployment_frequency", "Deployment Frequency", MetricType.OPERATIONAL, "per_week", 10.0, "Number of deployments per week")
        ]
        
        # Customer Metrics
        customer_metrics = [
            BusinessMetric("customer_satisfaction", "Customer Satisfaction", MetricType.CUSTOMER, "score", 8.5, "Customer satisfaction score (1-10)"),
            BusinessMetric("net_promoter_score", "Net Promoter Score", MetricType.CUSTOMER, "score", 50.0, "Net Promoter Score"),
            BusinessMetric("customer_retention", "Customer Retention", MetricType.CUSTOMER, "percentage", 90.0, "Customer retention rate"),
            BusinessMetric("monthly_active_users", "Monthly Active Users", MetricType.CUSTOMER, "count", 10000.0, "Number of monthly active users")
        ]
        
        # Employee Metrics
        employee_metrics = [
            BusinessMetric("employee_satisfaction", "Employee Satisfaction", MetricType.EMPLOYEE, "score", 8.0, "Employee satisfaction score (1-10)"),
            BusinessMetric("employee_retention", "Employee Retention", MetricType.EMPLOYEE, "percentage", 90.0, "Employee retention rate"),
            BusinessMetric("productivity_score", "Productivity Score", MetricType.EMPLOYEE, "score", 85.0, "Overall productivity score"),
            BusinessMetric("innovation_index", "Innovation Index", MetricType.EMPLOYEE, "score", 75.0, "Innovation and creativity index")
        ]
        
        # Technology Metrics
        technology_metrics = [
            BusinessMetric("technical_debt_ratio", "Technical Debt Ratio", MetricType.TECHNOLOGY, "percentage", 15.0, "Technical debt as percentage of codebase"),
            BusinessMetric("code_quality_score", "Code Quality Score", MetricType.TECHNOLOGY, "score", 85.0, "Overall code quality score"),
            BusinessMetric("security_score", "Security Score", MetricType.TECHNOLOGY, "score", 90.0, "Security posture score"),
            BusinessMetric("innovation_pipeline", "Innovation Pipeline", MetricType.TECHNOLOGY, "count", 5.0, "Number of active innovation projects")
        ]
        
        # Strategic Metrics
        strategic_metrics = [
            BusinessMetric("market_share", "Market Share", MetricType.STRATEGIC, "percentage", 15.0, "Market share percentage"),
            BusinessMetric("brand_awareness", "Brand Awareness", MetricType.STRATEGIC, "percentage", 60.0, "Brand awareness percentage"),
            BusinessMetric("strategic_goal_achievement", "Strategic Goal Achievement", MetricType.STRATEGIC, "percentage", 85.0, "Strategic goal achievement rate"),
            BusinessMetric("competitive_advantage", "Competitive Advantage", MetricType.STRATEGIC, "score", 80.0, "Competitive advantage score")
        ]
        
        # Register all metrics
        all_metrics = financial_metrics + operational_metrics + customer_metrics + employee_metrics + technology_metrics + strategic_metrics
        
        for metric in all_metrics:
            self.metrics[metric.metric_id] = metric

    async def _setup_metric_categories(self):
        """Set up metric categories."""
        for metric_id, metric in self.metrics.items():
            if metric.metric_type not in self.metric_categories:
                self.metric_categories[metric.metric_type] = []
            self.metric_categories[metric.metric_type].append(metric_id)

    async def _collection_loop(self):
        """Background metrics collection loop."""
        collection_interval = self.config.analytics_config.get("collection_interval", 300)
        
        while True:
            try:
                await self.collect_performance_metrics()
                await asyncio.sleep(collection_interval)
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)

    async def _analysis_loop(self):
        """Background analytics analysis loop."""
        while True:
            try:
                await self._generate_analytics_insights()
                await asyncio.sleep(1800)  # Every 30 minutes
            except Exception as e:
                self.logger.error(f"Analytics analysis error: {e}")
                await asyncio.sleep(300)

    async def collect_performance_metrics(self):
        """Collect performance metrics from various sources."""
        try:
            # Collect system metrics from AOS
            system_metrics = await self.aos.system_monitor.get_metrics()
            
            # Update operational metrics
            await self._update_operational_metrics(system_metrics)
            
            # Collect agent performance metrics
            await self._collect_agent_metrics()
            
            # Collect business-specific metrics
            await self._collect_business_metrics()
            
            self.logger.debug("Performance metrics collected successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to collect performance metrics: {e}")

    async def _update_operational_metrics(self, system_metrics: Dict[str, Any]):
        """Update operational metrics from system data."""
        # Update system uptime
        if "uptime_percentage" in system_metrics:
            await self.update_metric("system_uptime", system_metrics["uptime_percentage"])
        
        # Update response time
        if "avg_response_time_ms" in system_metrics:
            await self.update_metric("response_time", system_metrics["avg_response_time_ms"])
        
        # Update error rate
        if "error_rate_percentage" in system_metrics:
            await self.update_metric("error_rate", system_metrics["error_rate_percentage"])

    async def _collect_agent_metrics(self):
        """Collect metrics from business agents."""
        # This would collect metrics from agents
        # For now, simulating with sample data
        await self.update_metric("productivity_score", 87.5)
        await self.update_metric("innovation_index", 78.2)

    async def _collect_business_metrics(self):
        """Collect business-specific metrics."""
        # This would integrate with external systems to collect real business metrics
        # For now, simulating with sample data
        await self.update_metric("customer_satisfaction", 8.7)
        await self.update_metric("employee_satisfaction", 8.2)
        await self.update_metric("revenue_growth", 18.5)

    async def _generate_analytics_insights(self):
        """Generate analytics insights and reports."""
        try:
            # Generate KPI dashboard
            self.kpi_dashboard = await self._generate_kpi_dashboard()
            
            # Generate performance summaries
            self.performance_summaries = await self._generate_performance_summaries()
            
            # Generate trend analysis
            trend_analysis = await self._generate_trend_analysis()
            
            # Store analytics report
            analytics_report = {
                "timestamp": datetime.utcnow().isoformat(),
                "kpi_dashboard": self.kpi_dashboard,
                "performance_summaries": self.performance_summaries,
                "trend_analysis": trend_analysis,
                "insights": await self._generate_insights()
            }
            
            self.analytics_reports[datetime.utcnow().strftime("%Y%m%d_%H%M")] = analytics_report
            
        except Exception as e:
            self.logger.error(f"Failed to generate analytics insights: {e}")

    async def _generate_kpi_dashboard(self) -> Dict[str, Any]:
        """Generate KPI dashboard data."""
        dashboard = {}
        
        for category, metric_ids in self.metric_categories.items():
            dashboard[category.value] = {
                "metrics": [],
                "overall_performance": "good",
                "alerts": []
            }
            
            for metric_id in metric_ids:
                metric = self.metrics[metric_id]
                metric_data = {
                    "id": metric.metric_id,
                    "name": metric.name,
                    "current_value": metric.current_value,
                    "target_value": metric.target_value,
                    "unit": metric.unit,
                    "performance_status": metric.get_performance_status(),
                    "trend": metric.get_trend(),
                    "last_updated": metric.last_updated.isoformat() if metric.last_updated else None
                }
                dashboard[category.value]["metrics"].append(metric_data)
                
                # Add alerts for poor performance
                if metric.get_performance_status() == "poor":
                    dashboard[category.value]["alerts"].append({
                        "metric": metric.name,
                        "message": f"{metric.name} is below target ({metric.current_value} vs {metric.target_value})",
                        "severity": "high"
                    })
        
        return dashboard

    async def _generate_performance_summaries(self) -> Dict[str, Any]:
        """Generate performance summaries by category."""
        summaries = {}
        
        for category, metric_ids in self.metric_categories.items():
            category_metrics = [self.metrics[mid] for mid in metric_ids]
            
            # Calculate category performance
            performance_scores = [
                self._calculate_performance_score(metric)
                for metric in category_metrics
            ]
            
            avg_performance = sum(performance_scores) / len(performance_scores) if performance_scores else 0
            
            summaries[category.value] = {
                "metrics_count": len(category_metrics),
                "average_performance": avg_performance,
                "performance_grade": self._get_performance_grade(avg_performance),
                "top_performers": [
                    {"name": m.name, "score": self._calculate_performance_score(m)}
                    for m in sorted(category_metrics, key=self._calculate_performance_score, reverse=True)[:3]
                ],
                "areas_for_improvement": [
                    {"name": m.name, "score": self._calculate_performance_score(m)}
                    for m in sorted(category_metrics, key=self._calculate_performance_score)[:3]
                ]
            }
        
        return summaries

    async def _generate_trend_analysis(self) -> Dict[str, Any]:
        """Generate trend analysis."""
        trends = {}
        
        for metric_id, metric in self.metrics.items():
            trend = metric.get_trend()
            if trend not in trends:
                trends[trend] = []
            trends[trend].append({
                "metric": metric.name,
                "category": metric.metric_type.value,
                "current_value": metric.current_value,
                "target_value": metric.target_value
            })
        
        return trends

    async def _generate_insights(self) -> List[Dict[str, Any]]:
        """Generate business insights from metrics."""
        insights = []
        
        # Identify strong performers
        strong_performers = [
            metric for metric in self.metrics.values()
            if metric.get_performance_status() in ["excellent", "good"] and metric.get_trend() == "increasing"
        ]
        
        if strong_performers:
            insights.append({
                "type": "positive",
                "title": "Strong Performance Areas",
                "message": f"{len(strong_performers)} metrics showing excellent performance and positive trends",
                "details": [{"metric": m.name, "performance": m.get_performance_status()} for m in strong_performers[:5]]
            })
        
        # Identify areas needing attention
        underperformers = [
            metric for metric in self.metrics.values()
            if metric.get_performance_status() == "poor"
        ]
        
        if underperformers:
            insights.append({
                "type": "warning",
                "title": "Areas Requiring Attention",
                "message": f"{len(underperformers)} metrics below target performance",
                "details": [{"metric": m.name, "current": m.current_value, "target": m.target_value} for m in underperformers]
            })
        
        return insights

    def _calculate_performance_score(self, metric: BusinessMetric) -> float:
        """Calculate performance score for a metric."""
        if metric.target_value == 0:
            return 1.0
        
        ratio = metric.current_value / metric.target_value
        return min(1.0, max(0.0, ratio))

    def _get_performance_grade(self, score: float) -> str:
        """Get performance grade from score."""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"

    async def update_metric(self, metric_id: str, value: float, timestamp: datetime = None):
        """Update a metric value."""
        if metric_id in self.metrics:
            self.metrics[metric_id].update_value(value, timestamp)
            self.logger.debug(f"Updated metric {metric_id}: {value}")
        else:
            self.logger.warning(f"Unknown metric ID: {metric_id}")

    async def get_business_analytics(self) -> Dict[str, Any]:
        """Get comprehensive business analytics."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "kpi_dashboard": self.kpi_dashboard,
            "performance_summaries": self.performance_summaries,
            "metrics_overview": {
                "total_metrics": len(self.metrics),
                "categories": list(self.metric_categories.keys()),
                "last_collection": datetime.utcnow().isoformat()
            },
            "recent_insights": await self._generate_insights()
        }

    async def get_summary(self) -> Dict[str, Any]:
        """Get analytics summary."""
        return {
            "metrics_tracked": len(self.metrics),
            "categories": len(self.metric_categories),
            "reports_generated": len(self.analytics_reports),
            "last_collection": datetime.utcnow().isoformat(),
            "overall_health": "good"  # This would be calculated from metrics
        }

    async def get_metric_details(self, metric_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific metric."""
        if metric_id not in self.metrics:
            return None
        
        metric = self.metrics[metric_id]
        return {
            "metric_id": metric.metric_id,
            "name": metric.name,
            "type": metric.metric_type.value,
            "unit": metric.unit,
            "description": metric.description,
            "current_value": metric.current_value,
            "target_value": metric.target_value,
            "performance_status": metric.get_performance_status(),
            "trend": metric.get_trend(),
            "last_updated": metric.last_updated.isoformat() if metric.last_updated else None,
            "historical_data": metric.historical_values[-30:] if len(metric.historical_values) > 30 else metric.historical_values
        }

    async def shutdown(self):
        """Shutdown analytics manager."""
        try:
            self.logger.info("Shutting down Business Analytics Manager...")
            
            # Cancel background tasks
            if self._collection_task:
                self._collection_task.cancel()
            if self._analysis_task:
                self._analysis_task.cancel()
            
            self.logger.info("Business Analytics Manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during analytics manager shutdown: {e}")
            raise