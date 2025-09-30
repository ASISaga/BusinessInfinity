#!/usr/bin/env python3
"""
Demo script showcasing the enhanced audit-driven self-learning system.

This demonstrates the new functionality implemented based on the Self-Learning.md
framework including episode processing, metrics calculation, decision engine,
and abstract context management.
"""

import asyncio
import tempfile
import json
from datetime import datetime
from adapters.self_learning_system import (
    SelfLearningSystem, EpisodeEvent, InterfaceType, FocusArea
)


async def demo_enhanced_self_learning():
    """Demo the enhanced self-learning system capabilities"""
    print("🚀 Enhanced Audit-Driven Self-Learning System Demo")
    print("=" * 60)
    
    # Create temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temporary data directory: {temp_dir}")
        
        # Initialize enhanced system
        system = SelfLearningSystem(data_dir=temp_dir)
        print("✅ Enhanced self-learning system initialized")
        print(f"   - Metrics Calculator: {type(system.metrics_calculator).__name__}")
        print(f"   - Decision Engine: {type(system.decision_engine).__name__}")
        print(f"   - Context Manager: {type(system.context_manager).__name__}")
        print()
        
        # Demo 1: Context-focused episode
        print("📊 Demo 1: Episode with Context Focus")
        print("-" * 40)
        
        context_episode = create_context_focused_episode()
        result1 = await system.process_episode(context_episode)
        
        print(f"Episode ID: {result1['episode_id']}")
        print(f"Focus Area: {result1['focus_area']}")
        print(f"Metrics Summary:")
        print(f"  - Retrieval Hit Rate: {result1['metrics'].retrieval_hit_rate}")
        print(f"  - Conflict Density: {result1['metrics'].conflict_density}")
        print(f"Changes Applied: {result1['changes_applied']}")
        print()
        
        # Demo 2: Interface-focused episode
        print("🔧 Demo 2: Episode with Interface Focus")
        print("-" * 40)
        
        interface_episode = create_interface_focused_episode()
        result2 = await system.process_episode(interface_episode)
        
        print(f"Episode ID: {result2['episode_id']}")
        print(f"Focus Area: {result2['focus_area']}")
        print(f"Interface Error Rates: {dict(result2['metrics'].interface_error_rates)}")
        print(f"Changes Applied: {result2['changes_applied']}")
        print()
        
        # Demo 3: Model-focused episode
        print("🧠 Demo 3: Episode with Model Focus")
        print("-" * 40)
        
        model_episode = create_model_focused_episode()
        result3 = await system.process_episode(model_episode)
        
        print(f"Episode ID: {result3['episode_id']}")
        print(f"Focus Area: {result3['focus_area']}")
        print(f"Prediction Quality:")
        print(f"  - F1 Score: {result3['metrics'].f1_score}")
        print(f"  - RMSE: {result3['metrics'].rmse}")
        print(f"Changes Applied: {result3['changes_applied']}")
        print()
        
        # Demo 4: Shadow evaluation and rollback
        print("🔄 Demo 4: Shadow Evaluation and Rollback")
        print("-" * 40)
        
        rollback_episode = create_rollback_demo_episode()
        # Mock poor evaluation results
        original_shadow_eval = system._shadow_evaluate
        async def mock_poor_evaluation(agent_id, episode):
            return {
                "improvement": -0.05,
                "confidence_interval": [-0.1, 0.0],
                "baseline_performance": 0.8,
                "new_performance": 0.75
            }
        system._shadow_evaluate = mock_poor_evaluation
        
        result4 = await system.process_episode(rollback_episode)
        
        print(f"Episode ID: {result4['episode_id']}")
        print(f"Focus Area: {result4['focus_area']}")
        print(f"Evaluation Result: {result4['evaluation_result']}")
        print(f"Changes Rolled Back: {result4['changes_applied']['rolled_back']}")
        print()
        
        # Restore original method
        system._shadow_evaluate = original_shadow_eval
        
        # Demo 5: Abstract context management
        print("🧠 Demo 5: Abstract Context Management")
        print("-" * 40)
        
        agent_id = "ceo_001"
        context = await system.context_manager.get_context(agent_id)
        if context:
            print(f"Context for {agent_id}:")
            print(f"  - Commitments: {len(context.commitments)}")
            print(f"  - Episode Summaries: {len(context.episode_summaries)}")
            print(f"  - Reliability Scores: {context.reliability_scores}")
            print(f"  - Version: {context.version}")
            print(f"  - Last Updated: {context.last_updated}")
            
            # Check for conflicts
            conflicts = system.context_manager.detect_conflicts(context)
            if conflicts:
                print(f"  - Conflicts Detected: {len(conflicts)}")
                for conflict in conflicts[:2]:  # Show first 2 conflicts
                    print(f"    * {conflict}")
            else:
                print("  - No conflicts detected")
        print()
        
        # Demo 6: System statistics
        print("📈 Demo 6: System Statistics")
        print("-" * 40)
        
        print(f"Total Episodes Processed: {len(system.episodes)}")
        print(f"Total Derived Metrics: {len(system.derived_metrics)}")
        print(f"Shadow Evaluations: {len(system.shadow_evaluations)}")
        print(f"Rollback Points: {len(system.rollback_points)}")
        print(f"Context Versions: {sum(len(versions) for versions in system.context_manager.context_versions.values())}")
        print()
        
        print("🎉 Enhanced Self-Learning System Demo Complete!")
        print("=" * 60)


def create_context_focused_episode():
    """Create an episode that will trigger context focus"""
    return EpisodeEvent(
        agent_id="ceo_001",
        scenario_id="strategic_planning_context_demo",
        timestamp=datetime.now(),
        source="demo",
        correlation_ids=["demo_context_001"],
        user_intent="Develop quarterly strategic plan with market analysis",
        prompts=["What should be our strategic priorities for Q4?"],
        tool_calls=[{"tool": "market_analysis", "params": {"depth": "comprehensive"}}],
        retrieved_context={
            "retrieved_items": 3,   # Low hit rate
            "total_queries": 15,
            "conflicts": 8,         # High conflict density
            "total_items": 12
        },
        third_party_payloads={"market_data": {"growth_rate": 0.15}},
        model_output="Based on limited market data, I recommend focusing on customer retention...",
        action_plan={"priority": "customer_retention", "timeline": "Q4"},
        selected_tools=["market_analysis"],
        confidence_scores={"strategy": 0.65},  # Low confidence due to poor context
        actual_results={"implementation_success": True},
        user_verdict="needs_improvement",
        interfaces_used={}  # No interface issues
    )


def create_interface_focused_episode():
    """Create an episode that will trigger interface focus"""
    return EpisodeEvent(
        agent_id="cfo_001",
        scenario_id="financial_analysis_interface_demo",
        timestamp=datetime.now(),
        source="demo",
        correlation_ids=["demo_interface_001"],
        user_intent="Generate quarterly financial report",
        prompts=["Please prepare the Q4 financial analysis"],
        tool_calls=[{"tool": "erp_integration", "params": {"report_type": "quarterly"}}],
        retrieved_context={
            "retrieved_items": 18,
            "total_queries": 20,    # Good hit rate
            "conflicts": 1,
            "total_items": 20       # Low conflict density
        },
        third_party_payloads={"erp_data": {"budget": 1000000}},
        model_output="Financial analysis shows strong Q4 performance...",
        action_plan={"report_delivery": "by_friday", "format": "executive_summary"},
        selected_tools=["erp_integration", "financial_modeling"],
        confidence_scores={"financial_accuracy": 0.85},
        actual_results={"report_generated": True},
        user_verdict="success",
        interfaces_used={
            InterfaceType.ERP: {"error_count": 5, "total_calls": 20, "retry_count": 3},  # High error rate
            InterfaceType.CRM: {"error_count": 0, "total_calls": 10, "retry_count": 0}
        }
    )


def create_model_focused_episode():
    """Create an episode that will trigger model focus"""
    return EpisodeEvent(
        agent_id="cmo_001",
        scenario_id="marketing_prediction_model_demo",
        timestamp=datetime.now(),
        source="demo",
        correlation_ids=["demo_model_001"],
        user_intent="Predict campaign effectiveness for new product launch",
        prompts=["What will be the ROI of our new product marketing campaign?"],
        tool_calls=[{"tool": "campaign_predictor", "params": {"product": "new_widget"}}],
        retrieved_context={
            "retrieved_items": 19,
            "total_queries": 20,    # Good context
            "conflicts": 0,
            "total_items": 20
        },
        third_party_payloads={"campaign_data": {"budget": 500000}},
        model_output="Predicted campaign ROI: 250%. Expected conversion: 15%",
        action_plan={"campaign_start": "next_month", "budget_allocation": "aggressive"},
        selected_tools=["campaign_predictor"],
        confidence_scores={"roi_prediction": 0.92, "conversion_prediction": 0.88},
        actual_results={
            "predicted_categories": ["high_roi", "medium_conversion"],
            "actual_categories": ["medium_roi", "low_conversion"],  # Poor predictions
            "predicted_values": [2.5, 0.15],
            "actual_roi": 1.8,
            "actual_conversion": 0.08
        },
        user_verdict="mixed_results",
        kpis={"actual_roi": 1.8, "actual_conversion": 0.08},
        interfaces_used={}  # No interface issues
    )


def create_rollback_demo_episode():
    """Create an episode to demonstrate rollback mechanism"""
    return EpisodeEvent(
        agent_id="coo_001",
        scenario_id="operations_optimization_rollback_demo",
        timestamp=datetime.now(),
        source="demo",
        correlation_ids=["demo_rollback_001"],
        user_intent="Optimize warehouse operations for efficiency",
        prompts=["How can we improve warehouse efficiency by 20%?"],
        tool_calls=[{"tool": "operations_optimizer", "params": {"target_improvement": 0.20}}],
        retrieved_context={
            "retrieved_items": 16,
            "total_queries": 18,
            "conflicts": 2,
            "total_items": 18
        },
        third_party_payloads={"warehouse_data": {"current_efficiency": 0.75}},
        model_output="Implement automated sorting and reduce staff by 15%...",
        action_plan={"automation": "immediate", "staff_reduction": "gradual"},
        selected_tools=["operations_optimizer"],
        confidence_scores={"efficiency_gain": 0.85},
        actual_results={"efficiency_improvement": 0.18},
        user_verdict="close_to_target",
        interfaces_used={}
    )


if __name__ == "__main__":
    asyncio.run(demo_enhanced_self_learning())