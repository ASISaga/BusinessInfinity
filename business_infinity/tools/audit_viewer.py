"""
BusinessInfinity Tools - Audit Viewer

Tool for viewing and analyzing audit trail data from the AOS audit system.
This is business-specific tooling that uses the AOS audit infrastructure.
"""

import json
import asyncio
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

try:
    # Try to import from AOS
    from aos.monitoring.audit_trail import AuditTrailManager, AuditQuery, AuditEventType, AuditSeverity
    AOS_AVAILABLE = True
except ImportError:
    # Fallback for development/testing
    AOS_AVAILABLE = False
    print("Warning: AOS audit system not available")


class BusinessAuditViewer:
    """Business-focused audit trail viewer with business context"""
    
    def __init__(self, audit_manager=None):
        self.audit_manager = audit_manager or (AuditTrailManager() if AOS_AVAILABLE else None)
        
    async def view_business_decisions(self, start_date: Optional[datetime] = None, 
                                   end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """View business decision-related audit events"""
        if not self.audit_manager:
            return []
        
        query = AuditQuery(
            start_time=start_date,
            end_time=end_date,
            event_types=[
                AuditEventType.BOARDROOM_DECISION,
                AuditEventType.DECISION_INITIATED,
                AuditEventType.DECISION_COMPLETED
            ]
        )
        
        events = await self.audit_manager.query_events(query)
        
        # Format for business context
        business_events = []
        for event in events:
            business_event = {
                "timestamp": event.timestamp.isoformat(),
                "decision_type": event.event_type.value,
                "description": event.action,
                "agent": event.subject_id,
                "outcome": event.context.get("outcome", "unknown"),
                "metadata": event.metadata
            }
            business_events.append(business_event)
        
        return business_events
    
    async def view_agent_performance(self, agent_id: Optional[str] = None,
                                   days: int = 7) -> Dict[str, Any]:
        """View agent performance metrics from audit data"""
        if not self.audit_manager:
            return {}
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        query = AuditQuery(
            start_time=start_time,
            end_time=end_time,
            subject_ids=[agent_id] if agent_id else None,
            event_types=[
                AuditEventType.AGENT_ACTION,
                AuditEventType.AGENT_DECISION,
                AuditEventType.TASK_COMPLETED,
                AuditEventType.WORKFLOW_COMPLETED
            ]
        )
        
        events = await self.audit_manager.query_events(query)
        
        # Aggregate performance data
        agent_metrics = {}
        for event in events:
            agent = event.subject_id
            if agent not in agent_metrics:
                agent_metrics[agent] = {
                    "total_actions": 0,
                    "successful_tasks": 0,
                    "failed_tasks": 0,
                    "average_duration": 0.0,
                    "last_activity": None
                }
            
            agent_metrics[agent]["total_actions"] += 1
            if event.event_type == AuditEventType.TASK_COMPLETED:
                if event.context.get("success", False):
                    agent_metrics[agent]["successful_tasks"] += 1
                else:
                    agent_metrics[agent]["failed_tasks"] += 1
            
            if event.metrics.get("duration_seconds"):
                current_avg = agent_metrics[agent]["average_duration"]
                new_duration = event.metrics["duration_seconds"]
                agent_metrics[agent]["average_duration"] = (current_avg + new_duration) / 2
            
            if not agent_metrics[agent]["last_activity"] or event.timestamp > datetime.fromisoformat(agent_metrics[agent]["last_activity"]):
                agent_metrics[agent]["last_activity"] = event.timestamp.isoformat()
        
        return agent_metrics
    
    async def view_system_health(self, hours: int = 24) -> Dict[str, Any]:
        """View system health metrics from audit data"""
        if not self.audit_manager:
            return {}
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        query = AuditQuery(
            start_time=start_time,
            end_time=end_time,
            event_types=[
                AuditEventType.SYSTEM_ERROR,
                AuditEventType.COMPONENT_STARTED,
                AuditEventType.COMPONENT_STOPPED,
                AuditEventType.SYSTEM_STARTUP,
                AuditEventType.SYSTEM_SHUTDOWN
            ]
        )
        
        events = await self.audit_manager.query_events(query)
        
        # Analyze system health
        health_metrics = {
            "total_events": len(events),
            "error_count": 0,
            "startup_count": 0,
            "component_restarts": 0,
            "error_rate": 0.0,
            "components_status": {}
        }
        
        for event in events:
            if event.event_type == AuditEventType.SYSTEM_ERROR:
                health_metrics["error_count"] += 1
            elif event.event_type == AuditEventType.SYSTEM_STARTUP:
                health_metrics["startup_count"] += 1
            elif event.event_type == AuditEventType.COMPONENT_STARTED:
                component = event.component or "unknown"
                if component not in health_metrics["components_status"]:
                    health_metrics["components_status"][component] = {"starts": 0, "stops": 0}
                health_metrics["components_status"][component]["starts"] += 1
            elif event.event_type == AuditEventType.COMPONENT_STOPPED:
                component = event.component or "unknown"
                if component not in health_metrics["components_status"]:
                    health_metrics["components_status"][component] = {"starts": 0, "stops": 0}
                health_metrics["components_status"][component]["stops"] += 1
        
        # Calculate error rate
        if health_metrics["total_events"] > 0:
            health_metrics["error_rate"] = health_metrics["error_count"] / health_metrics["total_events"]
        
        return health_metrics
    
    async def generate_business_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive business audit report"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Collect different types of data
        decisions = await self.view_business_decisions(start_time, end_time)
        agent_performance = await self.view_agent_performance(days=days)
        system_health = await self.view_system_health(hours=days*24)
        
        return {
            "report_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "days": days
            },
            "business_decisions": {
                "total": len(decisions),
                "by_type": self._group_by_type(decisions),
                "recent": decisions[-5:] if decisions else []
            },
            "agent_performance": agent_performance,
            "system_health": system_health,
            "summary": {
                "total_decisions": len(decisions),
                "active_agents": len(agent_performance),
                "system_error_rate": system_health.get("error_rate", 0.0),
                "overall_health": "good" if system_health.get("error_rate", 0.0) < 0.1 else "warning"
            }
        }
    
    def _group_by_type(self, decisions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group decisions by type for summary"""
        type_counts = {}
        for decision in decisions:
            decision_type = decision.get("decision_type", "unknown")
            type_counts[decision_type] = type_counts.get(decision_type, 0) + 1
        return type_counts
    
    def format_report(self, report: Dict[str, Any]) -> str:
        """Format report for display"""
        output = []
        output.append("=" * 60)
        output.append("BUSINESS INFINITY AUDIT REPORT")
        output.append("=" * 60)
        
        # Report period
        period = report["report_period"]
        output.append(f"Period: {period['start']} to {period['end']} ({period['days']} days)")
        output.append("")
        
        # Summary
        summary = report["summary"]
        output.append("SUMMARY:")
        output.append(f"  Total Decisions: {summary['total_decisions']}")
        output.append(f"  Active Agents: {summary['active_agents']}")
        output.append(f"  System Error Rate: {summary['system_error_rate']:.2%}")
        output.append(f"  Overall Health: {summary['overall_health'].upper()}")
        output.append("")
        
        # Business decisions
        decisions = report["business_decisions"]
        output.append("BUSINESS DECISIONS:")
        output.append(f"  Total: {decisions['total']}")
        if decisions['by_type']:
            output.append("  By Type:")
            for decision_type, count in decisions['by_type'].items():
                output.append(f"    {decision_type}: {count}")
        output.append("")
        
        # Agent performance
        performance = report["agent_performance"]
        if performance:
            output.append("AGENT PERFORMANCE:")
            for agent_id, metrics in performance.items():
                success_rate = 0.0
                total_tasks = metrics['successful_tasks'] + metrics['failed_tasks']
                if total_tasks > 0:
                    success_rate = metrics['successful_tasks'] / total_tasks
                
                output.append(f"  {agent_id}:")
                output.append(f"    Actions: {metrics['total_actions']}")
                output.append(f"    Success Rate: {success_rate:.2%}")
                output.append(f"    Avg Duration: {metrics['average_duration']:.2f}s")
                output.append(f"    Last Activity: {metrics['last_activity']}")
                output.append("")
        
        return "\n".join(output)


async def main():
    """Command line interface for audit viewer"""
    parser = argparse.ArgumentParser(description="BusinessInfinity Audit Viewer")
    parser.add_argument("--command", choices=["decisions", "performance", "health", "report"], 
                       default="report", help="Command to execute")
    parser.add_argument("--agent", help="Specific agent ID for performance view")
    parser.add_argument("--days", type=int, default=7, help="Number of days to analyze")
    parser.add_argument("--hours", type=int, default=24, help="Number of hours for health check")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    if not AOS_AVAILABLE:
        print("Error: AOS audit system not available")
        return
    
    viewer = BusinessAuditViewer()
    
    try:
        if args.command == "decisions":
            end_time = datetime.now()
            start_time = end_time - timedelta(days=args.days)
            result = await viewer.view_business_decisions(start_time, end_time)
        
        elif args.command == "performance":
            result = await viewer.view_agent_performance(args.agent, args.days)
        
        elif args.command == "health":
            result = await viewer.view_system_health(args.hours)
        
        elif args.command == "report":
            result = await viewer.generate_business_report(args.days)
            if args.format == "text":
                print(viewer.format_report(result))
                return
        
        # Output result
        if args.format == "json":
            print(json.dumps(result, indent=2, default=str))
        else:
            print(json.dumps(result, indent=2, default=str))
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())