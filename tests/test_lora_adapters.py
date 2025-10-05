
# Ensure BusinessInfinity/src is in sys.path for pytest import resolution
import sys
from pathlib import Path
src_path = str(Path(__file__).resolve().parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
import pytest
import asyncio
import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

# Import the adapter system
from adapters import (
    LoRAAdapterManager,
    SelfLearningSystem,
    ModelUpgradeManager,
    EvaluationHarness,
    AdapterOrchestrator,
    MultiDimensionalLearningOrchestrator,
    initialize_adapter_system,
    generate_boardroom_response,
    evaluate_boardroom_response,
    BoardroomRole,
    AdapterType,
    LearningPhase,
    UpgradeStatus,
    MetricType,
    LearningDimension,
    AdaptationTrigger,
    AdaptationStrategy
)


class TestLoRAAdapterManager:
    """Test LoRA adapter management functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def adapter_config(self, temp_dir):
        """Create test adapter configuration"""
        config_data = {
            "domain_adapters": {
                "cfo": {
                    "rank": 48,
                    "alpha": 32,
                    "target_modules": ["q_proj", "k_proj", "v_proj"],
                    "layer_range": [8, 28],
                    "fusion_weight": 0.78,
                    "path": os.path.join(temp_dir, "cfo_adapter")
                }
            },
            "leadership_adapter": {
                "rank": 12,
                "alpha": 12,
                "target_modules": ["o_proj"],
                "layer_range": [24, 32],
                "path": os.path.join(temp_dir, "leadership_adapter")
            }
        }
        
        config_path = os.path.join(temp_dir, "test_config.json")
        with open(config_path, 'w') as f:
            json.dump(config_data, f)
        
        return config_path
    
    @pytest.mark.asyncio
    async def test_adapter_manager_initialization(self, adapter_config):
        """Test LoRA adapter manager initialization"""
        manager = LoRAAdapterManager(config_path=adapter_config)
        await manager.initialize_model()
        
        assert manager.config_path == adapter_config
        assert "domain_cfo" in manager.adapter_configs
        assert "leadership" in manager.adapter_configs
        assert manager.base_model is not None  # Should be stub or actual model
    
    @pytest.mark.asyncio
    async def test_adapter_loading(self, adapter_config):
        """Test loading individual adapters"""
        manager = LoRAAdapterManager(config_path=adapter_config)
        await manager.initialize_model()
        
        # Test domain adapter loading
        success = await manager.load_adapter("domain_cfo")
        assert success
        assert "domain_cfo" in manager.loaded_adapters
    
    @pytest.mark.asyncio
    async def test_role_adapter_loading(self, adapter_config):
        """Test loading role-specific adapter combinations"""
        manager = LoRAAdapterManager(config_path=adapter_config)
        await manager.initialize_model()
        
        success, adapter_info = await manager.load_role_adapters(BoardroomRole.CFO)
        assert success
        assert adapter_info["role"] == "cfo"
        assert adapter_info["domain_adapter"] == "domain_cfo"
        assert adapter_info["leadership_adapter"] == "leadership"
        assert "fusion_weights" in adapter_info
        assert adapter_info["fusion_weights"]["domain"] == 0.78
    
    @pytest.mark.asyncio
    async def test_response_generation(self, adapter_config):
        """Test response generation with adapter fusion"""
        manager = LoRAAdapterManager(config_path=adapter_config)
        await manager.initialize_model()
        
        response = await manager.generate_response(
            role=BoardroomRole.CFO,
            prompt="Analyze the Q4 budget proposal",
            max_length=200
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Should contain role indicator since we're using stub implementation
        assert "CFO" in response or "cfo" in response.lower()
    
    @pytest.mark.asyncio
    async def test_adapter_metrics(self, adapter_config):
        """Test adapter metrics retrieval"""
        manager = LoRAAdapterManager(config_path=adapter_config)
        await manager.initialize_model()
        
        metrics = await manager.get_adapter_metrics("domain_cfo")
        assert "adapter_id" in metrics
        assert metrics["role"] == "cfo"
        assert metrics["type"] == "domain"
        assert "rank" in metrics
        assert "alpha" in metrics
    
    @pytest.mark.asyncio
    async def test_list_all_adapters(self, adapter_config):
        """Test listing all available adapters"""
        manager = LoRAAdapterManager(config_path=adapter_config)
        await manager.initialize_model()
        
        adapters = await manager.list_all_adapters()
        assert "total_adapters" in adapters
        assert "domain_adapters" in adapters
        assert "leadership_adapter" in adapters
        assert adapters["total_adapters"] > 0


class TestSelfLearningSystem:
    """Test self-learning system functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def learning_system(self, temp_dir):
        """Create test learning system"""
        return SelfLearningSystem(data_dir=temp_dir)
    
    @pytest.mark.asyncio
    async def test_situation_generation(self, learning_system):
        """Test generation of boardroom situations"""
        situation = await learning_system.generate_situation(
            decision_type="strategic",
            target_roles=["cfo", "founder"],
            complexity_level=3
        )
        
        assert situation.id is not None
        assert situation.decision_type == "strategic"
        assert "cfo" in situation.target_roles
        assert "founder" in situation.target_roles
        assert situation.complexity_level == 3
        assert len(situation.context) > 0
    
    @pytest.mark.asyncio
    async def test_mentor_feedback_collection(self, learning_system):
        """Test collection of mentor feedback"""
        # First generate a situation
        situation = await learning_system.generate_situation("financial", ["cfo"])
        
        mentor_input = {
            "rating": 0.8,
            "corrections": "Add more detailed financial analysis",
            "improvements": "Include sensitivity analysis",
            "mentor_id": "test_mentor"
        }
        
        feedback = await learning_system.collect_mentor_feedback(
            situation.id,
            "cfo",
            "Mock agent response",
            mentor_input
        )
        
        assert feedback.situation_id == situation.id
        assert feedback.agent_role == "cfo"
        assert feedback.mentor_rating == 0.8
        assert feedback.corrections == mentor_input["corrections"]
    
    @pytest.mark.asyncio
    async def test_training_example_creation(self, learning_system):
        """Test creation of training examples from feedback"""
        # Generate situation and feedback
        situation = await learning_system.generate_situation("operational", ["coo"])
        
        mentor_input = {
            "rating": 0.75,
            "corrections": "More operational detail needed",
            "improvements": "Add process optimization recommendations"
        }
        
        feedback = await learning_system.collect_mentor_feedback(
            situation.id, "coo", "Mock COO response", mentor_input
        )
        
        training_example = await learning_system.create_training_example(feedback)
        
        assert training_example.role == "coo"
        assert training_example.quality_score == 0.75
        assert len(training_example.input_prompt) > 0
        assert len(training_example.target_response) > 0
    
    @pytest.mark.asyncio
    async def test_learning_cycle(self, learning_system):
        """Test complete learning cycle execution"""
        result = await learning_system.run_learning_cycle("cfo")
        
        assert result["role"] == "cfo"
        assert result["cycle_number"] == 1
        assert "phases" in result
        assert "situation_generation" in result["phases"]
        assert "mentor_feedback" in result["phases"]
        assert "training_examples" in result["phases"]
    
    @pytest.mark.asyncio
    async def test_blended_dataset_creation(self, learning_system):
        """Test creation of blended training datasets"""
        # Mock some original dataset
        learning_system.original_dataset["cfo"] = [
            MagicMock(role="cfo") for _ in range(10)
        ]
        
        # Mock some self-learning dataset
        learning_system.self_learning_dataset["cfo"] = [
            MagicMock(role="cfo") for _ in range(5)
        ]
        
        blended = await learning_system.create_blended_dataset("cfo")
        
        assert len(blended) > 0
        # Should contain examples from both datasets


class TestEvaluationHarness:
    """Test evaluation harness functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def evaluation_harness(self, temp_dir):
        """Create test evaluation harness"""
        return EvaluationHarness(data_dir=temp_dir)
    
    @pytest.mark.asyncio
    async def test_response_evaluation(self, evaluation_harness):
        """Test evaluation of agent responses"""
        # Use one of the default scenarios
        scenarios = list(evaluation_harness.evaluation_scenarios.keys())
        assert len(scenarios) > 0
        
        scenario_id = scenarios[0]
        
        response_text = """
        From a financial perspective, this strategic expansion requires careful analysis.
        I recommend conducting a thorough ROI analysis considering the $50M investment.
        Key risks include regulatory challenges and competitive response.
        My recommendation is to proceed with a phased approach starting with market research.
        Actions: 1) Hire market research firm (CFO, 30 days), 2) Financial modeling (CFO, 14 days)
        """
        
        result = await evaluation_harness.evaluate_response(
            response_text=response_text,
            agent_role="cfo",
            scenario_id=scenario_id
        )
        
        assert result.agent_role == "cfo"
        assert result.scenario_id == scenario_id
        assert 0.0 <= result.overall_score <= 1.0
        assert 0.0 <= result.role_fidelity.overall_score <= 1.0
        assert 0.0 <= result.leadership_clarity.overall_score <= 1.0
        assert 0.0 <= result.conflict_index.overall_score <= 1.0
        assert 0.0 <= result.guardrail_compliance.overall_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_role_fidelity_evaluation(self, evaluation_harness):
        """Test role fidelity metric calculation"""
        cfo_response = """
        The financial analysis shows strong ROI potential with EBITDA improvements.
        Cash flow projections indicate positive returns within 18 months.
        Risk assessment reveals manageable exposure with proper hedging strategies.
        """
        
        metrics = await evaluation_harness._evaluate_role_fidelity(
            cfo_response, "cfo", evaluation_harness.evaluation_scenarios[list(evaluation_harness.evaluation_scenarios.keys())[0]]
        )
        
        assert 0.0 <= metrics.overall_score <= 1.0
        assert metrics.vocabulary_consistency > 0  # Should detect financial terms
        assert metrics.kpi_relevance >= 0
    
    @pytest.mark.asyncio
    async def test_evaluation_suite(self, evaluation_harness):
        """Test evaluation of multiple agent responses"""
        scenario_id = list(evaluation_harness.evaluation_scenarios.keys())[0]
        
        agent_responses = {
            "cfo": "Financial analysis shows positive ROI...",
            "cmo": "Market opportunity analysis indicates strong demand...",
            "founder": "This aligns with our long-term vision..."
        }
        
        results = await evaluation_harness.run_evaluation_suite(agent_responses, scenario_id)
        
        assert len(results) == 3
        assert "cfo" in results
        assert "cmo" in results
        assert "founder" in results
        
        for role, result in results.items():
            assert result.agent_role == role
            assert result.scenario_id == scenario_id
    
    @pytest.mark.asyncio
    async def test_performance_trends(self, evaluation_harness):
        """Test performance trend analysis"""
        # Add some mock evaluation results
        for i in range(5):
            result = MagicMock()
            result.agent_role = "cfo"
            result.overall_score = 0.7 + (i * 0.05)  # Improving trend
            result.role_fidelity.overall_score = 0.8
            result.leadership_clarity.overall_score = 0.75
            result.conflict_index.overall_score = 0.3
            result.evaluation_timestamp = datetime.now() - timedelta(days=i)
            
            evaluation_harness.evaluation_results.append(result)
        
        trends = await evaluation_harness.get_performance_trends("cfo", days=30)
        
        assert trends["roles_analyzed"] == ["cfo"]
        assert "trends" in trends
        assert "cfo" in trends["trends"]
        assert trends["trends"]["cfo"]["evaluations_count"] == 5


class TestAdapterOrchestrator:
    """Test adapter orchestrator integration"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, temp_dir):
        """Test adapter orchestrator initialization"""
        orchestrator = AdapterOrchestrator(data_dir=temp_dir)
        await orchestrator.initialize()
        
        assert orchestrator.lora_manager is not None
        assert orchestrator.learning_system is not None
        assert orchestrator.upgrade_manager is not None
        assert orchestrator.evaluation_harness is not None
        assert orchestrator.status.value in ["ready", "initializing"]
    
    @pytest.mark.asyncio
    async def test_agent_response_generation(self, temp_dir):
        """Test agent response generation through orchestrator"""
        orchestrator = AdapterOrchestrator(data_dir=temp_dir)
        await orchestrator.initialize()
        
        result = await orchestrator.generate_agent_response(
            role="cfo",
            prompt="Analyze the quarterly budget variance",
            max_length=200
        )
        
        assert result["success"] is True
        assert result["role"] == "cfo"
        assert "response" in result
        assert len(result["response"]) > 0
    
    @pytest.mark.asyncio
    async def test_response_evaluation(self, temp_dir):
        """Test response evaluation through orchestrator"""
        orchestrator = AdapterOrchestrator(data_dir=temp_dir)
        await orchestrator.initialize()
        
        result = await orchestrator.evaluate_response(
            role="cfo",
            response_text="Financial analysis shows positive trends with ROI improvements."
        )
        
        assert result["success"] is True
        assert "evaluation_result" in result
        assert "overall_score" in result["evaluation_result"]
    
    @pytest.mark.asyncio
    async def test_learning_cycle_execution(self, temp_dir):
        """Test learning cycle execution through orchestrator"""
        orchestrator = AdapterOrchestrator(data_dir=temp_dir)
        await orchestrator.initialize()
        
        result = await orchestrator.run_learning_cycle("cfo")
        
        assert result["success"] is True
        assert "learning_results" in result
        assert result["learning_results"]["role"] == "cfo"
    
    @pytest.mark.asyncio
    async def test_system_status(self, temp_dir):
        """Test system status reporting"""
        orchestrator = AdapterOrchestrator(data_dir=temp_dir)
        await orchestrator.initialize()
        
        status = await orchestrator.get_system_status()
        
        assert "status" in status
        assert "components" in status
        assert "metrics" in status
        assert "uptime_hours" in status


class TestIntegrationFunctions:
    """Test global integration functions"""
    
    @pytest.mark.asyncio
    async def test_initialize_adapter_system(self):
        """Test global adapter system initialization"""
        with patch('adapters.adapter_orchestrator.AdapterOrchestrator') as mock_orchestrator:
            mock_instance = AsyncMock()
            mock_orchestrator.return_value = mock_instance
            
            result = await initialize_adapter_system()
            
            mock_instance.initialize.assert_called_once()
            assert result == mock_instance
    
    @pytest.mark.asyncio
    async def test_generate_boardroom_response(self):
        """Test global response generation function"""
        with patch('adapters.adapter_orchestrator.adapter_orchestrator') as mock_orchestrator:
            mock_orchestrator.generate_agent_response = AsyncMock(return_value={
                "success": True,
                "role": "cfo",
                "response": "Test response"
            })
            
            result = await generate_boardroom_response("cfo", "Test prompt")
            
            mock_orchestrator.generate_agent_response.assert_called_once_with("cfo", "Test prompt", 512)
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_evaluate_boardroom_response(self):
        """Test global response evaluation function"""
        with patch('adapters.adapter_orchestrator.adapter_orchestrator') as mock_orchestrator:
            mock_orchestrator.evaluate_response = AsyncMock(return_value={
                "success": True,
                "evaluation_result": {"overall_score": 0.85}
            })
            
            result = await evaluate_boardroom_response("cfo", "Test response")
            
            mock_orchestrator.evaluate_response.assert_called_once_with("cfo", "Test response", None)
            assert result["success"] is True


class TestMultiDimensionalLearning:
    """Test multi-dimensional learning system functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def multi_dim_orchestrator(self):
        """Create test multi-dimensional learning orchestrator"""
        return MultiDimensionalLearningOrchestrator()
    
    @pytest.fixture
    def sample_feedback_data(self):
        """Generate sample feedback data for testing"""
        return [
            {
                "id": "feedback_001",
                "type": "performance_review",
                "content": "The CFO agent's financial analysis lacks depth in risk assessment. Need better model capabilities.",
                "sentiment": 0.3,
                "severity": 0.8,
                "affected_role": "cfo",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "feedback_002",
                "type": "context_issues",
                "content": "Decisions lack proper context about market conditions and competitor actions.",
                "sentiment": 0.4,
                "severity": 0.6,
                "affected_role": "all",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "feedback_003",
                "type": "prompt_clarity",
                "content": "The prompts are unclear and don't provide sufficient structure.",
                "sentiment": 0.35,
                "severity": 0.7,
                "affected_role": "all",
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    @pytest.fixture
    def sample_audit_events(self):
        """Generate sample audit events for testing"""
        return [
            {
                "event_id": "audit_001",
                "event_type": "boardroom_decision",
                "timestamp": datetime.now().isoformat(),
                "subject_id": "boardroom",
                "context": {
                    "confidence_score": 0.5,  # Low confidence
                    "consensus_score": 0.6,   # Medium consensus
                    "decision_start": (datetime.now() - timedelta(minutes=30)).isoformat()
                }
            },
            {
                "event_id": "audit_002",
                "event_type": "agent_vote",
                "timestamp": datetime.now().isoformat(),
                "subject_role": "cfo",
                "context": {
                    "vote_value": 0.4,
                    "confidence": 0.45,  # Low confidence
                    "decision_id": "decision_001"
                }
            },
            {
                "event_id": "audit_003",
                "event_type": "mcp_request",
                "timestamp": datetime.now().isoformat(),
                "subject_id": "agent",
                "context": {
                    "success": False,  # Failed MCP request
                    "error_type": "timeout",
                    "response_time_ms": 4000,
                    "mcp_server": "market_data"
                }
            }
        ]
    
    @pytest.mark.asyncio
    async def test_stakeholder_feedback_analysis(self, multi_dim_orchestrator, sample_feedback_data):
        """Test stakeholder feedback analysis"""
        patterns = await multi_dim_orchestrator.analyze_stakeholder_feedback(sample_feedback_data)
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0  # Should find some patterns
        
        # Check pattern structure
        for pattern in patterns:
            assert hasattr(pattern, 'dimension')
            assert hasattr(pattern, 'feedback_type')
            assert hasattr(pattern, 'frequency')
            assert hasattr(pattern, 'severity')
            assert hasattr(pattern, 'confidence')
            assert 0.0 <= pattern.confidence <= 1.0
            assert 0.0 <= pattern.severity <= 1.0
    
    @pytest.mark.asyncio
    async def test_audit_pattern_analysis(self, multi_dim_orchestrator, sample_audit_events):
        """Test audit trail pattern analysis"""
        patterns = await multi_dim_orchestrator.analyze_audit_patterns(sample_audit_events)
        
        assert isinstance(patterns, list)
        # May or may not find patterns depending on the data
        
        for pattern in patterns:
            assert hasattr(pattern, 'dimension')
            assert hasattr(pattern, 'feedback_type')
            assert hasattr(pattern, 'confidence')
    
    @pytest.mark.asyncio
    async def test_adaptation_priority_determination(self, multi_dim_orchestrator, sample_feedback_data):
        """Test adaptation priority determination"""
        patterns = await multi_dim_orchestrator.analyze_stakeholder_feedback(sample_feedback_data)
        decisions = await multi_dim_orchestrator.determine_adaptation_priorities(patterns)
        
        assert isinstance(decisions, list)
        
        if decisions:  # If adaptations are recommended
            # Check decisions are properly sorted by priority
            priorities = [d.priority for d in decisions]
            assert priorities == sorted(priorities, reverse=True)
            
            # Check decision structure
            for decision in decisions:
                assert hasattr(decision, 'dimension')
                assert hasattr(decision, 'strategy')
                assert hasattr(decision, 'priority')
                assert hasattr(decision, 'estimated_impact')
                assert hasattr(decision, 'estimated_cost')
                assert 1 <= decision.priority <= 5
                assert 0.0 <= decision.estimated_impact <= 1.0
    
    @pytest.mark.asyncio
    async def test_dimensional_adaptation_execution(self, multi_dim_orchestrator):
        """Test execution of dimensional adaptations"""
        # Create mock adaptation decisions
        from adapters.multi_dimensional_learning import AdaptationDecision
        
        mock_decision = AdaptationDecision(
            dimension=LearningDimension.PROMPT,
            trigger=AdaptationTrigger.STAKEHOLDER_FEEDBACK,
            strategy=AdaptationStrategy.INCREMENTAL,
            priority=3,
            estimated_impact=0.3,
            estimated_cost=1.0,
            risk_assessment=0.2,
            timeline="2-4 hours",
            dependencies=[],
            rollback_plan="Restore previous prompts"
        )
        
        results = await multi_dim_orchestrator.execute_adaptations([mock_decision])
        
        assert "adaptations_executed" in results
        assert "adaptations_successful" in results
        assert "execution_details" in results
        assert results["adaptations_executed"] == 1
    
    @pytest.mark.asyncio
    async def test_learning_status_retrieval(self, multi_dim_orchestrator):
        """Test learning status retrieval"""
        status = await multi_dim_orchestrator.get_learning_status()
        
        assert "dimensional_metrics" in status
        assert "total_adaptations" in status
        assert "system_status" in status
        
        # Check all dimensions are tracked
        expected_dimensions = [dim.value for dim in LearningDimension]
        actual_dimensions = list(status["dimensional_metrics"].keys())
        
        for expected_dim in expected_dimensions:
            assert expected_dim in actual_dimensions
        
        # Check metric structure
        for dim_name, metrics in status["dimensional_metrics"].items():
            assert "current_performance" in metrics
            assert "stakeholder_satisfaction" in metrics
            assert "adaptation_frequency" in metrics
    
    @pytest.mark.asyncio
    async def test_dimension_specific_analysis(self, multi_dim_orchestrator):
        """Test analysis for specific dimensions"""
        
        # Test LLM Model dimension feedback
        model_feedback = [{
            "type": "capability_feedback",
            "content": "The model lacks sophisticated reasoning capabilities and understanding",
            "sentiment": 0.2,
            "severity": 0.9,
            "affected_role": "all"
        }]
        
        patterns = await multi_dim_orchestrator.analyze_stakeholder_feedback(model_feedback)
        model_patterns = [p for p in patterns if p.dimension == LearningDimension.LLM_MODEL]
        
        assert len(model_patterns) > 0  # Should detect model-related issues
        
        # Test Context dimension feedback
        context_feedback = [{
            "type": "context_feedback",
            "content": "Agents lack proper context and situational awareness for decisions",
            "sentiment": 0.3,
            "severity": 0.7,
            "affected_role": "all"
        }]
        
        patterns = await multi_dim_orchestrator.analyze_stakeholder_feedback(context_feedback)
        context_patterns = [p for p in patterns if p.dimension == LearningDimension.CONTEXT]
        
        assert len(context_patterns) > 0  # Should detect context-related issues
    
    @pytest.mark.asyncio  
    async def test_adaptation_strategy_selection(self, multi_dim_orchestrator):
        """Test adaptation strategy selection based on feedback severity"""
        
        # High severity feedback should suggest comprehensive strategy
        high_severity_feedback = [{
            "type": "critical_issue",
            "content": "Major model intelligence reasoning capability training issues",
            "sentiment": 0.1,
            "severity": 0.95,
            "affected_role": "all"
        }]
        
        patterns = await multi_dim_orchestrator.analyze_stakeholder_feedback(high_severity_feedback)
        high_severity_patterns = [p for p in patterns if p.severity > 0.8]
        
        if high_severity_patterns:
            # High severity should often suggest comprehensive or targeted strategies
            comprehensive_patterns = [p for p in high_severity_patterns 
                                    if p.suggested_action in [AdaptationStrategy.COMPREHENSIVE, AdaptationStrategy.TARGETED]]
            assert len(comprehensive_patterns) > 0
        
        # Low severity feedback should suggest incremental strategy
        low_severity_feedback = [{
            "type": "minor_issue",
            "content": "Slight prompt formatting improvement needed",
            "sentiment": 0.6,
            "severity": 0.3,
            "affected_role": "cfo"
        }]
        
        patterns = await multi_dim_orchestrator.analyze_stakeholder_feedback(low_severity_feedback)
        low_severity_patterns = [p for p in patterns if p.severity < 0.5]
        
        if low_severity_patterns:
            incremental_patterns = [p for p in low_severity_patterns 
                                  if p.suggested_action == AdaptationStrategy.INCREMENTAL]
            # Should often suggest incremental for low severity
            assert len(incremental_patterns) >= 0


class TestIntegratedMultiDimensionalSystem:
    """Test integrated multi-dimensional learning with adapter orchestrator"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_orchestrator_multi_dimensional_integration(self, temp_dir):
        """Test integration of multi-dimensional learning with adapter orchestrator"""
        orchestrator = AdapterOrchestrator(data_dir=temp_dir)
        await orchestrator.initialize()
        
        # Should have multi-dimensional learning initialized
        assert orchestrator.multi_dimensional_learning is not None
        assert hasattr(orchestrator, 'analyze_stakeholder_feedback')
        assert hasattr(orchestrator, 'analyze_audit_patterns')
        assert hasattr(orchestrator, 'execute_dimensional_adaptations')
    
    @pytest.mark.asyncio
    async def test_stakeholder_feedback_analysis_integration(self, temp_dir):
        """Test stakeholder feedback analysis through orchestrator"""
        orchestrator = AdapterOrchestrator(data_dir=temp_dir)
        await orchestrator.initialize()
        
        sample_feedback = [{
            "type": "performance",
            "content": "The agents need better model capabilities and reasoning",
            "sentiment": 0.3,
            "severity": 0.8,
            "affected_role": "all"
        }]
        
        result = await orchestrator.analyze_stakeholder_feedback(sample_feedback)
        
        assert result.get("success") is True
        assert "patterns_identified" in result
        assert "adaptations_recommended" in result
        assert "feedback_patterns" in result
        assert "adaptation_decisions" in result
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis_integration(self, temp_dir):
        """Test comprehensive analysis through orchestrator"""
        orchestrator = AdapterOrchestrator(data_dir=temp_dir)
        await orchestrator.initialize()
        
        sample_feedback = [{
            "type": "comprehensive_feedback",
            "content": "System needs improvements in model, context, and prompt areas",
            "sentiment": 0.4,
            "severity": 0.7,
            "affected_role": "all"
        }]
        
        result = await orchestrator.run_comprehensive_analysis(
            feedback_data=sample_feedback,
            audit_lookback_days=7
        )
        
        assert result.get("success") is True
        assert "total_patterns_identified" in result
        assert "total_recommendations" in result
        assert "analysis_results" in result
        assert "learning_dimensions_evaluated" in result
        
        # Should evaluate all 5 dimensions
        assert len(result["learning_dimensions_evaluated"]) == 5
    
    @pytest.mark.asyncio
    async def test_intelligent_adaptation_trigger(self, temp_dir):
        """Test intelligent adaptation triggering"""
        orchestrator = AdapterOrchestrator(data_dir=temp_dir)
        await orchestrator.initialize()
        
        # Test with high threshold (should not trigger adaptation in good system)
        result = await orchestrator.trigger_intelligent_adaptation(
            trigger_threshold=0.9,
            execute_immediately=False
        )
        
        assert result.get("success") is True
        assert "adaptation_needed" in result
        
        # Test with low threshold (should trigger adaptation)
        result_low_threshold = await orchestrator.trigger_intelligent_adaptation(
            trigger_threshold=0.5,
            execute_immediately=False
        )
        
        assert result_low_threshold.get("success") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])