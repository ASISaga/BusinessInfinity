#!/usr/bin/env python3
"""
Business Infinity Audit Trail System Demo

Demonstrates comprehensive audit trail functionality including:
- Boardroom decision making and voting
- MCP server interactions
- Social media actions
- Business system actions
- Access control events
- Audit trail querying and reporting
"""

import sys
import os
sys.path.insert(0, '.')

from core.audit_trail import (
    AuditTrailManager, AuditEventType, AuditSeverity, AuditQuery,
    get_audit_manager
)
from core.mcp_access_control import MCPAccessControlManager
from datetime import datetime, timedelta
import json


def simulate_boardroom_session():
    """Simulate a complete boardroom decision-making session"""
    print("🏢 Simulating Boardroom Decision Session...")
    
    audit_manager = get_audit_manager()
    
    # 1. Boardroom session initialization
    session_id = "boardroom_session_2024_q1_001"
    audit_manager.log_event(
        event_type=AuditEventType.SYSTEM_STARTUP,
        subject_id=session_id,
        subject_type="system",
        action="Autonomous boardroom session started",
        severity=AuditSeverity.MEDIUM,
        context={
            "session_type": "strategic_planning",
            "quarter": "Q1_2024",
            "participants": ["CEO", "CFO", "CMO", "CTO", "COO"]
        },
        compliance_tags={"business_governance", "sox"}
    )
    
    # 2. Market expansion proposal
    proposal = {
        "title": "European Market Expansion Initiative",
        "description": "Expand Business Infinity operations to European markets, starting with Germany and France",
        "projected_investment": 2500000,
        "projected_roi": 0.35,
        "timeline": "6 months"
    }
    
    audit_manager.log_event(
        event_type=AuditEventType.AGENT_PROPOSAL,
        subject_id="strategic_planning_agent",
        subject_type="agent",
        subject_role="Strategic Planning",
        action="Submitted market expansion proposal",
        context=proposal,
        rationale="Market analysis indicates strong demand for AI business automation in European markets",
        evidence=[
            "European AI market report Q4 2023",
            "Competitor analysis - 3 main players identified",
            "Customer demand survey - 78% interest rate"
        ],
        severity=AuditSeverity.HIGH,
        compliance_tags={"business_governance", "strategic_planning"}
    )
    
    # 3. Individual agent votes
    votes = [
        {
            "agent": "CEO",
            "role": "Chief Executive Officer", 
            "vote_value": 0.85,
            "rationale": "Strong strategic alignment with our 5-year growth plan",
            "confidence": 0.9
        },
        {
            "agent": "CFO", 
            "role": "Chief Financial Officer",
            "vote_value": 0.75,
            "rationale": "Financially viable with acceptable risk profile",
            "confidence": 0.8
        },
        {
            "agent": "CMO",
            "role": "Chief Marketing Officer", 
            "vote_value": 0.90,
            "rationale": "European market shows strong demand signals",
            "confidence": 0.85
        },
        {
            "agent": "CTO",
            "role": "Chief Technology Officer",
            "vote_value": 0.70,
            "rationale": "Technical infrastructure can support expansion",
            "confidence": 0.75
        },
        {
            "agent": "COO",
            "role": "Chief Operating Officer",
            "vote_value": 0.65,
            "rationale": "Operational complexity is manageable with proper planning",
            "confidence": 0.70
        }
    ]
    
    decision_id = "decision_eu_expansion_2024"
    
    for vote in votes:
        audit_manager.log_agent_vote(
            voter_id=f"{vote['agent'].lower()}_agent",
            voter_role=vote['role'],
            decision_id=decision_id,
            vote_value=vote['vote_value'],
            rationale=vote['rationale'],
            evidence=[f"Domain expertise: {vote['role']}", f"LoRA adapter score: {vote['vote_value']}"],
            confidence=vote['confidence']
        )
    
    # 4. Final boardroom decision
    final_decision = "APPROVED - European market expansion initiative approved with phased approach"
    confidence_score = sum(v['vote_value'] * v['confidence'] for v in votes) / len(votes)
    consensus_score = 1.0 - (max(v['vote_value'] for v in votes) - min(v['vote_value'] for v in votes))
    
    audit_manager.log_boardroom_decision(
        decision_id=decision_id,
        decision_type="strategic",
        proposed_by="strategic_planning_agent",
        final_decision=final_decision,
        rationale="Strong consensus among leadership team with solid financial and market justification",
        votes=[{
            "voter_id": f"{v['agent'].lower()}_agent",
            "voter_role": v['role'],
            "vote_value": v['vote_value'],
            "confidence": v['confidence'],
            "rationale": v['rationale']
        } for v in votes],
        confidence_score=confidence_score,
        consensus_score=consensus_score
    )
    
    print(f"✅ Boardroom decision logged: {decision_id}")
    print(f"   Decision: {final_decision}")
    print(f"   Confidence: {confidence_score:.2f}, Consensus: {consensus_score:.2f}")


def simulate_mcp_interactions():
    """Simulate MCP server interactions across different platforms"""
    print("\\n🔗 Simulating MCP Server Interactions...")
    
    audit_manager = get_audit_manager()
    
    # 1. LinkedIn announcement post
    linkedin_response = audit_manager.log_mcp_interaction(
        mcp_server="linkedin",
        operation="create_post",
        subject_id="marketing_agent_001",
        subject_type="agent",
        success=True,
        request_data={
            "content": "🚀 Big news! Business Infinity is expanding to European markets! Our AI-powered boardroom technology is helping startups make better strategic decisions. #AI #BusinessAutomation #Europe #Expansion",
            "target_audience": "technology_professionals",
            "visibility": "public"
        },
        response_data={
            "post_id": "linkedin_post_20240115_001",
            "status": "published",
            "visibility": "public",
            "initial_engagement": {
                "impressions": 1500,
                "likes": 89,
                "comments": 23,
                "shares": 12
            }
        }
    )
    
    # 2. Reddit community engagement
    reddit_response = audit_manager.log_mcp_interaction(
        mcp_server="reddit",
        operation="create_post",
        subject_id="community_manager_agent",
        subject_type="agent", 
        success=True,
        request_data={
            "subreddit": "startups",
            "title": "How AI Boardroom Technology is Revolutionizing Startup Decision-Making",
            "content": "Sharing insights from our autonomous boardroom implementation...",
            "flair": "Discussion"
        },
        response_data={
            "post_id": "reddit_startups_20240115_001",
            "status": "published",
            "upvotes": 156,
            "comments": 47,
            "engagement_rate": 0.23
        }
    )
    
    # 3. ERPNext customer record creation
    erpnext_response = audit_manager.log_mcp_interaction(
        mcp_server="erpnext",
        operation="create_customer",
        subject_id="sales_agent_002", 
        subject_type="agent",
        success=True,
        request_data={
            "customer_name": "TechStart GmbH",
            "country": "Germany",
            "industry": "Technology",
            "contact_email": "contact@techstart.de",
            "estimated_revenue": 50000
        },
        response_data={
            "customer_id": "CUST-2024-001",
            "status": "active",
            "credit_limit": 25000,
            "payment_terms": "Net 30"
        }
    )
    
    # 4. Failed MCP interaction (for demonstration)
    failed_response = audit_manager.log_mcp_interaction(
        mcp_server="linkedin",
        operation="delete_post",
        subject_id="content_moderator_agent",
        subject_type="agent",
        success=False,
        request_data={
            "post_id": "linkedin_post_20240115_002"
        },
        error_details="Insufficient permissions - agent does not have delete permissions for this post"
    )
    
    print(f"✅ LinkedIn post: {linkedin_response[:8]}...")
    print(f"✅ Reddit post: {reddit_response[:8]}...")
    print(f"✅ ERPNext customer: {erpnext_response[:8]}...")
    print(f"❌ Failed LinkedIn delete: {failed_response[:8]}...")


def simulate_business_actions():
    """Simulate business system actions"""
    print("\\n💼 Simulating Business System Actions...")
    
    audit_manager = get_audit_manager()
    
    # 1. Invoice creation
    invoice_id = audit_manager.log_business_action(
        system="erpnext",
        operation="create_invoice",
        agent_id="finance_agent_001",
        business_entity="TechStart GmbH",
        transaction_data={
            "invoice_number": "INV-2024-001",
            "customer": "TechStart GmbH",
            "amount": 15000.00,
            "currency": "EUR",
            "items": [
                {"description": "Business Infinity License", "quantity": 1, "rate": 12000.00},
                {"description": "Implementation Service", "quantity": 1, "rate": 3000.00}
            ],
            "due_date": "2024-02-15",
            "tax_rate": 0.19
        }
    )
    
    # 2. Contract creation
    contract_id = audit_manager.log_business_action(
        system="erpnext",
        operation="create_contract",
        agent_id="legal_agent_001",
        business_entity="TechStart GmbH",
        transaction_data={
            "contract_number": "CONT-2024-001",
            "contract_type": "Software License Agreement",
            "term": "12 months",
            "value": 15000.00,
            "auto_renewal": True,
            "governing_law": "German Law"
        }
    )
    
    # 3. CRM opportunity creation
    opportunity_id = audit_manager.log_business_action(
        system="crm",
        operation="create_opportunity",
        agent_id="sales_agent_002",
        business_entity="FrenchTech SARL",
        transaction_data={
            "opportunity_name": "Business Infinity Implementation - FrenchTech",
            "stage": "Qualified Lead",
            "value": 25000.00,
            "probability": 0.65,
            "expected_close": "2024-03-01",
            "source": "European expansion campaign"
        }
    )
    
    print(f"✅ Invoice created: {invoice_id[:8]}...")
    print(f"✅ Contract created: {contract_id[:8]}...")
    print(f"✅ CRM opportunity: {opportunity_id[:8]}...")


def simulate_social_media_campaign():
    """Simulate comprehensive social media campaign"""
    print("\\n📱 Simulating Social Media Campaign...")
    
    audit_manager = get_audit_manager()
    
    # 1. LinkedIn thought leadership post
    linkedin_post = audit_manager.log_social_media_action(
        platform="linkedin",
        action_type="post",
        agent_id="thought_leader_agent",
        content="🤔 The future of business decision-making is here. Our autonomous boardroom technology has processed over 1,000 strategic decisions with 94% accuracy. What role do you think AI should play in boardroom decisions? #AILeadership #FutureOfWork",
        target_audience="business_executives",
        engagement_metrics={
            "impressions": 8500,
            "likes": 342,
            "comments": 89,
            "shares": 45,
            "clicks": 156,
            "engagement_rate": 0.062
        }
    )
    
    # 2. Reddit AMA announcement
    reddit_ama = audit_manager.log_social_media_action(
        platform="reddit",
        action_type="post",
        agent_id="community_manager_agent",
        content="AMA: We've built an autonomous AI boardroom that makes real business decisions. Ask us anything about AI governance, decision transparency, and the future of automated business leadership!",
        target_audience="technology_community",
        engagement_metrics={
            "upvotes": 892,
            "comments": 267,
            "awards": 15,
            "crossposts": 8,
            "engagement_rate": 0.34
        }
    )
    
    # 3. LinkedIn case study
    case_study = audit_manager.log_social_media_action(
        platform="linkedin",
        action_type="article",
        agent_id="content_marketing_agent",
        content="Case Study: How AI-Powered Boardroom Decisions Increased Startup Success Rate by 40%. Detailed analysis of 6-month pilot program with 25 startups using Business Infinity autonomous decision-making technology.",
        target_audience="startup_founders",
        engagement_metrics={
            "views": 12000,
            "likes": 456,
            "comments": 123,
            "shares": 78,
            "saves": 234,
            "follows_generated": 89
        }
    )
    
    print(f"✅ LinkedIn thought leadership: {linkedin_post[:8]}...")
    print(f"✅ Reddit AMA: {reddit_ama[:8]}...")
    print(f"✅ LinkedIn case study: {case_study[:8]}...")


def simulate_access_control_events():
    """Simulate access control and security events"""
    print("\\n🔐 Simulating Access Control Events...")
    
    audit_manager = get_audit_manager()
    
    # 1. Successful user access
    audit_manager.log_event(
        event_type=AuditEventType.ACCESS_GRANTED,
        subject_id="user_john_smith",
        subject_type="user",
        subject_role="Manager",
        action="Granted access to linkedin.create_post",
        mcp_server="linkedin",
        context={
            "operation": "create_post",
            "access_level": "full_write",
            "onboarding_stage": "trusted"
        },
        compliance_tags={"access_control", "data_access"}
    )
    
    # 2. Denied access - insufficient permissions
    audit_manager.log_event(
        event_type=AuditEventType.ACCESS_DENIED,
        subject_id="user_jane_doe",
        subject_type="user",
        subject_role="Employee",
        action="Denied access to erpnext.delete_customer",
        mcp_server="erpnext",
        severity=AuditSeverity.MEDIUM,
        context={
            "operation": "delete_customer",
            "access_level": "read_only",
            "reason": "Operation requires full_write access level"
        },
        compliance_tags={"access_control", "security"}
    )
    
    # 3. Agent permission escalation
    audit_manager.log_event(
        event_type=AuditEventType.PERMISSION_CHANGE,
        subject_id="marketing_agent_001",
        subject_type="agent",
        subject_role="Marketing Agent",
        action="Permission escalated to admin level for emergency campaign",
        context={
            "previous_level": "full_write",
            "new_level": "admin",
            "escalation_reason": "Emergency product recall campaign",
            "authorized_by": "cmo_agent",
            "duration": "2 hours"
        },
        severity=AuditSeverity.HIGH,
        compliance_tags={"access_control", "emergency_escalation"}
    )
    
    print("✅ Access control events simulated")


def generate_comprehensive_report():
    """Generate and display comprehensive audit report"""
    print("\\n📊 Generating Comprehensive Audit Report...")
    
    audit_manager = get_audit_manager()
    
    # Query all events from the last day
    query = AuditQuery(
        start_time=datetime.utcnow() - timedelta(days=1),
        limit=1000
    )
    
    events = audit_manager.query_events(query)
    
    print(f"\\n=== Audit Trail Summary ===")
    print(f"Total Events: {len(events)}")
    
    # Event type breakdown
    event_types = {}
    severity_counts = {}
    compliance_tags = set()
    
    for event in events:
        event_type = event.event_type.value
        event_types[event_type] = event_types.get(event_type, 0) + 1
        
        severity = event.severity.value
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        compliance_tags.update(event.compliance_tags)
    
    print(f"\\nEvent Types:")
    for event_type, count in sorted(event_types.items()):
        print(f"  {event_type}: {count}")
    
    print(f"\\nSeverity Distribution:")
    for severity, count in sorted(severity_counts.items()):
        print(f"  {severity}: {count}")
    
    print(f"\\nCompliance Tags: {', '.join(sorted(compliance_tags))}")
    
    # Integrity check
    integrity_valid = sum(1 for event in events if event.verify_integrity())
    print(f"\\nIntegrity Check: {integrity_valid}/{len(events)} events verified")
    
    # Generate export
    export_data = audit_manager.export_audit_trail(
        query=query,
        format="json",
        include_integrity_check=True
    )
    
    print(f"\\nExport Size: {len(export_data)} bytes")
    print("✅ Comprehensive audit report generated")


def main():
    """Run comprehensive audit trail demo"""
    print("🎯 Business Infinity Comprehensive Audit Trail Demo")
    print("=" * 60)
    
    try:
        # Simulate various business activities
        simulate_boardroom_session()
        simulate_mcp_interactions()
        simulate_business_actions()
        simulate_social_media_campaign()
        simulate_access_control_events()
        
        # Generate comprehensive report
        generate_comprehensive_report()
        
        print("\\n🎉 Demo completed successfully!")
        print("\\nNext steps:")
        print("- View recent events: python tools/audit_viewer.py recent")
        print("- View boardroom decisions: python tools/audit_viewer.py decisions")
        print("- View MCP interactions: python tools/audit_viewer.py mcp")
        print("- Export compliance report: python tools/audit_viewer.py export --output report.json")
        
    except Exception as e:
        print(f"\\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()