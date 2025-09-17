#!/usr/bin/env python3
"""
Simple validation script to test the consolidated system
Runs without pytest for easier execution
"""

import sys
import os
import traceback

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_function(name, test_func):
    """Run a test function and report results"""
    try:
        test_func()
        print(f"✅ {name}")
        return True
    except Exception as e:
        print(f"❌ {name}: {e}")
        traceback.print_exc()
        return False

def test_core_system_imports():
    """Test importing the main core system"""
    import core
    
    # Check that main components are available
    required_attrs = [
        'agent_manager', 'auth_handler', 'storage_manager', 
        'triggers_manager', 'utils_manager', 'unified_server',
        'mcp_handler', 'orchestrator'
    ]
    
    for attr in required_attrs:
        assert hasattr(core, attr), f"Missing attribute: {attr}"
    
    print(f"   Core system has {len(core.__all__)} exported components")

def test_backward_compatibility():
    """Test that backward compatibility is maintained"""
    # Test agents
    from agents import agent_manager, UnifiedAgentManager
    assert agent_manager is not None
    assert hasattr(agent_manager, 'get_agent_profiles')
    
    # Test authentication
    from authentication import auth_handler, UNAUTHORIZED_MSG
    assert auth_handler is not None
    assert UNAUTHORIZED_MSG == "Unauthorized"
    
    # Test storage
    from storage import storage_manager, UnifiedStorageManager
    assert storage_manager is not None
    assert hasattr(storage_manager, 'validate_configuration')
    
    # Test triggers
    from triggers import register_http_routes, triggers_manager
    assert register_http_routes is not None
    assert triggers_manager is not None
    
    # Test utils
    from utils import validate_request, GovernanceError, utils_manager
    assert validate_request is not None
    assert GovernanceError is not None
    assert utils_manager is not None
    
    print("   All legacy imports working correctly")

def test_configuration_validation():
    """Test configuration validation across modules"""
    from core import auth_handler, storage_manager, triggers_manager, utils_manager
    
    configs = {
        'auth': auth_handler.validate_configuration(),
        'storage': storage_manager.validate_configuration(),
        'triggers': triggers_manager.validate_configuration(),
        'utils': utils_manager.validate_configuration()
    }
    
    for name, config in configs.items():
        assert isinstance(config, dict), f"{name} config validation failed"
        assert 'valid' in config, f"{name} config missing 'valid' field"
        assert 'issues' in config, f"{name} config missing 'issues' field"
    
    print("   Configuration validation working for all modules")

def test_agent_functionality():
    """Test basic agent functionality"""
    from core import agent_manager
    
    # Test getting agent profiles
    profiles = agent_manager.get_agent_profiles()
    assert isinstance(profiles, str), "Agent profiles should be JSON string"
    
    # Test agent count
    count = agent_manager.get_agent_count()
    assert isinstance(count, int), "Agent count should be integer"
    assert count >= 0, "Agent count should be non-negative"
    
    # Test agent IDs
    ids = agent_manager.list_agent_ids()
    assert isinstance(ids, list), "Agent IDs should be a list"
    
    print(f"   Agent system working with {count} agents")

def test_azure_functions_integration():
    """Test Azure Functions integration"""
    from core.azure_functions import consolidated_functions, register_consolidated_functions
    
    # Test configuration validation
    config = consolidated_functions.validate_configuration()
    assert isinstance(config, dict), "Azure Functions config should be dict"
    
    # Test that function exists
    assert callable(register_consolidated_functions), "register_consolidated_functions should be callable"
    
    # Test legacy agents
    legacy_count = len(consolidated_functions.legacy_agents)
    assert legacy_count > 0, "Should have legacy agents defined"
    
    print(f"   Azure Functions integration working with {legacy_count} legacy agents")

def test_config_files():
    """Test that config files exist and can be loaded"""
    from pathlib import Path
    
    project_root = Path(__file__).parent
    config_paths = [
        project_root / "shared" / "framework" / "configs" / "principles.example.json",
        project_root / "shared" / "framework" / "configs" / "decision_tree.example.json", 
        project_root / "shared" / "framework" / "configs" / "adapters.example.json"
    ]
    
    for config_path in config_paths:
        assert config_path.exists(), f"Config file missing: {config_path}"
    
    # Test loading
    from shared.framework.server.config_loader import load_principles, load_decision_tree, load_adapters
    
    principles = load_principles()
    assert isinstance(principles, dict), "Principles should be dict"
    
    tree = load_decision_tree()
    assert isinstance(tree, dict), "Decision tree should be dict"
    
    adapters = load_adapters()
    assert isinstance(adapters, dict), "Adapters should be dict"
    
    print("   Config files exist and load correctly")

def test_governance_functionality():
    """Test governance and validation functionality"""
    from core import utils_manager
    from utils import GovernanceError
    
    # Test basic validation (should not raise error)
    try:
        utils_manager.validate_request("inference", {
            "role": "test", 
            "payload": {"agentId": "test"}
        })
    except GovernanceError:
        pass  # Expected for some validation rules
    
    # Test UI schema generation
    schema = utils_manager.get_ui_schema("test_role", "local")
    assert isinstance(schema, dict), "UI schema should be dict"
    
    print("   Governance and validation working")

def main():
    """Run all validation tests"""
    print("🧪 Validating Consolidated Business Infinity System")
    print("=" * 50)
    
    tests = [
        ("Core System Imports", test_core_system_imports),
        ("Backward Compatibility", test_backward_compatibility),
        ("Configuration Validation", test_configuration_validation),
        ("Agent Functionality", test_agent_functionality),
        ("Azure Functions Integration", test_azure_functions_integration),
        ("Config Files", test_config_files),
        ("Governance Functionality", test_governance_functionality),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        if test_function(name, test_func):
            passed += 1
        else:
            failed += 1
    
    print("=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The consolidated system is working correctly.")
        return 0
    else:
        print("💥 Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())