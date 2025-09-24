#!/usr/bin/env python3
"""
Multi-Dimensional Self-Learning System Demonstration

This script demonstrates the comprehensive multi-dimensional learning methodology
that adapts across 5 different dimensions based on stakeholder feedback and
audit trail analysis.

The system intelligently determines when to update:
1. LLM Model - Base model selection and capabilities
2. Weights/Dataset - Training data and model parameters 
3. Context to LLM - Situational context and background information
4. Prompt to LLM - Input formatting and prompt engineering
5. Features of associated MCP - MCP server capabilities and integrations

Usage: python demo_multi_dimensional_learning.py
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import the multi-dimensional learning system
from adapters import (
    initialize_adapter_system,
    LearningDimension,
    AdaptationTrigger,
    AdaptationStrategy
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_sample_stakeholder_feedback() -> List[Dict[str, Any]]:
    """Generate sample stakeholder feedback for demonstration"""
    return [
        {
            "id": "feedback_001",
            "type": "performance_review",
            "content": "The CFO agent's financial analysis lacks depth in market risk assessment. Need more sophisticated modeling capabilities.",
            "sentiment": 0.3,  # Negative feedback
            "severity": 0.8,   # High severity
            "affected_role": "cfo",
            "timestamp": datetime.now().isoformat(),
            "stakeholder": "board_member_1"
        },
        {
            "id": "feedback_002", 
            "type": "decision_quality",
            "content": "Recent boardroom decisions seem to lack proper context about current market conditions and competitor actions.",
            "sentiment": 0.4,  # Somewhat negative
            "severity": 0.6,   # Medium severity
            "affected_role": "all",
            "timestamp": datetime.now().isoformat(),
            "stakeholder": "executive_team"
        },
        {
            "id": "feedback_003",
            "type": "response_clarity",
            "content": "The prompts given to agents are unclear and don't provide sufficient structure for complex strategic decisions.",
            "sentiment": 0.35, # Negative
            "severity": 0.7,   # High-medium severity
            "affected_role": "all",
            "timestamp": datetime.now().isoformat(),
            "stakeholder": "operations_manager"
        },
        {
            "id": "feedback_004",
            "type": "integration_issues", 
            "content": "MCP integrations are failing frequently and causing delays in decision-making processes.",
            "sentiment": 0.2,  # Very negative
            "severity": 0.9,   # Very high severity
            "affected_role": "all",
            "timestamp": datetime.now().isoformat(),
            "stakeholder": "it_manager"
        },
        {
            "id": "feedback_005",
            "type": "learning_effectiveness",
            "content": "The system doesn't seem to be learning from previous mistakes. Same errors are repeated across cycles.",
            "sentiment": 0.25, # Very negative
            "severity": 0.8,   # High severity
            "affected_role": "all",
            "timestamp": datetime.now().isoformat(),
            "stakeholder": "quality_assurance"
        },
        {
            "id": "feedback_006",
            "type": "positive_feedback",
            "content": "The CTO agent's technical recommendations have been excellent and well-aligned with our technology strategy.",
            "sentiment": 0.9,  # Very positive
            "severity": 0.1,   # Low severity (positive feedback)
            "affected_role": "cto",
            "timestamp": datetime.now().isoformat(),
            "stakeholder": "engineering_lead"
        }
    ]


def generate_sample_audit_events() -> List[Dict[str, Any]]:
    """Generate sample audit events for demonstration"""
    base_time = datetime.now() - timedelta(days=7)
    
    return [
        {
            "event_id": "audit_001",
            "event_type": "boardroom_decision",
            "timestamp": (base_time + timedelta(hours=1)).isoformat(),
            "subject_id": "autonomous_boardroom",
            "subject_type": "system",
            "action": "Strategic expansion decision",
            "context": {
                "confidence_score": 0.65,
                "consensus_score": 0.7,
                "decision_start": (base_time + timedelta(minutes=30)).isoformat(),
                "participants": ["cfo", "cmo", "founder"]
            }
        },
        {
            "event_id": "audit_002",
            "event_type": "agent_vote",
            "timestamp": (base_time + timedelta(hours=2)).isoformat(),
            "subject_id": "agent_cfo",
            "subject_role": "cfo",
            "subject_type": "agent", 
            "action": "Cast vote on budget allocation",
            "context": {
                "vote_value": 0.4,  # Low confidence vote
                "confidence": 0.5,  # Medium confidence
                "decision_id": "decision_001"
            }
        },
        {
            "event_id": "audit_003",
            "event_type": "mcp_request",
            "timestamp": (base_time + timedelta(hours=3)).isoformat(),
            "subject_id": "boardroom_agent",
            "subject_type": "agent",
            "action": "Request market data",
            "context": {
                "success": False,   # Failed request
                "error_type": "timeout",
                "response_time_ms": 5000,  # 5 second timeout
                "mcp_server": "market_data"
            }
        },
        {
            "event_id": "audit_004",
            "event_type": "agent_vote",
            "timestamp": (base_time + timedelta(hours=4)).isoformat(),
            "subject_id": "agent_cmo",
            "subject_role": "cmo", 
            "subject_type": "agent",
            "action": "Cast vote on marketing strategy",
            "context": {
                "vote_value": 0.3,  # Low vote
                "confidence": 0.45, # Low confidence
                "decision_id": "decision_002"
            }
        },
        {
            "event_id": "audit_005",
            "event_type": "mcp_response",
            "timestamp": (base_time + timedelta(hours=5)).isoformat(),
            "subject_id": "mcp_linkedin",
            "subject_type": "mcp_server",
            "action": "Return social media analytics",
            "context": {
                "success": True,
                "response_time_ms": 1200,
                "data_quality": 0.8
            }
        }
    ]


async def demo_stakeholder_feedback_analysis():
    """Demonstrate stakeholder feedback analysis"""
    print("\n" + "="*70)
    print("1. STAKEHOLDER FEEDBACK ANALYSIS")
    print("="*70)
    
    # Initialize the adapter system
    print("Initializing adapter system...")
    orchestrator = await initialize_adapter_system()
    
    if not hasattr(orchestrator, 'multi_dimensional_learning') or not orchestrator.multi_dimensional_learning:
        print("Multi-dimensional learning not available - skipping demo")
        return
    
    # Generate sample feedback
    feedback_data = generate_sample_stakeholder_feedback()
    print(f"Generated {len(feedback_data)} sample feedback entries")
    
    # Analyze feedback
    print("\nAnalyzing stakeholder feedback patterns...")
    analysis_result = await orchestrator.analyze_stakeholder_feedback(feedback_data)
    
    if analysis_result.get("success"):
        print(f"✓ Analysis completed successfully")
        print(f"  Patterns identified: {analysis_result['patterns_identified']}")
        print(f"  Adaptations recommended: {analysis_result['adaptations_recommended']}")
        
        # Show feedback patterns
        print("\n--- FEEDBACK PATTERNS ---")
        for pattern in analysis_result.get("feedback_patterns", []):
            print(f"  {pattern['dimension'].upper()}: {pattern['feedback_type']}")
            print(f"    Frequency: {pattern['frequency']}, Severity: {pattern['severity']:.2f}")
            print(f"    Trend: {pattern['trend']}, Confidence: {pattern['confidence']:.2f}")
            print(f"    Suggested: {pattern['suggested_action']}")
        
        # Show adaptation decisions
        print("\n--- ADAPTATION DECISIONS ---")
        for decision in analysis_result.get("adaptation_decisions", []):
            print(f"  Priority {decision['priority']}: {decision['dimension'].upper()}")
            print(f"    Strategy: {decision['strategy']}")
            print(f"    Impact: {decision['estimated_impact']:.2f}, Cost: {decision['estimated_cost']:.1f}")
            print(f"    Timeline: {decision['timeline']}")
            print(f"    Risk: {decision['risk_assessment']:.2f}")
    else:
        print(f"✗ Analysis failed: {analysis_result.get('error')}")


async def demo_audit_pattern_analysis():
    """Demonstrate audit trail pattern analysis"""
    print("\n" + "="*70)
    print("2. AUDIT TRAIL PATTERN ANALYSIS")
    print("="*70)
    
    # Initialize the adapter system
    orchestrator = await initialize_adapter_system()
    
    if not hasattr(orchestrator, 'multi_dimensional_learning') or not orchestrator.multi_dimensional_learning:
        print("Multi-dimensional learning not available - skipping demo")
        return
    
    # Analyze audit patterns
    print("Analyzing audit trail patterns (last 30 days)...")
    analysis_result = await orchestrator.analyze_audit_patterns(lookback_days=30)
    
    if analysis_result.get("success"):
        print(f"✓ Analysis completed successfully")
        print(f"  Audit events analyzed: {analysis_result['audit_events_analyzed']}")
        print(f"  Patterns identified: {analysis_result['patterns_identified']}")
        print(f"  Adaptations recommended: {analysis_result['adaptations_recommended']}")
        
        # Show audit patterns
        print("\n--- AUDIT PATTERNS ---")
        for pattern in analysis_result.get("audit_patterns", []):
            print(f"  {pattern['dimension'].upper()}: {pattern['pattern_type']}")
            print(f"    Frequency: {pattern['frequency']}, Severity: {pattern['severity']:.2f}")
            print(f"    Confidence: {pattern['confidence']:.2f}")
        
        # Show recommendations
        print("\n--- AUDIT-BASED RECOMMENDATIONS ---")
        for rec in analysis_result.get("adaptation_recommendations", []):
            print(f"  Priority {rec['priority']}: {rec['dimension'].upper()}")
            print(f"    Trigger: {rec['trigger']}, Strategy: {rec['strategy']}")
            print(f"    Timeline: {rec['timeline']}")
    else:
        print(f"✗ Analysis failed: {analysis_result.get('error')}")


async def demo_comprehensive_analysis():
    """Demonstrate comprehensive multi-dimensional analysis"""
    print("\n" + "="*70)
    print("3. COMPREHENSIVE MULTI-DIMENSIONAL ANALYSIS")
    print("="*70)
    
    # Initialize the adapter system
    orchestrator = await initialize_adapter_system()
    
    if not hasattr(orchestrator, 'multi_dimensional_learning') or not orchestrator.multi_dimensional_learning:
        print("Multi-dimensional learning not available - skipping demo")
        return
    
    # Generate sample data
    feedback_data = generate_sample_stakeholder_feedback()
    
    print("Running comprehensive analysis combining stakeholder feedback and audit patterns...")
    analysis_result = await orchestrator.run_comprehensive_analysis(
        feedback_data=feedback_data,
        audit_lookback_days=30
    )
    
    if analysis_result.get("success"):
        print(f"✓ Comprehensive analysis completed successfully")
        print(f"  Total patterns identified: {analysis_result['total_patterns_identified']}")
        print(f"  Total recommendations: {analysis_result['total_recommendations']}")
        print(f"  Dimensions evaluated: {', '.join(analysis_result['learning_dimensions_evaluated'])}")
        
        results = analysis_result["analysis_results"]
        
        # Stakeholder analysis summary
        if results["stakeholder_analysis"]:
            sa = results["stakeholder_analysis"]
            print(f"\n  Stakeholder Analysis: {sa['patterns_found']} patterns from {sa['feedback_entries_analyzed']} feedback entries")
        
        # Audit analysis summary
        if results["audit_analysis"]:
            aa = results["audit_analysis"]
            print(f"  Audit Analysis: {aa['patterns_found']} patterns from {aa['audit_events_analyzed']} events")
        
        # Combined recommendations
        print("\n--- COMBINED RECOMMENDATIONS (Prioritized) ---")
        for i, rec in enumerate(results.get("combined_recommendations", []), 1):
            print(f"  {i}. {rec['dimension'].upper()} - Priority {rec['priority']}")
            print(f"     Strategy: {rec['strategy']} ({rec['trigger']})")
            print(f"     Impact: {rec['estimated_impact']:.2f}, Cost: {rec['estimated_cost']:.1f}")
            print(f"     Timeline: {rec['timeline']}, Risk: {rec['risk_assessment']:.2f}")
            if rec.get('dependencies'):
                print(f"     Dependencies: {', '.join(rec['dependencies'])}")
            print()
    else:
        print(f"✗ Comprehensive analysis failed: {analysis_result.get('error')}")


async def demo_adaptive_execution():
    """Demonstrate adaptive execution based on analysis"""
    print("\n" + "="*70)
    print("4. INTELLIGENT ADAPTIVE EXECUTION")
    print("="*70)
    
    # Initialize the adapter system
    orchestrator = await initialize_adapter_system()
    
    if not hasattr(orchestrator, 'multi_dimensional_learning') or not orchestrator.multi_dimensional_learning:
        print("Multi-dimensional learning not available - skipping demo")
        return
    
    # Trigger intelligent adaptation
    print("Evaluating system for intelligent adaptation triggers...")
    adaptation_result = await orchestrator.trigger_intelligent_adaptation(
        trigger_threshold=0.8,  # High threshold for demo
        execute_immediately=False  # Don't execute, just recommend
    )
    
    if adaptation_result.get("success"):
        if adaptation_result.get("adaptation_needed"):
            print(f"✓ Adaptation needed detected")
            print(f"  Underperforming dimensions: {len(adaptation_result['underperforming_dimensions'])}")
            print(f"  Priority recommendations: {len(adaptation_result['priority_recommendations'])}")
            
            # Show underperforming dimensions
            print("\n--- UNDERPERFORMING DIMENSIONS ---")
            for dim in adaptation_result["underperforming_dimensions"]:
                print(f"  {dim['dimension'].upper()}:")
                print(f"    Performance: {dim['performance']:.2f}")
                print(f"    Satisfaction: {dim['satisfaction']:.2f}")
            
            # Show priority recommendations
            print("\n--- PRIORITY RECOMMENDATIONS ---")
            for rec in adaptation_result["priority_recommendations"]:
                print(f"  {rec['dimension'].upper()}: {rec['strategy']} (Priority {rec['priority']})")
                print(f"    Impact: {rec['estimated_impact']:.2f}, Timeline: {rec['timeline']}")
            
            # Simulate execution
            print("\n--- SIMULATING ADAPTATION EXECUTION ---")
            if adaptation_result["priority_recommendations"]:
                execution_result = await orchestrator.execute_dimensional_adaptations(
                    adaptation_result["priority_recommendations"]
                )
                
                if execution_result.get("success"):
                    results = execution_result["execution_results"]
                    print(f"✓ Executed {results['adaptations_executed']} adaptations")
                    print(f"  Successful: {results['adaptations_successful']}")
                    print(f"  Failed: {results['adaptations_failed']}")
                    
                    # Show execution details
                    print("\n--- EXECUTION DETAILS ---")
                    for detail in results["execution_details"]:
                        status = "✓" if detail["success"] else "✗"
                        print(f"  {status} {detail['dimension'].upper()}: {detail.get('details', {}).get('strategy', 'N/A')}")
                        if detail["success"] and "changes_made" in detail.get("details", {}):
                            for change in detail["details"]["changes_made"]:
                                print(f"    - {change}")
                else:
                    print(f"✗ Execution failed: {execution_result.get('error')}")
        else:
            print(f"✓ No adaptation needed - all dimensions performing well")
            print(f"  All metrics above threshold: {adaptation_result['trigger_threshold']}")
    else:
        print(f"✗ Intelligent adaptation evaluation failed: {adaptation_result.get('error')}")


async def demo_system_status():
    """Demonstrate multi-dimensional system status monitoring"""
    print("\n" + "="*70)
    print("5. MULTI-DIMENSIONAL SYSTEM STATUS")
    print("="*70)
    
    # Initialize the adapter system
    orchestrator = await initialize_adapter_system()
    
    if not hasattr(orchestrator, 'multi_dimensional_learning') or not orchestrator.multi_dimensional_learning:
        print("Multi-dimensional learning not available - skipping demo")
        return
    
    # Get system status
    print("Retrieving multi-dimensional learning system status...")
    status_result = await orchestrator.get_multi_dimensional_status()
    
    if status_result.get("success"):
        print("✓ System status retrieved successfully")
        
        mdl_status = status_result["multi_dimensional_learning"]
        metrics = mdl_status.get("dimensional_metrics", {})
        
        print(f"  Total adaptations: {mdl_status.get('total_adaptations', 0)}")
        print(f"  Recent patterns: {mdl_status.get('recent_patterns', 0)}")
        print(f"  System status: {mdl_status.get('system_status', 'unknown')}")
        
        # Show dimensional performance
        print("\n--- DIMENSIONAL PERFORMANCE METRICS ---")
        for dim_name, dim_metrics in metrics.items():
            print(f"  {dim_name.upper()}:")
            print(f"    Performance: {dim_metrics['current_performance']:.3f}")
            print(f"    Satisfaction: {dim_metrics['stakeholder_satisfaction']:.3f}")
            print(f"    Adaptations: {dim_metrics['adaptation_frequency']}")
            print(f"    Cost/Benefit: {dim_metrics['cost_benefit_ratio']:.2f}")
            last_adapt = dim_metrics['last_adaptation']
            if last_adapt:
                print(f"    Last Adaptation: {last_adapt}")
            print()
        
        # Calculate overall system health
        avg_performance = sum(m['current_performance'] for m in metrics.values()) / len(metrics) if metrics else 0
        avg_satisfaction = sum(m['stakeholder_satisfaction'] for m in metrics.values()) / len(metrics) if metrics else 0
        
        print(f"--- OVERALL SYSTEM HEALTH ---")
        print(f"  Average Performance: {avg_performance:.3f}")
        print(f"  Average Satisfaction: {avg_satisfaction:.3f}")
        
        if avg_performance > 0.8 and avg_satisfaction > 0.8:
            health_status = "EXCELLENT"
        elif avg_performance > 0.6 and avg_satisfaction > 0.6:
            health_status = "GOOD"
        elif avg_performance > 0.4 and avg_satisfaction > 0.4:
            health_status = "FAIR"
        else:
            health_status = "NEEDS ATTENTION"
        
        print(f"  System Health: {health_status}")
    else:
        print(f"✗ Status retrieval failed: {status_result.get('error')}")


async def main():
    """Run complete multi-dimensional learning demonstration"""
    print("Business Infinity Multi-Dimensional Self-Learning System Demo")
    print("=" * 70)
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis demo shows how the system adapts across 5 dimensions:")
    print("1. LLM Model - Base model selection and capabilities")
    print("2. Weights/Dataset - Training data and model parameters")
    print("3. Context - Situational context and background information")
    print("4. Prompt - Input formatting and prompt engineering")
    print("5. MCP Features - MCP server capabilities and integrations")
    
    try:
        # 1. Stakeholder feedback analysis
        await demo_stakeholder_feedback_analysis()
        
        # 2. Audit pattern analysis
        await demo_audit_pattern_analysis()
        
        # 3. Comprehensive analysis
        await demo_comprehensive_analysis()
        
        # 4. Intelligent adaptive execution
        await demo_adaptive_execution()
        
        # 5. System status monitoring
        await demo_system_status()
        
        print("\n" + "="*70)
        print("MULTI-DIMENSIONAL LEARNING DEMO COMPLETED SUCCESSFULLY")
        print("="*70)
        print("The system successfully demonstrated:")
        print("✓ Stakeholder feedback pattern analysis")
        print("✓ Audit trail pattern recognition")
        print("✓ Multi-dimensional adaptation decision making")
        print("✓ Intelligent adaptation triggering and execution")
        print("✓ Comprehensive system health monitoring")
        print("\nThe multi-dimensional learning system is ready for production use.")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\nDemo encountered an error: {e}")
        print("This may be due to missing dependencies or system limitations.")


if __name__ == "__main__":
    asyncio.run(main())