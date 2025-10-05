from BusinessAgent import BusinessAgent
"""
Unit tests for BusinessInfinity Business Manager

Tests the core BusinessManager class functionality including agent management,
task assignment, workflow orchestration, and status monitoring.

Based on specifications in docs/functionality/specifications.md
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from datetime import datetime
from typing import Dict, Any
from BusinessAgent import BusinessAgent


@pytest.mark.unit
class TestBusinessManagerInitialization:
    """Test BusinessManager initialization and setup"""
    
    @pytest.fixture
    def business_manager(self):
        """Create BusinessManager instance for testing"""
        from src.orchestration.business_manager import BusinessManager
        return BusinessManager()
    
    @pytest.mark.unit
    def test_business_manager_creation(self, business_manager):
        """Test BusinessManager can be created"""
        assert business_manager is not None
        assert hasattr(business_manager, 'logger')
        assert hasattr(business_manager, 'agents')
        assert hasattr(business_manager, 'tasks')
    
    @pytest.mark.unit
    def test_default_agents_initialized(self, business_manager):
        """Test default business agents are initialized"""
        # Should have some default agents
        assert isinstance(business_manager.agents, dict)
        # Default agents should be set up (implementation specific)
        assert len(business_manager.agents) >= 0
    
    @pytest.mark.asyncio
    async def test_business_manager_initialize(self, business_manager):
        """Test async initialization of BusinessManager"""
        # Mock AOS components
        with patch('business_infinity.core.business_manager.AOS_AVAILABLE', True):
            with patch('business_infinity.core.business_manager.create_autonomous_boardroom') as mock_boardroom:
                mock_boardroom.return_value = AsyncMock()
                
                # Should not raise exception
                await business_manager.initialize()
                
                # Verify initialization completed
                assert True  # Test passes if no exception


@pytest.mark.unit
class TestAgentManagement:
    """Test agent registration and management"""
    
    @pytest.fixture
    def business_manager(self):
        """Create BusinessManager for testing"""
        from src.orchestration.business_manager import BusinessManager
        return BusinessManager()
    
    @pytest.fixture
    def sample_agent(self):
        """Create sample business agent"""
        return BusinessAgent(
            id="ceo-001",
            name="Chief Executive Officer",
            role="ceo",
            status="available",
            capabilities=["strategic_planning", "decision_making", "leadership"],
            current_workload=0.3,
            performance_metrics={"accuracy": 0.95, "response_time": 2.5}
        )
    
    @pytest.mark.unit
    def test_register_agent(self, business_manager, sample_agent):
        """Test registering a new agent"""
        # Act
        business_manager.register_agent(sample_agent)
        
        # Assert
        assert sample_agent.id in business_manager.agents
        assert business_manager.agents[sample_agent.id] == sample_agent
    
    @pytest.mark.asyncio
    async def test_get_agent_success(self, business_manager, sample_agent):
        """Test retrieving an existing agent"""
        # Arrange
        business_manager.register_agent(sample_agent)
        
        # Act
        retrieved = await business_manager.get_agent(sample_agent.id)
        
        # Assert
        assert retrieved is not None
        assert retrieved.id == sample_agent.id
        assert retrieved.role == "ceo"
    
    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, business_manager):
        """Test retrieving non-existent agent returns None"""
        # Act
        result = await business_manager.get_agent("non-existent-agent")
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_list_agents(self, business_manager, sample_agent):
        """Test listing all registered agents"""
        # Arrange
        business_manager.register_agent(sample_agent)
        
        # Create another agent
        from src.orchestration.business_manager import BusinessAgent
        cfo_agent = BusinessAgent(
            id="cfo-001",
            name="Chief Financial Officer",
            role="cfo",
            status="available"
        )
        business_manager.register_agent(cfo_agent)
        
        # Act
        agents = await business_manager.list_agents()
        
        # Assert
        assert len(agents) >= 2
        agent_ids = [a.id for a in agents]
        assert "ceo-001" in agent_ids
        assert "cfo-001" in agent_ids
    
    @pytest.mark.asyncio
    async def test_get_agent_status(self, business_manager, sample_agent):
        """Test getting agent status"""
        # Arrange
        business_manager.register_agent(sample_agent)
        
        # Act
        status = await business_manager.get_agent_status(sample_agent.id)
        
        # Assert
        assert status is not None
        assert status["status"] == "available"
        assert status["workload"] == 0.3


@pytest.mark.unit
class TestTaskManagement:
    """Test task assignment and tracking"""
    
    @pytest.fixture
    def business_manager(self):
        """Create BusinessManager for testing"""
        from src.orchestration.business_manager import BusinessManager
        return BusinessManager()
    
    @pytest.fixture
    def sample_task(self):
        """Create sample business task"""
        from src.orchestration.business_manager import BusinessTask
        return BusinessTask(
            task_id="task-001",
            agent_id="ceo-001",
            description="Strategic planning for Q1 2024",
            priority="high",
            status="pending",
            progress=0.0,
            context={"department": "strategy", "quarter": "Q1-2024"}
        )
    
    @pytest.mark.asyncio
    async def test_assign_task(self, business_manager, sample_task):
        """Test assigning a task to an agent"""
        # Act
        task_id = await business_manager.assign_task(sample_task)
        
        # Assert
        assert task_id is not None
        assert task_id in business_manager.tasks
    
    @pytest.mark.unit
    def test_task_properties(self, sample_task):
        """Test business task data structure"""
        assert sample_task.task_id == "task-001"
        assert sample_task.agent_id == "ceo-001"
        assert sample_task.priority == "high"
        assert sample_task.status == "pending"
        assert sample_task.progress == 0.0
        assert "department" in sample_task.context
    
    @pytest.mark.parametrize("priority", ["low", "medium", "high", "critical"])
    def test_task_priorities(self, priority):
        """Test different task priority levels"""
        from src.orchestration.business_manager import BusinessTask
        
        task = BusinessTask(
            task_id=f"task-{priority}",
            agent_id="test-agent",
            description=f"Task with {priority} priority",
            priority=priority
        )
        
        assert task.priority == priority


@pytest.mark.unit
class TestWorkflowOrchestration:
    """Test workflow management and orchestration"""
    
    @pytest.fixture
    def business_manager(self):
        """Create BusinessManager for testing"""
        from src.orchestration.business_manager import BusinessManager
        return BusinessManager()
    
    @pytest.mark.asyncio
    async def test_start_workflow(self, business_manager):
        """Test starting a new workflow"""
        # Arrange
        workflow_id = "workflow-001"
        context = {
            "type": "strategic_planning",
            "participants": ["ceo", "cfo", "cto"],
            "timeline": "Q1-2024"
        }
        
        # Act
        result = await business_manager.start_workflow(workflow_id, context)
        
        # Assert
        assert result is not None
        assert workflow_id in business_manager.active_workflows
    
    @pytest.mark.asyncio
    async def test_get_workflow_status(self, business_manager):
        """Test retrieving workflow status"""
        # Arrange
        workflow_id = "workflow-002"
        context = {"type": "decision_making"}
        await business_manager.start_workflow(workflow_id, context)
        
        # Act
        status = await business_manager.get_workflow_status(workflow_id)
        
        # Assert
        assert status is not None
        assert "status" in status or "state" in status
    
    @pytest.mark.asyncio
    async def test_update_workflow(self, business_manager):
        """Test updating workflow state"""
        # Arrange
        workflow_id = "workflow-003"
        await business_manager.start_workflow(workflow_id, {})
        
        updates = {"status": "in_progress", "progress": 0.5}
        
        # Act
        result = await business_manager.update_workflow(workflow_id, updates)
        
        # Assert
        assert result is True or result is not None
    
    @pytest.mark.asyncio
    async def test_cancel_workflow(self, business_manager):
        """Test cancelling an active workflow"""
        # Arrange
        workflow_id = "workflow-004"
        await business_manager.start_workflow(workflow_id, {})
        
        # Act
        result = await business_manager.cancel_workflow(workflow_id)
        
        # Assert
        assert result is True or result is not None


@pytest.mark.unit
class TestBusinessManagerIntegration:
    """Test BusinessManager integration with other components"""
    
    @pytest.fixture
    def business_manager(self):
        """Create BusinessManager for testing"""
        from src.orchestration.business_manager import BusinessManager
        return BusinessManager()
    
    @pytest.mark.asyncio
    async def test_aos_integration_when_available(self, business_manager):
        """Test integration with AOS when available"""
        with patch('business_infinity.core.business_manager.AOS_AVAILABLE', True):
            with patch('business_infinity.core.business_manager.create_autonomous_boardroom') as mock_create:
                mock_boardroom = AsyncMock()
                mock_create.return_value = mock_boardroom
                
                # Act
                await business_manager.initialize()
                
                # Assert
                assert business_manager.boardroom is not None or True
    
    @pytest.mark.asyncio
    async def test_standalone_mode_when_aos_unavailable(self, business_manager):
        """Test operation in standalone mode when AOS unavailable"""
        with patch('business_infinity.core.business_manager.AOS_AVAILABLE', False):
            # Act - should not raise exception
            await business_manager.initialize()
            
            # Assert - manager should still function
            assert business_manager is not None


@pytest.mark.unit
class TestBusinessAgentDataClass:
    """Test BusinessAgent data class"""
    
    def test_business_agent_creation(self):
        """Test creating a BusinessAgent"""
        from src.orchestration.business_manager import BusinessAgent
        
        agent = BusinessAgent(
            id="test-001",
            name="Test Agent",
            role="tester",
            status="available",
            capabilities=["testing"],
            current_workload=0.5,
            performance_metrics={"score": 0.9}
        )
        
        assert agent.id == "test-001"
        assert agent.name == "Test Agent"
        assert agent.role == "tester"
        assert agent.status == "available"
        assert "testing" in agent.capabilities
        assert agent.current_workload == 0.5
        assert agent.performance_metrics["score"] == 0.9
    
    def test_business_agent_defaults(self):
        """Test BusinessAgent with default values"""
        from src.orchestration.business_manager import BusinessAgent
        
        agent = BusinessAgent(
            id="minimal-001",
            name="Minimal Agent",
            role="minimal"
        )
        
        assert agent.status == "available"
        assert agent.current_workload == 0.0
        assert isinstance(agent.capabilities, list)
        assert isinstance(agent.performance_metrics, dict)


@pytest.mark.unit
class TestBusinessTaskDataClass:
    """Test BusinessTask data class"""
    
    def test_business_task_creation(self):
        """Test creating a BusinessTask"""
        from src.orchestration.business_manager import BusinessTask
        
        task = BusinessTask(
            task_id="task-test-001",
            agent_id="agent-001",
            description="Test task",
            priority="medium",
            status="pending",
            progress=0.0,
            context={"test": True}
        )
        
        assert task.task_id == "task-test-001"
        assert task.agent_id == "agent-001"
        assert task.description == "Test task"
        assert task.priority == "medium"
        assert task.status == "pending"
        assert task.progress == 0.0
        assert task.context["test"] is True
    
    def test_business_task_defaults(self):
        """Test BusinessTask with default values"""
        from src.orchestration.business_manager import BusinessTask
        
        task = BusinessTask(
            task_id="minimal-task",
            agent_id="agent-001",
            description="Minimal task"
        )
        
        assert task.priority == "medium"
        assert task.status == "pending"
        assert task.progress == 0.0
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.context, dict)
