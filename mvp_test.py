#!/usr/bin/env python3
"""
MVP Test Script for BusinessInfinity
Tests the core MVP functionality without external dependencies
"""

import sys
import os
import asyncio
import json
import time

def test_function(name, test_func):
    """Run a test function and report results"""
    try:
        test_func()
        print(f"✅ {name}")
        return True
    except Exception as e:
        print(f"❌ {name}: {e}")
        return False


def test_mvp_agents():
    """Test MVP agent system"""
    from mvp_agents import agent_manager, LeadershipAgent
    
    # Test agent manager initialization
    assert len(agent_manager.agents) > 0, "Should have agents initialized"
    
    # Test getting agents
    ceo = agent_manager.get_agent('ceo')
    assert ceo is not None, "Should be able to get CEO agent"
    assert ceo.role == "CEO", "CEO should have correct role"
    
    # Test agent profiles
    profiles = agent_manager.list_agents()
    assert len(profiles) > 0, "Should have agent profiles"
    assert all('id' in p and 'name' in p and 'role' in p for p in profiles), "Profiles should have required fields"
    
    print(f"   Initialized {len(agent_manager.agents)} agents successfully")


def test_mvp_chat():
    """Test MVP chat functionality"""
    from mvp_agents import agent_manager
    
    async def chat_test():
        # Test chatting with CEO
        response = await agent_manager.ask_agent('ceo', 'What is our strategic vision?')
        assert response is not None, "Should get response from CEO"
        assert 'strategic' in response.lower() or 'vision' in response.lower(), "Response should be relevant"
        
        # Test chatting with CFO
        response = await agent_manager.ask_agent('cfo', 'What is our budget status?')
        assert response is not None, "Should get response from CFO"
        assert len(response) > 10, "Response should be substantial"
        
        # Test invalid agent
        response = await agent_manager.ask_agent('invalid_agent', 'test')
        assert response is None, "Should return None for invalid agent"
        
    # Run async test
    asyncio.run(chat_test())
    print("   Chat functionality working correctly")


def test_mvp_functions():
    """Test MVP Azure Functions"""
    from mvp_functions import mvp_function
    
    # Test health check
    response = mvp_function.health_check()
    assert response['statusCode'] == 200, "Health check should return 200"
    body = json.loads(response['body'])
    assert body['status'] == 'healthy', "Should be healthy"
    
    # Test list agents
    response = mvp_function.list_agents()
    assert response['statusCode'] == 200, "List agents should return 200"
    agents = json.loads(response['body'])
    assert len(agents) > 0, "Should have agents"
    
    # Test get agent
    response = mvp_function.get_agent('ceo')
    assert response['statusCode'] == 200, "Get agent should return 200"
    agent = json.loads(response['body'])
    assert agent['role'] == 'CEO', "Should get CEO agent"
    
    # Test get invalid agent
    response = mvp_function.get_agent('invalid')
    assert response['statusCode'] == 404, "Invalid agent should return 404"
    
    # Test chat
    response = mvp_function.chat_with_agent('ceo', 'Hello')
    assert response['statusCode'] == 200, "Chat should return 200"
    chat_result = json.loads(response['body'])
    assert 'response' in chat_result, "Should have response"
    
    print("   MVP Functions working correctly")


def test_server_components():
    """Test server components without starting server"""
    from mvp_server import MVPAPIHandler
    
    # Test that handler class exists and has required methods
    handler_methods = ['do_GET', 'do_POST', 'do_OPTIONS']
    for method in handler_methods:
        assert hasattr(MVPAPIHandler, method), f"Handler should have {method} method"
    
    print("   Server components initialized correctly")


def test_configuration():
    """Test basic configuration and file structure"""
    # Check that required MVP files exist
    required_files = [
        'mvp_agents.py',
        'mvp_server.py', 
        'mvp_functions.py',
        'mvp_test.py'
    ]
    
    for filename in required_files:
        assert os.path.exists(filename), f"Required MVP file {filename} should exist"
    
    # Test that original files are preserved
    original_files = [
        'pyproject.toml',
        'README.md',
        'function_app.py'
    ]
    
    for filename in original_files:
        assert os.path.exists(filename), f"Original file {filename} should be preserved"
    
    print("   Configuration and file structure correct")


def test_integration():
    """Test integration between components"""
    from mvp_agents import agent_manager
    from mvp_functions import mvp_function
    
    # Test that functions can access agents
    assert mvp_function.agent_manager is agent_manager, "Functions should use same agent manager"
    
    # Test cross-component communication
    response = mvp_function.chat_with_agent('founder', 'What is our company vision?')
    assert response['statusCode'] == 200, "Should be able to chat with founder through function"
    
    print("   Integration between components working")


def main():
    """Run all MVP tests"""
    print("🧪 Testing BusinessInfinity MVP")
    print("=" * 40)
    
    tests = [
        ("MVP Agent System", test_mvp_agents),
        ("MVP Chat Functionality", test_mvp_chat),
        ("MVP Functions", test_mvp_functions),
        ("Server Components", test_server_components),
        ("Configuration", test_configuration),
        ("Integration", test_integration),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        if test_function(name, test_func):
            passed += 1
        else:
            failed += 1
    
    print("=" * 40)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 MVP tests passed! The system is ready.")
        print("\n🚀 To run the MVP server:")
        print("   python mvp_server.py")
        print("\n📋 Available at:")
        print("   • http://localhost:8080 - Main interface")
        print("   • http://localhost:8080/dashboard - Interactive dashboard")
        return 0
    else:
        print("💥 Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())