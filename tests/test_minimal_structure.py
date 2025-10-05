from BusinessAgent import BusinessAgent
#!/usr/bin/env python3
"""
Minimal test script to verify the new BusinessInfinity package structure
without requiring full AOS dependencies.
"""



def test_package_imports():
    """Test that the package structure can be imported."""
    print("Testing Business Infinity 2.0 package imports...")
    
    try:
        # Test core configuration import
        from business_infinity.core.config import BusinessInfinityConfig
        print("✅ Configuration classes imported successfully")
        
        # Test agent imports
        from BusinessAgent import BusinessAgent
        from CEO import ChiefExecutiveOfficer
        from CTO import ChiefTechnologyOfficer
        from Founder import FounderAgent
        print("✅ Agent classes imported successfully")
        
        # Test workflow imports
        from business_infinity.workflows.manager import BusinessWorkflowManager, WorkflowStatus
        print("✅ Workflow classes imported successfully")
        
        # Test analytics imports
        from business_infinity.analytics.manager import BusinessAnalyticsManager, BusinessMetric, MetricType
        print("✅ Analytics classes imported successfully")
        
        # Test main package imports
        from src.tools import __version__, __author__, __description__
        print(f"✅ Package metadata imported: v{__version__} by {__author__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration_creation():
    """Test that configuration can be created."""
    print("\nTesting configuration creation...")
    
    try:
        from business_infinity.core.config import (
            BusinessInfinityConfig,
            create_default_config,
            create_development_config,
            create_production_config
        )
        
        # Test default config
        config = create_default_config()
        print(f"✅ Default config: {config.company_name}")
        
        # Test development config
        dev_config = create_development_config()
        print(f"✅ Development config: {dev_config.environment_config.get('environment', 'unknown')}")
        
        # Test production config
        prod_config = create_production_config()
        print(f"✅ Production config: {prod_config.environment_config.get('environment', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

def test_agent_class_structure():
    """Test that agent classes have expected structure."""
    print("\nTesting agent class structure...")
    
    try:
        from CEO import ChiefExecutiveOfficer
        from CTO import ChiefTechnologyOfficer
        from Founder import FounderAgent
        
        # Check that classes have expected attributes
        print(f"✅ CEO class: {ChiefExecutiveOfficer.__name__}")
        print(f"✅ CTO class: {ChiefTechnologyOfficer.__name__}")
        print(f"✅ Founder class: {FounderAgent.__name__}")
        
        # Check that they inherit from BusinessAgent
        from BusinessAgent import BusinessAgent
        assert issubclass(ChiefExecutiveOfficer, BusinessAgent)
        assert issubclass(ChiefTechnologyOfficer, BusinessAgent)
        assert issubclass(FounderAgent, BusinessAgent)
        print("✅ All agents properly inherit from BusinessAgent")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent structure test error: {e}")
        return False

def test_package_structure():
    """Test the overall package structure."""
    print("\nTesting package structure...")
    
    try:
        # Test that main package imports work
        from src.tools import (
            BusinessInfinityConfig,
            BusinessAgent,
            ChiefExecutiveOfficer,
            ChiefTechnologyOfficer,
            FounderAgent,
            BusinessWorkflowManager,
            WorkflowStatus,
            BusinessAnalyticsManager,
            BusinessMetric,
            MetricType
        )
        
        print("✅ All main package imports successful")
        
        # Test convenience functions exist
        from src.tools import (
            create_default_config,
            create_production_config,
            create_development_config
        )
        
        print("✅ Configuration factory functions available")
        
        return True
        
    except Exception as e:
        print(f"❌ Package structure test error: {e}")
        return False

def main():
    """Run all tests."""
    print("Business Infinity 2.0 - Minimal Package Structure Test")
    print("=" * 60)
    
    success = True
    
    # Test imports
    if not test_package_imports():
        success = False
    
    # Test configuration
    if not test_configuration_creation():
        success = False
    
    # Test agent structure
    if not test_agent_class_structure():
        success = False
    
    # Test package structure
    if not test_package_structure():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All package structure tests passed!")
        print("📦 Business Infinity 2.0 package structure is working correctly")
        print("\n📋 Package Components Verified:")
        print("   ✅ Core Application Structure")
        print("   ✅ Configuration Management")
        print("   ✅ Business Agent Classes")
        print("   ✅ Workflow Management Classes")
        print("   ✅ Analytics Engine Classes")
        print("   ✅ Package Import Structure")
        print("   ✅ Factory Functions")
        print("\n🚀 Ready for integration with AOS infrastructure!")
    else:
        print("❌ Some package structure tests failed")
        print("🔧 Please check the error messages above")
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())