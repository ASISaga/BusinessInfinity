"""
Tests for AOS Agent Framework System

Tests the migration from Semantic Kernel to Microsoft Agent Framework.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

# Import the AOS Agent Framework components
from AgentOperatingSystem.agents.agent_framework_system import AgentFrameworkSystem
from AgentOperatingSystem.agents.multi_agent import MultiAgentSystem
from AgentOperatingSystem.orchestration.workflow_orchestrator import WorkflowOrchestrator, WorkflowOrchestratorFactory


class TestAgentFrameworkSystem:
    """Test the Agent Framework System implementation"""
    
    @pytest.fixture
    def agent_framework_system(self):
        """Create an Agent Framework System instance for testing"""
        return AgentFrameworkSystem()
    
    @pytest.mark.asyncio
    async def test_initialization(self, agent_framework_system):
        """Test Agent Framework System initialization"""
        # Mock the Agent Framework dependencies
        with patch('AgentOperatingSystem.agents.agent_framework_system.AGENT_FRAMEWORK_AVAILABLE', True):
            with patch('AgentOperatingSystem.agents.agent_framework_system.setup_telemetry') as mock_telemetry:
                mock_telemetry.return_value = None
                
                await agent_framework_system.initialize()
                
                assert agent_framework_system.is_initialized
                assert len(agent_framework_system.agents) >= 3  # Default agents
                mock_telemetry.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_agent(self, agent_framework_system):
        """Test creating a new agent"""
        with patch('AgentOperatingSystem.agents.agent_framework_system.AGENT_FRAMEWORK_AVAILABLE', True):
            with patch('AgentOperatingSystem.agents.agent_framework_system.ChatAgent') as mock_chat_agent:
                mock_agent = Mock()
                mock_agent.name = "TestAgent"
                mock_chat_agent.return_value = mock_agent
                
                await agent_framework_system.initialize()
                
                agent = await agent_framework_system.create_agent(
                    "TestAgent",
                    "Test instructions",
                    ["test_capability"]
                )
                
                assert agent.name == "TestAgent"
                assert "TestAgent" in agent_framework_system.agents
    
    @pytest.mark.asyncio
    async def test_run_multi_agent_conversation(self, agent_framework_system):
        """Test running a multi-agent conversation"""
        with patch('AgentOperatingSystem.agents.agent_framework_system.AGENT_FRAMEWORK_AVAILABLE', True):
            with patch('AgentOperatingSystem.agents.agent_framework_system.WorkflowBuilder') as mock_workflow_builder:
                mock_workflow = Mock()
                mock_workflow.execute = AsyncMock(return_value="Test result")
                
                mock_builder = Mock()
                mock_builder.add_agent.return_value = mock_builder
                mock_builder.build_sequential_workflow.return_value = mock_workflow
                mock_workflow_builder.return_value = mock_builder
                
                await agent_framework_system.initialize()
                
                result = await agent_framework_system.run_multi_agent_conversation(
                    "Test message",
                    ["BusinessAnalyst"]
                )
                
                assert result["success"] is True
                assert "result" in result
    
    @pytest.mark.asyncio
    async def test_remove_agent(self, agent_framework_system):
        """Test removing an agent"""
        with patch('AgentOperatingSystem.agents.agent_framework_system.AGENT_FRAMEWORK_AVAILABLE', True):
            await agent_framework_system.initialize()
            
            # Assume BusinessAnalyst was created during initialization
            assert "BusinessAnalyst" in agent_framework_system.agents
            
            removed = await agent_framework_system.remove_agent("BusinessAnalyst")
            
            assert removed is True
            assert "BusinessAnalyst" not in agent_framework_system.agents
    
    def test_get_statistics(self, agent_framework_system):
        """Test getting system statistics"""
        stats = agent_framework_system.get_statistics()
        
        assert "total_conversations" in stats
        assert "framework" in stats
        assert stats["framework"] == "Microsoft Agent Framework"


class TestMultiAgentSystem:
    """Test the updated Multi-Agent System"""
    
    @pytest.fixture
    def multi_agent_system(self):
        """Create a Multi-Agent System instance for testing"""
        return MultiAgentSystem()
    
    @pytest.mark.asyncio
    async def test_initialization_with_agent_framework(self, multi_agent_system):
        """Test Multi-Agent System initialization with Agent Framework"""
        with patch('AgentOperatingSystem.agents.multi_agent.AGENT_FRAMEWORK_AVAILABLE', True):
            with patch.object(multi_agent_system.agent_framework_system, 'initialize') as mock_init:
                mock_init.return_value = None
                
                await multi_agent_system.initialize()
                
                assert multi_agent_system.is_initialized
                mock_init.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_conversation_delegates_to_agent_framework(self, multi_agent_system):
        """Test that conversation execution delegates to Agent Framework system"""
        with patch('AgentOperatingSystem.agents.multi_agent.AGENT_FRAMEWORK_AVAILABLE', True):
            mock_result = {"success": True, "result": "test"}
            
            with patch.object(multi_agent_system.agent_framework_system, 'run_multi_agent_conversation') as mock_run:
                mock_run.return_value = mock_result
                
                await multi_agent_system.initialize()
                result = await multi_agent_system.run_multi_agent_conversation("test message")
                
                assert result["success"] is True
                assert "conversation_id" in result
                mock_run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_agent_delegates_to_agent_framework(self, multi_agent_system):
        """Test that agent creation delegates to Agent Framework system"""
        with patch('AgentOperatingSystem.agents.multi_agent.AGENT_FRAMEWORK_AVAILABLE', True):
            mock_agent = Mock()
            
            with patch.object(multi_agent_system.agent_framework_system, 'create_agent') as mock_create:
                mock_create.return_value = mock_agent
                
                await multi_agent_system.initialize()
                agent = await multi_agent_system.create_agent("TestAgent", "instructions")
                
                assert agent == mock_agent
                mock_create.assert_called_once_with("TestAgent", "instructions", None)
    
    def test_get_statistics_includes_framework_stats(self, multi_agent_system):
        """Test that statistics include Agent Framework system stats"""
        mock_framework_stats = {"framework_agents": 3}
        
        with patch.object(multi_agent_system.agent_framework_system, 'get_statistics') as mock_stats:
            mock_stats.return_value = mock_framework_stats
            
            stats = multi_agent_system.get_statistics()
            
            assert "agent_framework_available" in stats
            assert "framework_stats" in stats
            assert stats["framework_stats"] == mock_framework_stats


class TestWorkflowOrchestrator:
    """Test the generic Workflow Orchestrator"""
    
    @pytest.fixture
    def workflow_orchestrator(self):
        """Create a Workflow Orchestrator instance for testing"""
        return WorkflowOrchestrator("TestWorkflow")
    
    @pytest.mark.asyncio
    async def test_initialization(self, workflow_orchestrator):
        """Test Workflow Orchestrator initialization"""
        with patch('AgentOperatingSystem.orchestration.workflow_orchestrator.AGENT_FRAMEWORK_AVAILABLE', True):
            with patch('AgentOperatingSystem.orchestration.workflow_orchestrator.WorkflowBuilder') as mock_builder:
                mock_builder.return_value = Mock()
                
                await workflow_orchestrator.initialize()
                
                assert workflow_orchestrator.is_initialized
                assert workflow_orchestrator.workflow_builder is not None
    
    @pytest.mark.asyncio
    async def test_add_agent(self, workflow_orchestrator):
        """Test adding an agent to the workflow"""
        with patch('AgentOperatingSystem.orchestration.workflow_orchestrator.AGENT_FRAMEWORK_AVAILABLE', True):
            mock_agent = Mock()
            mock_agent.name = "TestAgent"
            
            mock_builder = Mock()
            mock_builder.add_executor.return_value = "node_id_123"
            workflow_orchestrator.workflow_builder = mock_builder
            workflow_orchestrator.is_initialized = True
            
            node_id = workflow_orchestrator.add_agent("TestAgent", mock_agent)
            
            assert node_id == "node_id_123"
            assert "TestAgent" in workflow_orchestrator.agents
            assert "TestAgent" in workflow_orchestrator.executors
    
    @pytest.mark.asyncio
    async def test_build_workflow(self, workflow_orchestrator):
        """Test building the workflow"""
        with patch('AgentOperatingSystem.orchestration.workflow_orchestrator.AGENT_FRAMEWORK_AVAILABLE', True):
            mock_workflow = Mock()
            mock_builder = Mock()
            mock_builder.build.return_value = mock_workflow
            
            workflow_orchestrator.workflow_builder = mock_builder
            workflow_orchestrator.is_initialized = True
            
            workflow_orchestrator.build_workflow()
            
            assert workflow_orchestrator.workflow == mock_workflow
            mock_builder.build.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_workflow(self, workflow_orchestrator):
        """Test executing the workflow"""
        mock_workflow = Mock()
        mock_workflow.run = AsyncMock(return_value="workflow result")
        
        workflow_orchestrator.workflow = mock_workflow
        
        result = await workflow_orchestrator.execute_workflow("test input")
        
        assert result == "workflow result"
        mock_workflow.run.assert_called_once_with("test input")
    
    def test_create_sequential_workflow(self, workflow_orchestrator):
        """Test creating a sequential workflow"""
        with patch('AgentOperatingSystem.orchestration.workflow_orchestrator.AGENT_FRAMEWORK_AVAILABLE', True):
            mock_agents = [Mock(), Mock(), Mock()]
            for i, agent in enumerate(mock_agents):
                agent.name = f"Agent{i}"
            
            workflow_orchestrator.workflow_builder = Mock()
            workflow_orchestrator.is_initialized = True
            
            with patch.object(workflow_orchestrator, 'add_agent') as mock_add_agent:
                with patch.object(workflow_orchestrator, 'add_workflow_edge') as mock_add_edge:
                    with patch.object(workflow_orchestrator, 'set_start_executor') as mock_set_start:
                        mock_add_agent.side_effect = ["node1", "node2", "node3"]
                        
                        result = workflow_orchestrator.create_sequential_workflow(
                            mock_agents, ["Agent0", "Agent1", "Agent2"]
                        )
                        
                        assert result == workflow_orchestrator
                        assert mock_add_agent.call_count == 3
                        assert mock_add_edge.call_count == 2  # n-1 edges for n agents
                        mock_set_start.assert_called_once_with("Agent0")


class TestWorkflowOrchestratorFactory:
    """Test the Workflow Orchestrator Factory"""
    
    @pytest.mark.asyncio
    async def test_create_boardroom_workflow(self):
        """Test creating a boardroom workflow pattern"""
        with patch('AgentOperatingSystem.orchestration.workflow_orchestrator.AGENT_FRAMEWORK_AVAILABLE', True):
            mock_agents = {
                "founder": Mock(),
                "investor": Mock(),
                "ceo": Mock(),
                "cfo": Mock(),
                "cto": Mock()
            }
            
            mock_decision_integrator = Mock()
            
            with patch('AgentOperatingSystem.orchestration.workflow_orchestrator.WorkflowOrchestrator') as mock_orchestrator_class:
                mock_orchestrator = Mock()
                mock_orchestrator.initialize = AsyncMock()
                mock_orchestrator.add_agent.return_value = "node_id"
                mock_orchestrator.add_executor.return_value = "decision_node"
                mock_orchestrator.add_workflow_edge = Mock()
                mock_orchestrator.set_start_executor = Mock()
                mock_orchestrator_class.return_value = mock_orchestrator
                
                result = WorkflowOrchestratorFactory.create_boardroom_workflow(
                    mock_agents, mock_decision_integrator
                )
                
                assert result == mock_orchestrator
                mock_orchestrator.initialize.assert_called_once()
                # Verify that agents were added
                assert mock_orchestrator.add_agent.call_count == len(mock_agents)
                # Verify that decision integrator was added
                mock_orchestrator.add_executor.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_simple_sequential(self):
        """Test creating a simple sequential workflow"""
        with patch('AgentOperatingSystem.orchestration.workflow_orchestrator.AGENT_FRAMEWORK_AVAILABLE', True):
            mock_agents = [Mock(), Mock()]
            mock_names = ["Agent1", "Agent2"]
            
            with patch('AgentOperatingSystem.orchestration.workflow_orchestrator.WorkflowOrchestrator') as mock_orchestrator_class:
                mock_orchestrator = Mock()
                mock_orchestrator.initialize = AsyncMock()
                mock_orchestrator.create_sequential_workflow = Mock(return_value=mock_orchestrator)
                mock_orchestrator_class.return_value = mock_orchestrator
                
                result = WorkflowOrchestratorFactory.create_simple_sequential(
                    mock_agents, mock_names
                )
                
                assert result == mock_orchestrator
                mock_orchestrator.initialize.assert_called_once()
                mock_orchestrator.create_sequential_workflow.assert_called_once_with(
                    mock_agents, mock_names
                )


# Integration test
class TestAgentFrameworkIntegration:
    """Integration tests for the full Agent Framework migration"""
    
    @pytest.mark.asyncio
    async def test_full_system_integration(self):
        """Test the complete Agent Framework system integration"""
        with patch('AgentOperatingSystem.agents.agent_framework_system.AGENT_FRAMEWORK_AVAILABLE', True):
            with patch('AgentOperatingSystem.agents.multi_agent.AGENT_FRAMEWORK_AVAILABLE', True):
                with patch('AgentOperatingSystem.orchestration.workflow_orchestrator.AGENT_FRAMEWORK_AVAILABLE', True):
                    
                    # Mock Agent Framework components
                    with patch('AgentOperatingSystem.agents.agent_framework_system.ChatAgent') as mock_chat_agent:
                        with patch('AgentOperatingSystem.agents.agent_framework_system.WorkflowBuilder') as mock_workflow_builder:
                            with patch('AgentOperatingSystem.agents.agent_framework_system.setup_telemetry'):
                                
                                # Set up mocks
                                mock_agent = Mock()
                                mock_agent.name = "TestAgent"
                                mock_chat_agent.return_value = mock_agent
                                
                                mock_workflow = Mock()
                                mock_workflow.execute = AsyncMock(return_value="Integration test result")
                                
                                mock_builder = Mock()
                                mock_builder.add_agent.return_value = mock_builder
                                mock_builder.build_sequential_workflow.return_value = mock_workflow
                                mock_workflow_builder.return_value = mock_builder
                                
                                # Test the integration
                                multi_agent_system = MultiAgentSystem()
                                await multi_agent_system.initialize()
                                
                                result = await multi_agent_system.run_multi_agent_conversation(
                                    "Integration test message"
                                )
                                
                                # Verify the integration works
                                assert result["success"] is True
                                assert multi_agent_system.is_initialized
                                
                                # Test statistics integration
                                stats = multi_agent_system.get_statistics()
                                assert "agent_framework_available" in stats
                                assert stats["agent_framework_available"] is True


if __name__ == "__main__":
    pytest.main([__file__])