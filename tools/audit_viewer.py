"""
Audit Trail Viewer and Reporting Tool

Provides tools to view, query, and analyze audit trail data from the Business Infinity system.
Supports various export formats and compliance reporting.
"""

import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.audit_trail import (
    AuditTrailManager, AuditEventType, AuditSeverity, AuditQuery, 
    get_audit_manager
)


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


def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(description="Business Infinity Audit Trail Viewer")
    parser.add_argument("command", choices=[
        "recent", "decisions", "mcp", "security", "export", "details"
    ], help="Command to execute")
    
    parser.add_argument("--hours", type=int, default=24, help="Number of hours to look back")
    parser.add_argument("--days", type=int, default=7, help="Number of days to look back")
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of events to show")
    parser.add_argument("--event-id", type=str, help="Specific event ID to show details for")
    parser.add_argument("--output", type=str, help="Output file for export")
    parser.add_argument("--format", type=str, default="json", choices=["json"], help="Export format")
    
    args = parser.parse_args()
    
    if args.command == "recent":
        view_recent_events(hours=args.hours, limit=args.limit)
    elif args.command == "decisions":
        view_boardroom_decisions(days=args.days)
    elif args.command == "mcp":
        view_mcp_interactions(hours=args.hours)
    elif args.command == "security":
        view_security_events(hours=args.hours)
    elif args.command == "export":
        export_compliance_report(days=args.days, format=args.format, output_file=args.output)
    elif args.command == "details":
        if not args.event_id:
            print("Error: --event-id required for details command")
            return
        
        audit_manager = get_audit_manager()
        query = AuditQuery(limit=10000)  # Large limit to find specific event
        events = audit_manager.query_events(query)
        
        event = next((e for e in events if e.event_id == args.event_id), None)
        if event:
            print_event_details(event)
        else:
            print(f"Event with ID {args.event_id} not found")


if __name__ == "__main__":
    main()