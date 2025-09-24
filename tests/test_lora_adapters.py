"""
Tests for Business Infinity LoRA Adapter System

Tests all components of the adapter system including:
- LoRA adapter loading and orchestration
- Self-learning system functionality
- Model upgrade management
- Evaluation harness metrics
- Integration with autonomous boardroom
"""

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
    initialize_adapter_system,
    generate_boardroom_response,
    evaluate_boardroom_response,
    BoardroomRole,
    AdapterType,
    LearningPhase,
    UpgradeStatus,
    MetricType
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])