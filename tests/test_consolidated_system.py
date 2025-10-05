"""
Integration Tests for Consolidated Core System
Tests the refactored architecture and backward compatibility
"""

import pytest



class TestCoreSystemImports:
    """Test that all core system modules can be imported successfully"""
    
    def test_core_system_imports(self):
        """Test importing the main core system"""
        import core
        
        # Check that main components are available
        assert hasattr(core, 'agent_manager')
        assert hasattr(core, 'auth_handler')
        assert hasattr(core, 'storage_manager')
        assert hasattr(core, 'triggers_manager')
        assert hasattr(core, 'utils_manager')
        assert hasattr(core, 'unified_server')
        assert hasattr(core, 'mcp_handler')
        assert hasattr(core, 'orchestrator')
    
    def test_core_individual_imports(self):
        """Test importing individual components from core"""
        from core import (
            agent_manager, auth_handler, storage_manager, 
            triggers_manager, utils_manager, unified_server,
            mcp_handler, orchestrator
        )
        
        # Basic sanity checks
        assert agent_manager is not None
        assert auth_handler is not None
        assert storage_manager is not None
        assert triggers_manager is not None
        assert utils_manager is not None
        assert unified_server is not None
        assert mcp_handler is not None
        assert orchestrator is not None


class TestBackwardCompatibility:
    """Test that backward compatibility is maintained"""
    
    def test_agents_backward_compatibility(self):
        """Test that agents module still works"""
        from agents import agent_manager, UnifiedAgentManager
        
        assert agent_manager is not None
        assert UnifiedAgentManager is not None
        assert hasattr(agent_manager, 'get_agent_profiles')
    
    def test_authentication_backward_compatibility(self):
        """Test that authentication module still works"""  
        from authentication import auth_handler, UNAUTHORIZED_MSG
        
        assert auth_handler is not None
        assert UNAUTHORIZED_MSG == "Unauthorized"
        assert hasattr(auth_handler, 'validate_jwt')
    
    def test_storage_backward_compatibility(self):
        """Test that storage module still works"""
        from storage import storage_manager, UnifiedStorageManager
        
        assert storage_manager is not None
        assert UnifiedStorageManager is not None
        assert hasattr(storage_manager, 'validate_configuration')
    
    def test_triggers_backward_compatibility(self):
        """Test that triggers module still works"""
        from triggers import (
            register_http_routes, register_queue_triggers, 
            register_service_bus_triggers, triggers_manager
        )
        
        assert register_http_routes is not None
        assert register_queue_triggers is not None
        assert register_service_bus_triggers is not None
        assert triggers_manager is not None
    
    def test_utils_backward_compatibility(self):
        """Test that utils module still works"""
        from utils import validate_request, GovernanceError, utils_manager
        
        assert validate_request is not None
        assert GovernanceError is not None
        assert utils_manager is not None
        
        # Test that governance validation works
        try:
            validate_request("inference", {"role": "test", "payload": {"agentId": "test"}})
        except GovernanceError:
            # This is expected - just testing it doesn't crash
            pass


class TestConsolidatedFunctionality:
    """Test that consolidated functionality works correctly"""
    
    def test_auth_handler_functionality(self):
        """Test authentication handler"""
        from core import auth_handler
        
        # Test configuration validation
        config_status = auth_handler.validate_configuration()
        assert isinstance(config_status, dict)
        assert 'valid' in config_status
        assert 'issues' in config_status
        
        # Test JWT validation with invalid token (should return None)
        result = auth_handler.validate_jwt("invalid_token")
        assert result is None
    
    def test_storage_manager_functionality(self):
        """Test storage manager"""
        from core import storage_manager
        
        # Test configuration validation
        config_status = storage_manager.validate_configuration()
        assert isinstance(config_status, dict)
        assert 'valid' in config_status
        assert 'issues' in config_status
        
        # Test that methods exist
        assert hasattr(storage_manager, 'get_agent_dirs')
        assert hasattr(storage_manager, 'get_agent_profiles')
        assert hasattr(storage_manager, 'get_domain_knowledge')
    
    def test_triggers_manager_functionality(self):
        """Test triggers manager"""
        from core import triggers_manager
        
        # Test configuration validation
        config_status = triggers_manager.validate_configuration()
        assert isinstance(config_status, dict)
        assert 'valid' in config_status
        assert 'issues' in config_status
        assert 'handlers_registered' in config_status
        
        # Test handler registration methods exist
        assert hasattr(triggers_manager, 'register_queue_handler')
        assert hasattr(triggers_manager, 'register_service_bus_handler')
        assert hasattr(triggers_manager, 'register_http_handler')
    
    def test_utils_manager_functionality(self):
        """Test utils manager"""
        from core import utils_manager
        
        # Test configuration validation
        config_status = utils_manager.validate_configuration()
        assert isinstance(config_status, dict)
        assert 'valid' in config_status
        assert 'issues' in config_status
        
        # Test utility functions
        assert hasattr(utils_manager, 'validate_request')
        assert hasattr(utils_manager, 'get_ui_schema')
        assert hasattr(utils_manager, 'load_config')
        
        # Test UI schema generation
        schema = utils_manager.get_ui_schema("test_role", "local")
        assert isinstance(schema, dict)
    
    def test_agent_manager_functionality(self):
        """Test agent manager"""
        from core import agent_manager
        
        # Test that basic methods exist and work
        assert hasattr(agent_manager, 'get_agent_profiles')
        assert hasattr(agent_manager, 'list_agent_ids')
        assert hasattr(agent_manager, 'get_agent_count')
        
        # Test getting agent profiles (should return JSON string)
        profiles = agent_manager.get_agent_profiles()
        assert isinstance(profiles, str)
        
        # Test agent count
        count = agent_manager.get_agent_count()
        assert isinstance(count, int)
        assert count >= 0


class TestFunctionAppIntegration:
    """Test that the function app loads correctly with consolidated system"""
    
    def test_function_app_imports(self):
        """Test that function app can import from core"""
        # This simulates what function_app.py does
        try:
            from core.azure_functions import register_consolidated_functions
            assert register_consolidated_functions is not None
        except ImportError as e:
            pytest.fail(f"Failed to import consolidated functions: {e}")
    
    def test_azure_functions_functionality(self):
        """Test Azure Functions integration"""
        from core.azure_functions import consolidated_functions
        
        # Test configuration validation
        config_status = consolidated_functions.validate_configuration()
        assert isinstance(config_status, dict)
        assert 'valid' in config_status
        assert 'azure_functions_available' in config_status
        assert 'core_system_available' in config_status
        assert 'legacy_agents_count' in config_status
        
        # Test that legacy agents are defined
        assert len(consolidated_functions.legacy_agents) > 0
        assert 'operations' in consolidated_functions.legacy_agents
        assert 'finance' in consolidated_functions.legacy_agents


class TestConfigurationSystem:
    """Test the configuration system"""
    
    def test_config_files_exist(self):
        """Test that essential config files exist"""
        import os
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent
        config_paths = [
            project_root / "shared" / "framework" / "configs" / "principles.example.json",
            project_root / "shared" / "framework" / "configs" / "decision_tree.example.json", 
            project_root / "shared" / "framework" / "configs" / "adapters.example.json"
        ]
        
        for config_path in config_paths:
            assert config_path.exists(), f"Config file missing: {config_path}"
    
    def test_config_loading(self):
        """Test that config files can be loaded"""
        from shared.framework.server.config_loader import load_principles, load_decision_tree, load_adapters
        
        try:
            principles = load_principles()
            assert isinstance(principles, dict)
            assert 'principles' in principles
            
            tree = load_decision_tree()
            assert isinstance(tree, dict)
            
            adapters = load_adapters()
            assert isinstance(adapters, dict)
            
        except Exception as e:
            pytest.fail(f"Failed to load config files: {e}")


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])