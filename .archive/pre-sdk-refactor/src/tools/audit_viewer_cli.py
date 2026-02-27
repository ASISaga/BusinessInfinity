"""
Business Infinity Audit Trail Viewer - CLI Entrypoint

This script provides the command-line interface for audit_viewer.py.
"""

import argparse
from datetime import datetime, timedelta
from audit_viewer import (
    view_recent_events,
    view_boardroom_decisions,
    view_mcp_interactions,
    view_security_events,
    export_compliance_report,
    print_event_details,
    get_audit_manager,
    AuditQuery
)

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
