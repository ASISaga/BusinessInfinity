"""
Test suite for the enhanced audit-driven self-learning system.

Tests the new functionality added to implement the Self-Learning.md framework:
- Episode processing and metrics calculation
- Decision engine for focus area determination
- Abstract context management
- Shadow evaluation and rollback mechanisms
"""

import pytest
import asyncio
import json
import tempfile
import os
from datetime import datetime
from unittest.mock import Mock, AsyncMock

from adapters.self_learning_system import (
    SelfLearningSystem, EpisodeEvent, MetricsCalculator, DecisionEngine,
    AbstractContextManager, AbstractContext, DerivedMetrics,
    FocusArea, InterfaceType, DatasetType
)


class TestMetricsCalculator:
    """Test the metrics calculation functionality"""
    
    def setup_method(self):
        self.calculator = MetricsCalculator()
    
    def test_metrics_calculator_initialization(self):
        """Test metrics calculator initializes correctly"""
        assert self.calculator.baseline_distributions == {}
        assert self.calculator.historical_metrics == []
    
    def test_calculate_derived_metrics(self):
        """Test calculation of derived metrics from episode"""
        episode = self._create_sample_episode()
        
        metrics = self.calculator.calculate_derived_metrics(episode)
        
        assert isinstance(metrics, DerivedMetrics)
        assert metrics.episode_id == f"{episode.agent_id}_{episode.scenario_id}_{episode.timestamp.isoformat()}"
        assert metrics.schema_mismatch_count == 0  # No mismatches in sample
        assert metrics.computed_at is not None
    
    def test_rmse_calculation(self):
        """Test RMSE calculation for numerical predictions"""
        episode = self._create_sample_episode()
        episode.actual_results = {
            "predicted_values": [0.8, 0.6, 0.9]
        }
        episode.kpis = {"metric1": 0.7, "metric2": 0.5, "metric3": 0.8}
        
        rmse = self.calculator._calculate_rmse(episode)
        
        assert rmse is not None
        assert isinstance(rmse, float)
        assert rmse >= 0
    
    def test_f1_score_calculation(self):
        """Test F1 score calculation"""
        episode = self._create_sample_episode()
        episode.actual_results = {
            "predicted_categories": ["A", "B", "A", "C"],
            "actual_categories": ["A", "B", "B", "C"]
        }
        
        f1 = self.calculator._calculate_f1_score(episode)
        
        assert f1 is not None
        assert isinstance(f1, float)
        assert 0 <= f1 <= 1
    
    def test_interface_error_rate_calculation(self):
        """Test interface error rate calculation"""
        episode = self._create_sample_episode()
        episode.interfaces_used = {
            InterfaceType.ERP: {"error_count": 2, "total_calls": 10},
            InterfaceType.CRM: {"error_count": 0, "total_calls": 5}
        }
        
        error_rates = self.calculator._calculate_interface_error_rates(episode)
        
        assert InterfaceType.ERP in error_rates
        assert error_rates[InterfaceType.ERP] == 0.2  # 2/10
        assert InterfaceType.CRM in error_rates
        assert error_rates[InterfaceType.CRM] == 0.0  # 0/5
    
    def _create_sample_episode(self):
        """Create a sample episode for testing"""
        return EpisodeEvent(
            agent_id="ceo_001",
            scenario_id="strategic_planning_001",
            timestamp=datetime.now(),
            source="test",
            correlation_ids=["test_correlation_1"],
            user_intent="Plan quarterly strategy",
            prompts=["What is the strategic direction for Q4?"],
            tool_calls=[{"tool": "market_analysis", "params": {}}],
            retrieved_context={"retrieved_items": 8, "total_queries": 10},
            third_party_payloads={},
            model_output="Based on market analysis, I recommend focusing on...",
            action_plan={"priority": "high", "timeline": "Q4"},
            selected_tools=["market_analysis"],
            confidence_scores={"strategy": 0.85, "timeline": 0.92},
            actual_results={"success": True, "implementation_rate": 0.87}
        )


class TestDecisionEngine:
    """Test the decision engine functionality"""
    
    def setup_method(self):
        self.engine = DecisionEngine()
    
    def test_decision_engine_initialization(self):
        """Test decision engine initializes with correct thresholds"""
        assert self.engine.thresholds["systematic_error_rate"] == 0.1
        assert self.engine.thresholds["prompt_sensitivity_index"] == 0.3
        assert self.engine.thresholds["interface_reliability"] == 0.95
        assert self.engine.thresholds["context_utility"] == 0.7
    
    def test_decide_focus_area_model(self):
        """Test decision for model focus area due to systematic errors"""
        metrics = DerivedMetrics(
            episode_id="test_episode",
            f1_score=0.5,  # Poor F1 score indicates systematic errors
            brier_score=0.15  # High Brier score
        )
        episode = self._create_sample_episode()
        
        focus_area = self.engine.decide_focus_area(metrics, episode)
        
        assert focus_area == FocusArea.MODEL
    
    def test_decide_focus_area_interface(self):
        """Test decision for interface focus area due to reliability issues"""
        metrics = DerivedMetrics(
            episode_id="test_episode",
            interface_error_rates={
                InterfaceType.ERP: 0.15  # High error rate
            }
        )
        episode = self._create_sample_episode()
        
        focus_area = self.engine.decide_focus_area(metrics, episode)
        
        assert focus_area == FocusArea.INTERFACE
    
    def test_decide_focus_area_context(self):
        """Test decision for context focus area due to utility issues"""
        metrics = DerivedMetrics(
            episode_id="test_episode",
            retrieval_hit_rate=0.5,  # Low hit rate
            conflict_density=0.4  # High conflict density
        )
        episode = self._create_sample_episode()
        
        focus_area = self.engine.decide_focus_area(metrics, episode)
        
        assert focus_area == FocusArea.CONTEXT
    
    def test_decide_focus_area_prompt(self):
        """Test decision for prompt focus area due to sensitivity issues"""
        metrics = DerivedMetrics(
            episode_id="test_episode",
            prompt_sensitivity_index=0.4  # High sensitivity
        )
        episode = self._create_sample_episode()
        
        focus_area = self.engine.decide_focus_area(metrics, episode)
        
        assert focus_area == FocusArea.PROMPT
    
    def _create_sample_episode(self):
        """Create a sample episode for testing"""
        return EpisodeEvent(
            agent_id="ceo_001",
            scenario_id="test_scenario",
            timestamp=datetime.now(),
            source="test",
            correlation_ids=[],
            user_intent="Test intent",
            prompts=["Test prompt"],
            tool_calls=[],
            retrieved_context={},
            third_party_payloads={},
            model_output="Test output",
            action_plan={},
            selected_tools=[],
            confidence_scores={},
            actual_results={}
        )


class TestAbstractContextManager:
    """Test the abstract context management functionality"""
    
    def setup_method(self):
        self.mock_mcp_client = AsyncMock()
        self.manager = AbstractContextManager(self.mock_mcp_client)
    
    def test_context_manager_initialization(self):
        """Test context manager initializes correctly"""
        assert self.manager.mcp_client == self.mock_mcp_client
        assert self.manager.contexts == {}
        assert self.manager.context_versions == {}
    
    @pytest.mark.asyncio
    async def test_update_context_comprehensive(self):
        """Test comprehensive context update"""
        episode = self._create_sample_episode()
        
        context = await self.manager.update_context_from_episode(
            episode, FocusArea.CONTEXT
        )
        
        assert context.agent_id == episode.agent_id
        assert episode.user_intent in context.commitments
        assert len(context.episode_summaries) > 0
        assert context.update_source == "comprehensive_update"
        
        # Verify MCP client was called
        self.mock_mcp_client.persist_context.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_context_incremental(self):
        """Test incremental context update"""
        episode = self._create_sample_episode()
        
        context = await self.manager.update_context_from_episode(
            episode, FocusArea.MODEL  # Non-context focus area
        )
        
        assert context.agent_id == episode.agent_id
        assert context.update_source == "incremental_update"
        
        # Verify MCP client was called
        self.mock_mcp_client.persist_context.assert_called_once()
    
    def test_detect_conflicts(self):
        """Test conflict detection in context"""
        context = AbstractContext(
            agent_id="ceo_001",
            commitments=["Increase market share", "Decrease spending"]
        )
        
        conflicts = self.manager.detect_conflicts(context)
        
        assert len(conflicts) > 0
        assert "Conflicting commitments" in conflicts[0]
    
    def test_no_conflicts_detected(self):
        """Test when no conflicts are present"""
        context = AbstractContext(
            agent_id="ceo_001",
            commitments=["Increase market share", "Improve customer satisfaction"]
        )
        
        conflicts = self.manager.detect_conflicts(context)
        
        assert len(conflicts) == 0
    
    def _create_sample_episode(self):
        """Create a sample episode for testing"""
        return EpisodeEvent(
            agent_id="ceo_001",
            scenario_id="strategic_planning",
            timestamp=datetime.now(),
            source="test",
            correlation_ids=["test_id"],
            user_intent="Develop growth strategy",
            prompts=["How should we grow?"],
            tool_calls=[],
            retrieved_context={},
            third_party_payloads={},
            model_output="Focus on market expansion",
            action_plan={"priority": "high"},
            selected_tools=[],
            confidence_scores={"strategy": 0.8},
            actual_results={"success": True},
            user_verdict="success",
            interfaces_used={InterfaceType.ERP: {"success_rate": 0.95}}
        )


class TestEnhancedSelfLearningSystem:
    """Test the enhanced self-learning system with audit-driven capabilities"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mock_lora_manager = Mock()
        self.mock_mcp_client = AsyncMock()
        
        self.system = SelfLearningSystem(
            data_dir=self.temp_dir,
            lora_manager=self.mock_lora_manager,
            mcp_client=self.mock_mcp_client
        )
    
    def teardown_method(self):
        """Clean up temporary directory"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_system_initialization(self):
        """Test system initializes with enhanced components"""
        assert isinstance(self.system.metrics_calculator, MetricsCalculator)
        assert isinstance(self.system.decision_engine, DecisionEngine)
        assert isinstance(self.system.context_manager, AbstractContextManager)
        
        assert self.system.episodes == {}
        assert self.system.derived_metrics == {}
        assert self.system.shadow_evaluations == {}
        assert self.system.rollback_points == {}
    
    @pytest.mark.asyncio
    async def test_process_episode_complete_flow(self):
        """Test complete episode processing flow"""
        episode = self._create_sample_episode()
        
        result = await self.system.process_episode(episode)
        
        assert "episode_id" in result
        assert "metrics" in result
        assert "focus_area" in result
        assert "changes_applied" in result
        assert "evaluation_result" in result
        
        # Verify episode was stored
        assert len(self.system.episodes) == 1
        assert len(self.system.derived_metrics) == 1
    
    @pytest.mark.asyncio
    async def test_episode_processing_with_context_focus(self):
        """Test episode processing that focuses on context updates"""
        episode = self._create_sample_episode()
        episode.retrieved_context = {
            "retrieved_items": 5, 
            "total_queries": 20,  # Low hit rate (5/20 = 0.25)
            "conflicts": 8, 
            "total_items": 15  # High conflict density (8/15 = 0.53)
        }
        
        result = await self.system.process_episode(episode)
        
        # Should focus on context due to low retrieval hit rate and high conflict density
        assert result["focus_area"] == FocusArea.CONTEXT.value
        assert result["changes_applied"]["context_updated"] is True
    
    @pytest.mark.asyncio
    async def test_episode_processing_with_model_focus(self):
        """Test episode processing that focuses on model fine-tuning"""
        episode = self._create_sample_episode()
        episode.actual_results = {
            "predicted_categories": ["A", "B"],
            "actual_categories": ["B", "A"]  # Poor predictions
        }
        # Remove interface data to avoid interface focus
        episode.interfaces_used = {}
        # Ensure good context metrics so it doesn't focus on context
        episode.retrieved_context = {
            "retrieved_items": 18, 
            "total_queries": 20,  # High hit rate
            "conflicts": 1, 
            "total_items": 15  # Low conflict density
        }
        
        result = await self.system.process_episode(episode)
        
        # Should focus on model due to poor prediction performance
        assert result["focus_area"] == FocusArea.MODEL.value
    
    @pytest.mark.asyncio
    async def test_rollback_mechanism(self):
        """Test that rollback works when evaluation fails"""
        episode = self._create_sample_episode()
        
        # Mock shadow evaluation to return poor results
        original_shadow_evaluate = self.system._shadow_evaluate
        async def mock_shadow_evaluate(agent_id, episode):
            return {
                "improvement": -0.05,  # Negative improvement
                "confidence_interval": [-0.1, 0.0]  # No significant improvement
            }
        self.system._shadow_evaluate = mock_shadow_evaluate
        
        result = await self.system.process_episode(episode)
        
        assert result["changes_applied"]["rolled_back"] is True
        
        # Restore original method
        self.system._shadow_evaluate = original_shadow_evaluate
    
    @pytest.mark.asyncio
    async def test_interface_reliability_tracking(self):
        """Test interface reliability tracking and fixing"""
        episode = self._create_sample_episode()
        episode.interfaces_used = {
            InterfaceType.ERP: {"error_count": 3, "total_calls": 10},  # High error rate
            InterfaceType.CRM: {"error_count": 0, "total_calls": 5}
        }
        
        result = await self.system.process_episode(episode)
        
        # Should detect interface issues
        metrics = result["metrics"]
        assert InterfaceType.ERP in metrics.interface_error_rates
        assert metrics.interface_error_rates[InterfaceType.ERP] == 0.3
    
    @pytest.mark.asyncio
    async def test_episode_persistence(self):
        """Test that episodes are properly saved and loaded"""
        episode1 = self._create_sample_episode()
        episode1.agent_id = "ceo_001"
        
        episode2 = self._create_sample_episode()
        episode2.agent_id = "cfo_001"
        
        # Process episodes
        await self.system.process_episode(episode1)
        await self.system.process_episode(episode2)
        
        # Verify both episodes are stored
        assert len(self.system.episodes) == 2
        
        # Create new system instance to test loading
        new_system = SelfLearningSystem(
            data_dir=self.temp_dir,
            lora_manager=self.mock_lora_manager,
            mcp_client=self.mock_mcp_client
        )
        
        # Should load the saved episodes
        assert len(new_system.episodes) == 2
    
    def _create_sample_episode(self):
        """Create a sample episode for testing"""
        return EpisodeEvent(
            agent_id="ceo_001",
            scenario_id="test_scenario_001",
            timestamp=datetime.now(),
            source="test_suite",
            correlation_ids=["test_correlation"],
            user_intent="Execute strategic initiative",
            prompts=["What is the best approach for this initiative?"],
            tool_calls=[{"tool": "strategic_analysis", "params": {"depth": "comprehensive"}}],
            retrieved_context={"retrieved_items": 15, "total_queries": 20, "conflicts": 2, "total_items": 15},
            third_party_payloads={"erp_data": {"budget": 100000}},
            model_output="I recommend a phased approach starting with market research...",
            action_plan={
                "phase1": "Market research",
                "phase2": "Product development",
                "timeline": "6 months"
            },
            selected_tools=["strategic_analysis", "market_research"],
            confidence_scores={"strategy": 0.85, "timeline": 0.78, "budget": 0.92},
            actual_results={
                "implementation_success": True,
                "budget_accuracy": 0.87,
                "timeline_accuracy": 0.82,
                "predicted_values": [0.85, 0.78, 0.92],
                "actual_text": "The phased approach was successfully implemented..."
            },
            user_verdict="success",
            mentor_verdict="approved",
            kpis={
                "roi": 0.85,
                "customer_satisfaction": 0.78,
                "market_share": 0.92
            },
            stakeholder_ratings={"board": 0.9, "investors": 0.85, "employees": 0.8},
            mentor_annotations=["Good strategic thinking", "Consider risk mitigation"],
            categorical_tags=["strategic_planning", "growth_initiative", "approved"],
            suggested_corrections=["Add more detailed risk analysis"],
            context_updates={"strategic_priorities": ["growth", "efficiency"]},
            mcp_object_refs=["context_strategic_001", "knowledge_growth_001"],
            interfaces_used={
                InterfaceType.ERP: {"error_count": 0, "total_calls": 5, "success_rate": 1.0},
                InterfaceType.CRM: {"error_count": 1, "total_calls": 8, "success_rate": 0.875}
            },
            schema_versions={"erp": "v2.1", "crm": "v1.8"}
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])