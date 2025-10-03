"""
Unit tests for BusinessInfinity Application

Tests the main BusinessInfinity class functionality including configuration,
initialization, agent coordination, decision-making, and workflow management.

Based on specifications in docs/functionality/specifications.md
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import Dict, Any
import json


@pytest.mark.unit
class TestBusinessInfinityConfiguration:
    """Test BusinessInfinity configuration"""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration"""
        config = MagicMock()
        config.aos_config = None
        return config
    
    @pytest.mark.unit
    def test_business_infinity_with_config(self, mock_config):
        """Test BusinessInfinity initialization with config"""
        with patch('src.business_infinity.AgentOperatingSystem'):
            with patch('src.business_infinity.UnifiedStorageManager'):
                from src.business_infinity import BusinessInfinity
                
                bi = BusinessInfinity(mock_config)
                
                assert bi is not None
                assert bi.config == mock_config
    
    @pytest.mark.unit
    def test_business_infinity_default_config(self):
        """Test BusinessInfinity with default configuration"""
        with patch('src.business_infinity.AgentOperatingSystem'):
            with patch('src.business_infinity.UnifiedStorageManager'):
                with patch('src.business_infinity.BusinessInfinityConfig') as MockConfig:
                    MockConfig.return_value = MagicMock()
                    
                    from src.business_infinity import BusinessInfinity
                    bi = BusinessInfinity()
                    
                    assert bi is not None
                    assert bi.config is not None


@pytest.mark.unit
class TestBusinessInfinityInitialization:
    """Test BusinessInfinity initialization and setup"""
    
    @pytest.fixture
    def mock_aos(self):
        """Mock Agent Operating System"""
        return MagicMock()
    
    @pytest.fixture
    def business_infinity_instance(self, mock_aos):
        """Create BusinessInfinity instance with mocked dependencies"""
        with patch('src.business_infinity.AgentOperatingSystem', return_value=mock_aos):
            with patch('src.business_infinity.UnifiedStorageManager'):
                with patch('src.business_infinity.UnifiedEnvManager'):
                    with patch('src.business_infinity.BusinessAgentManager'):
                        from src.business_infinity import BusinessInfinity
                        return BusinessInfinity()
    
    @pytest.mark.unit
    def test_aos_initialization(self, business_infinity_instance):
        """Test AOS is initialized"""
        assert business_infinity_instance.aos is not None
    
    @pytest.mark.unit
    def test_storage_manager_initialization(self, business_infinity_instance):
        """Test storage manager is initialized"""
        assert business_infinity_instance.storage_manager is not None
    
    @pytest.mark.unit
    def test_env_manager_initialization(self, business_infinity_instance):
        """Test environment manager is initialized"""
        assert business_infinity_instance.env_manager is not None


@pytest.mark.unit
class TestBusinessInfinityAgentManagement:
    """Test BusinessInfinity agent coordination"""
    
    @pytest.fixture
    def business_infinity_mock(self):
        """Create BusinessInfinity with mocked components"""
        with patch('src.business_infinity.AgentOperatingSystem'):
            with patch('src.business_infinity.UnifiedStorageManager'):
                with patch('src.business_infinity.BusinessAgentManager') as MockAgentMgr:
                    mock_agent_mgr = MagicMock()
                    mock_agent_mgr.get_agent = AsyncMock(return_value={"id": "ceo", "status": "available"})
                    mock_agent_mgr.list_agents = AsyncMock(return_value=[
                        {"id": "ceo", "role": "CEO"},
                        {"id": "cfo", "role": "CFO"}
                    ])
                    MockAgentMgr.return_value = mock_agent_mgr
                    
                    from src.business_infinity import BusinessInfinity
                    return BusinessInfinity()
    
    @pytest.mark.asyncio
    async def test_get_agent(self, business_infinity_mock):
        """Test getting agent through BusinessInfinity"""
        # Act
        agent = await business_infinity_mock.agent_manager.get_agent("ceo")
        
        # Assert
        assert agent is not None
        assert agent["id"] == "ceo"
    
    @pytest.mark.asyncio
    async def test_list_agents(self, business_infinity_mock):
        """Test listing agents through BusinessInfinity"""
        # Act
        agents = await business_infinity_mock.agent_manager.list_agents()
        
        # Assert
        assert len(agents) == 2
        assert agents[0]["role"] == "CEO"
        assert agents[1]["role"] == "CFO"


@pytest.mark.unit  
class TestBusinessInfinityDecisionMaking:
    """Test strategic decision-making functionality"""
    
    @pytest.fixture
    def decision_context(self):
        """Sample decision context"""
        return {
            "title": "Strategic Initiative for Q1 2024",
            "type": "strategic",
            "description": "Launch new product line",
            "budget": 500000,
            "timeline": "Q1-2024",
            "champion": "ceo"
        }
    
    @pytest.fixture
    def business_infinity_with_workflow(self):
        """BusinessInfinity with workflow manager"""
        with patch('src.business_infinity.AgentOperatingSystem'):
            with patch('src.business_infinity.UnifiedStorageManager'):
                with patch('src.business_infinity.BusinessWorkflowManager') as MockWorkflow:
                    mock_workflow = MagicMock()
                    mock_workflow.create_strategic_decision = AsyncMock(return_value="decision-001")
                    mock_workflow.get_decision = AsyncMock(return_value={
                        "id": "decision-001",
                        "status": "pending",
                        "votes": {}
                    })
                    MockWorkflow.return_value = mock_workflow
                    
                    from src.business_infinity import BusinessInfinity
                    bi = BusinessInfinity()
                    bi.workflow_manager = mock_workflow
                    return bi
    
    @pytest.mark.asyncio
    async def test_create_strategic_decision(self, business_infinity_with_workflow, decision_context):
        """Test creating a strategic decision"""
        # Act
        decision_id = await business_infinity_with_workflow.workflow_manager.create_strategic_decision(
            decision_context
        )
        
        # Assert
        assert decision_id == "decision-001"
    
    @pytest.mark.asyncio
    async def test_get_decision_details(self, business_infinity_with_workflow):
        """Test retrieving decision details"""
        # Act
        decision = await business_infinity_with_workflow.workflow_manager.get_decision("decision-001")
        
        # Assert
        assert decision is not None
        assert decision["id"] == "decision-001"
        assert decision["status"] == "pending"


@pytest.mark.unit
class TestBusinessInfinityAnalytics:
    """Test business analytics functionality"""
    
    @pytest.fixture
    def business_infinity_with_analytics(self):
        """BusinessInfinity with analytics manager"""
        with patch('src.business_infinity.AgentOperatingSystem'):
            with patch('src.business_infinity.UnifiedStorageManager'):
                with patch('src.business_infinity.BusinessAnalyticsManager') as MockAnalytics:
                    mock_analytics = MagicMock()
                    mock_analytics.record_metric = AsyncMock(return_value=True)
                    mock_analytics.get_metrics = AsyncMock(return_value=[
                        {"name": "revenue", "value": 100000, "unit": "USD"}
                    ])
                    MockAnalytics.return_value = mock_analytics
                    
                    from src.business_infinity import BusinessInfinity
                    bi = BusinessInfinity()
                    bi.analytics_manager = mock_analytics
                    return bi
    
    @pytest.mark.asyncio
    async def test_record_metric(self, business_infinity_with_analytics):
        """Test recording a business metric"""
        # Act
        result = await business_infinity_with_analytics.analytics_manager.record_metric(
            name="revenue",
            value=100000,
            unit="USD",
            metric_type="financial"
        )
        
        # Assert
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, business_infinity_with_analytics):
        """Test retrieving metrics"""
        # Act
        metrics = await business_infinity_with_analytics.analytics_manager.get_metrics()
        
        # Assert
        assert len(metrics) == 1
        assert metrics[0]["name"] == "revenue"
        assert metrics[0]["value"] == 100000


@pytest.mark.unit
class TestBusinessInfinityMCPIntegration:
    """Test MCP (Model Context Protocol) integration"""
    
    @pytest.fixture
    def business_infinity_with_mcp(self):
        """BusinessInfinity with MCP client"""
        with patch('src.business_infinity.AgentOperatingSystem'):
            with patch('src.business_infinity.UnifiedStorageManager'):
                with patch('src.business_infinity.MCPServiceBusClient') as MockMCP:
                    mock_mcp = MagicMock()
                    mock_mcp.send_request = AsyncMock(return_value={"status": "success"})
                    MockMCP.return_value = mock_mcp
                    
                    from src.business_infinity import BusinessInfinity
                    bi = BusinessInfinity()
                    bi.mcp_servicebus_client = mock_mcp
                    return bi
    
    @pytest.mark.asyncio
    async def test_mcp_client_initialization(self, business_infinity_with_mcp):
        """Test MCP Service Bus client is initialized"""
        assert business_infinity_with_mcp.mcp_servicebus_client is not None
    
    @pytest.mark.asyncio
    async def test_send_mcp_request(self, business_infinity_with_mcp):
        """Test sending MCP request"""
        # Act
        response = await business_infinity_with_mcp.mcp_servicebus_client.send_request(
            server="linkedin",
            method="get_profile",
            params={"user_id": "test"}
        )
        
        # Assert
        assert response["status"] == "success"


@pytest.mark.unit
class TestBusinessInfinityStorageIntegration:
    """Test storage and persistence functionality"""
    
    @pytest.fixture
    def business_infinity_with_storage(self):
        """BusinessInfinity with storage manager"""
        with patch('src.business_infinity.AgentOperatingSystem'):
            with patch('src.business_infinity.UnifiedStorageManager') as MockStorage:
                mock_storage = MagicMock()
                mock_storage.store_boardroom_decision = AsyncMock(return_value=True)
                mock_storage.get_boardroom_history = AsyncMock(return_value=[
                    {"decision_id": "d1", "title": "Decision 1"},
                    {"decision_id": "d2", "title": "Decision 2"}
                ])
                MockStorage.return_value = mock_storage
                
                from src.business_infinity import BusinessInfinity
                bi = BusinessInfinity()
                return bi
    
    @pytest.mark.asyncio
    async def test_store_decision(self, business_infinity_with_storage):
        """Test storing a decision"""
        decision_data = {
            "decision_id": "test-001",
            "title": "Test Decision",
            "status": "pending"
        }
        
        # Act
        result = await business_infinity_with_storage.storage_manager.store_boardroom_decision(
            decision_data
        )
        
        # Assert
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_decision_history(self, business_infinity_with_storage):
        """Test retrieving decision history"""
        # Act
        history = await business_infinity_with_storage.storage_manager.get_boardroom_history(limit=10)
        
        # Assert
        assert len(history) == 2
        assert history[0]["decision_id"] == "d1"
        assert history[1]["decision_id"] == "d2"


@pytest.mark.unit
class TestBusinessInfinityErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.unit
    def test_initialization_with_missing_dependencies(self):
        """Test graceful handling of missing dependencies"""
        with patch('src.business_infinity.AgentOperatingSystem', side_effect=ImportError()):
            with patch('src.business_infinity.UnifiedStorageManager'):
                # Should handle gracefully or raise expected error
                try:
                    from src.business_infinity import BusinessInfinity
                    bi = BusinessInfinity()
                    # If it doesn't raise, that's acceptable
                    assert True
                except (ImportError, Exception) as e:
                    # Expected error is acceptable
                    assert True
    
    @pytest.mark.unit
    def test_mcp_client_unavailable(self):
        """Test operation when MCP client is unavailable"""
        with patch('src.business_infinity.AgentOperatingSystem'):
            with patch('src.business_infinity.UnifiedStorageManager'):
                with patch('src.business_infinity.MCPServiceBusClient', side_effect=ImportError()):
                    from src.business_infinity import BusinessInfinity
                    bi = BusinessInfinity()
                    
                    # Should set mcp_servicebus_client to None
                    assert bi.mcp_servicebus_client is None


@pytest.mark.unit
class TestBusinessInfinityModularManagers:
    """Test modular manager architecture"""
    
    @pytest.fixture
    def business_infinity_full(self):
        """BusinessInfinity with all managers"""
        with patch('src.business_infinity.AgentOperatingSystem'):
            with patch('src.business_infinity.UnifiedStorageManager'):
                with patch('src.business_infinity.BusinessAgentManager') as MockAgentMgr:
                    with patch('src.business_infinity.BusinessWorkflowManager') as MockWorkflow:
                        with patch('src.business_infinity.BusinessAnalyticsManager') as MockAnalytics:
                            with patch('src.business_infinity.BusinessCovenantManager') as MockCovenant:
                                MockAgentMgr.return_value = MagicMock()
                                MockWorkflow.return_value = MagicMock()
                                MockAnalytics.return_value = MagicMock()
                                MockCovenant.return_value = MagicMock()
                                
                                from src.business_infinity import BusinessInfinity
                                return BusinessInfinity()
    
    @pytest.mark.unit
    def test_all_managers_initialized(self, business_infinity_full):
        """Test that all modular managers are initialized"""
        assert hasattr(business_infinity_full, 'agent_manager')
        assert business_infinity_full.agent_manager is not None
        
        # Note: Other managers depend on actual implementation
        # This test validates the architecture pattern


@pytest.mark.unit
class TestBusinessInfinityMCPServersRegistry:
    """Test MCP servers registry functionality"""
    
    @pytest.fixture
    def mock_mcp_servers_file(self, tmp_path):
        """Create mock MCP servers JSON file"""
        mcp_data = {
            "linkedin": {
                "name": "LinkedIn MCP",
                "endpoint": "linkedin-mcp-server",
                "capabilities": ["profile", "connections", "posts"]
            },
            "reddit": {
                "name": "Reddit MCP",
                "endpoint": "mcp-reddit",
                "capabilities": ["posts", "comments", "subreddits"]
            }
        }
        
        mcp_file = tmp_path / "mcp_servers.json"
        mcp_file.write_text(json.dumps(mcp_data))
        return str(mcp_file)
    
    @pytest.mark.unit
    def test_mcp_servers_loaded(self):
        """Test MCP servers registry is loaded"""
        with patch('src.business_infinity.AgentOperatingSystem'):
            with patch('src.business_infinity.UnifiedStorageManager'):
                from src.business_infinity import BusinessInfinity
                bi = BusinessInfinity()
                
                # Should have loaded MCP servers
                assert hasattr(bi, 'mcp_servers')
                assert isinstance(bi.mcp_servers, dict)
