############################################################
# BusinessInfinity Tools - Audit Viewer (from audit_viewer1.py)
############################################################

import asyncio
from typing import Dict, Any, List, Optional

try:
    # Try to import from AOS
    from aos.monitoring.audit_trail import AuditTrailManager, AuditQuery, AuditEventType, AuditSeverity
    AOS_AVAILABLE = True
except ImportError:
    # Fallback for development/testing
    AOS_AVAILABLE = False
    print("Warning: AOS audit system not available")

import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.audit_trail import (
    AuditTrailManager, AuditEventType, AuditSeverity, AuditQuery, 
    get_audit_manager
)

try:
    from aos.monitoring.audit_trail import AuditTrailManager as AOSAuditTrailManager, AuditQuery as AOSAuditQuery, AuditEventType as AOSAuditEventType, AuditSeverity as AOSAuditSeverity
    AOS_AVAILABLE = True
except ImportError:
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


async def business_audit_main():
    """Command line interface for BusinessAuditViewer (from audit_viewer1.py)"""
    import argparse
    parser = argparse.ArgumentParser(description="BusinessInfinity Audit Viewer (BusinessAuditViewer)")
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

# End of audit_viewer1.py merge

"""
Audit Trail Viewer and Reporting Tool

Provides tools to view, query, and analyze audit trail data from the Business Infinity system.
Supports various export formats and compliance reporting.
"""



def format_event_summary(event) -> str:
    """Format an audit event for summary display"""
    timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} | {event.event_type.value:20} | {event.severity.value:8} | {event.subject_id:15} | {event.action[:60]}"


def print_event_details(event) -> None:
    """Print detailed information about an audit event"""
    print(f"\n{'='*80}")
    print(f"Event ID: {event.event_id}")
    print(f"Timestamp: {event.timestamp}")
    print(f"Event Type: {event.event_type.value}")
    print(f"Severity: {event.severity.value}")
    print(f"Subject: {event.subject_id} ({event.subject_type})")
    if event.subject_role:
        print(f"Role: {event.subject_role}")
    print(f"Action: {event.action}")
    
    if event.target:
        print(f"Target: {event.target}")
    if event.mcp_server:
        print(f"MCP Server: {event.mcp_server}")
    if event.rationale:
        print(f"Rationale: {event.rationale}")
    
    if event.evidence:
        print(f"Evidence:")
        for i, evidence in enumerate(event.evidence, 1):
            print(f"  {i}. {evidence}")
    
    if event.context:
        print(f"Context:")
        for key, value in event.context.items():
            print(f"  {key}: {value}")
    
    if event.metrics:
        print(f"Metrics:")
        for key, value in event.metrics.items():
            print(f"  {key}: {value}")
    
    if event.compliance_tags:
        print(f"Compliance Tags: {', '.join(event.compliance_tags)}")
    
    if event.retention_until:
        print(f"Retention Until: {event.retention_until}")
    
    print(f"Integrity Valid: {event.verify_integrity()}")
    print(f"{'='*80}")


def view_recent_events(hours: int = 24, limit: int = 50):
    """View recent audit events"""
    audit_manager = get_audit_manager()
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    query = AuditQuery(
        start_time=start_time,
        end_time=end_time,
        limit=limit
    )
    
    events = audit_manager.query_events(query)
    
    print(f"\n=== Recent Audit Events (Last {hours} hours) ===")
    print(f"Found {len(events)} events")
    print(f"{'Timestamp':<19} | {'Event Type':<20} | {'Severity':<8} | {'Subject':<15} | {'Action'}")
    print("-" * 120)
    
    for event in events:
        print(format_event_summary(event))


def view_boardroom_decisions(days: int = 7):
    """View recent boardroom decisions"""
    audit_manager = get_audit_manager()
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    query = AuditQuery(
        start_time=start_time,
        end_time=end_time,
        event_types=[AuditEventType.BOARDROOM_DECISION, AuditEventType.AGENT_VOTE],
        limit=100
    )
    
    events = audit_manager.query_events(query)
    
    # Group by decision
    decisions = {}
    votes = {}
    
    for event in events:
        if event.event_type == AuditEventType.BOARDROOM_DECISION:
            decisions[event.subject_id] = event
        elif event.event_type == AuditEventType.AGENT_VOTE:
            decision_id = event.target or "unknown"
            if decision_id not in votes:
                votes[decision_id] = []
            votes[decision_id].append(event)
    
    print(f"\n=== Boardroom Decisions (Last {days} days) ===")
    
    for decision_id, decision in decisions.items():
        print(f"\nDecision: {decision_id}")
        print(f"  Timestamp: {decision.timestamp}")
        print(f"  Type: {decision.context.get('decision_type', 'Unknown')}")
        print(f"  Proposed by: {decision.context.get('proposed_by', 'Unknown')}")
        print(f"  Final Decision: {decision.context.get('final_decision', 'Unknown')}")
        print(f"  Confidence: {decision.metrics.get('confidence_score', 0):.2f}")
        print(f"  Consensus: {decision.metrics.get('consensus_score', 0):.2f}")
        
        if decision_id in votes:
            print(f"  Votes ({len(votes[decision_id])}):")
            for vote in votes[decision_id]:
                print(f"    - {vote.subject_role}: {vote.metrics.get('vote_value', 0):.2f} (conf: {vote.metrics.get('confidence', 0):.2f})")


def view_mcp_interactions(hours: int = 24):
    """View MCP server interactions"""
    audit_manager = get_audit_manager()
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    query = AuditQuery(
        start_time=start_time,
        end_time=end_time,
        event_types=[AuditEventType.MCP_REQUEST, AuditEventType.MCP_RESPONSE, AuditEventType.MCP_ERROR],
        limit=100
    )
    
    events = audit_manager.query_events(query)
    
    print(f"\n=== MCP Server Interactions (Last {hours} hours) ===")
    
    # Group by MCP server
    by_server = {}
    for event in events:
        server = event.mcp_server or "unknown"
        if server not in by_server:
            by_server[server] = []
        by_server[server].append(event)
    
    for server, server_events in by_server.items():
        print(f"\nMCP Server: {server}")
        success_count = sum(1 for e in server_events if e.context.get('success', False))
        error_count = len(server_events) - success_count
        print(f"  Total interactions: {len(server_events)} (Success: {success_count}, Errors: {error_count})")
        
        for event in server_events[-5:]:  # Show last 5
            status = "✓" if event.context.get('success', False) else "✗"
            print(f"    {status} {event.timestamp.strftime('%H:%M:%S')} - {event.context.get('operation', 'unknown')} by {event.subject_id}")


def view_security_events(hours: int = 24):
    """View security-related audit events"""
    audit_manager = get_audit_manager()
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    query = AuditQuery(
        start_time=start_time,
        end_time=end_time,
        event_types=[AuditEventType.ACCESS_DENIED, AuditEventType.ACCESS_GRANTED, AuditEventType.MCP_ACCESS_DENIED],
        limit=100
    )
    
    events = audit_manager.query_events(query)
    
    print(f"\n=== Security Events (Last {hours} hours) ===")
    
    granted = [e for e in events if e.event_type == AuditEventType.ACCESS_GRANTED]
    denied = [e for e in events if e.event_type in [AuditEventType.ACCESS_DENIED, AuditEventType.MCP_ACCESS_DENIED]]
    
    print(f"Access Granted: {len(granted)}")
    print(f"Access Denied: {len(denied)}")
    
    if denied:
        print(f"\nRecent Access Denials:")
        for event in denied[-10:]:  # Show last 10 denials
            reason = event.context.get('reason', 'Unknown reason')
            print(f"  {event.timestamp.strftime('%H:%M:%S')} - {event.subject_id} ({event.subject_type}) -> {event.mcp_server}.{event.context.get('operation', 'unknown')}")
            print(f"    Reason: {reason}")


def export_compliance_report(days: int = 30, format: str = "json", output_file: Optional[str] = None):
    """Export compliance report"""
    audit_manager = get_audit_manager()
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    query = AuditQuery(
        start_time=start_time,
        end_time=end_time,
        limit=10000  # Large limit for comprehensive report
    )
    
    export_data = audit_manager.export_audit_trail(
        query=query,
        format=format,
        include_integrity_check=True
    )
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(export_data)
        print(f"Compliance report exported to: {output_file}")
    else:
        print(export_data)


