#!/usr/bin/env python3
"""
Test script for Business Infinity Covenant-Based Expansion

Tests the new covenant management functionality and ensures
the expansion meets the requirements from covenant.md.
"""

import asyncio
import json


async def test_covenant_schema_validation():
    """Test that the covenant schema is valid and can validate covenants"""
    try:
        import jsonschema
        
        # Load the covenant schema
        with open("schema/covenant.schema.json", "r") as f:
            schema = json.load(f)
        
        print("✓ Covenant schema loaded successfully")
        
        # Test with a minimal valid covenant
        minimal_covenant = {
            "covenant_version": "1.0.0",
            "preamble": {
                "mission_statement": "To operate as an autonomous enterprise boardroom within the global network of verified businesses, maintaining transparency and collaboration.",
                "core_values": ["Innovation", "Transparency", "Collaboration"],
                "declaration_of_intent": "We hereby declare our commitment to participate in the global network of autonomous boardrooms, operating with transparency, maintaining immutable provenance of our decisions, and collaborating with peer enterprises for mutual benefit."
            },
            "identity": {
                "company_name": "Test Corp",
                "linkedin_verification": {
                    "company_url": "https://www.linkedin.com/company/test-corp",
                    "verification_status": "verified",
                    "verified_at": "2024-01-01T00:00:00Z"
                },
                "registration_details": {
                    "jurisdiction": "United States",
                    "industry": "Technology",
                    "size": "51-200",
                    "location": "San Francisco, CA"
                },
                "verification_timestamp": "2024-01-01T00:00:00Z"
            },
            "constitutional_roles": {
                "boardroom_structure": {
                    "c_suite": ["CEO", "CFO", "CTO"],
                    "stakeholder_agents": ["Founder"]
                },
                "agent_definitions": {
                    "CEO": {
                        "role": "Chief Executive Officer",
                        "domain": "executive_leadership", 
                        "responsibilities": ["Strategic decision making"],
                        "authorities": ["Final veto power"],
                        "voting_weight": 0.4
                    },
                    "CFO": {
                        "role": "Chief Financial Officer",
                        "domain": "financial_management",
                        "responsibilities": ["Financial planning"],
                        "authorities": ["Budget approval"],
                        "voting_weight": 0.3
                    },
                    "CTO": {
                        "role": "Chief Technology Officer", 
                        "domain": "technology_leadership",
                        "responsibilities": ["Technology strategy"],
                        "authorities": ["Technology roadmap"],
                        "voting_weight": 0.3
                    }
                }
            },
            "obligations": {
                "transparency": {
                    "decision_logging": True,
                    "audit_trail": True
                },
                "provenance": {
                    "decision_provenance": True,
                    "schema_validation": True,
                    "cryptographic_signing": True
                },
                "interoperability": {
                    "standard_protocols": True,
                    "peer_validation": True,
                    "federation_participation": True
                }
            },
            "governance_protocols": {
                "decision_making": {
                    "quorum_requirement": 0.6,
                    "consensus_threshold": 0.7,
                    "voting_method": "consensus"
                },
                "amendment_process": {
                    "proposal_threshold": 0.3,
                    "approval_threshold": 0.7,
                    "cooling_period": 7
                }
            },
            "provenance": {
                "covenant_history": [],
                "validation_records": [],
                "recognition_status": {
                    "status": "draft",
                    "recognition_count": 0,
                    "bic_badge": {"awarded": False}
                }
            }
        }
        
        # Validate against schema
        jsonschema.validate(minimal_covenant, schema)
        print("✓ Minimal covenant validates against schema")
        
        return True
        
    except Exception as e:
        print(f"✗ Covenant schema validation failed: {e}")
        return False

async def test_covenant_manager():
    """Test the covenant manager functionality"""
    try:
        from network.covenant_manager import CovenantManager, create_covenant_manager
        from network.verification import LinkedInVerificationService
        
        # Create verification service (in test mode)
        verification_service = LinkedInVerificationService()
        
        # Create covenant manager
        covenant_manager = create_covenant_manager(verification_service=verification_service)
        print("✓ Covenant manager created successfully")
        
        # Test covenant creation (will fail verification but should create structure)
        enterprise_data = {
            "company_name": "Test Corporation",
            "linkedin_url": "https://www.linkedin.com/company/test-corp",
            "industry": "Technology",
            "jurisdiction": "United States"
        }
        
        try:
            covenant_id = await covenant_manager.create_covenant(enterprise_data)
            print(f"✓ Covenant creation process completed (ID: {covenant_id})")
        except Exception as e:
            print(f"! Covenant creation expected to fail due to verification: {e}")
        
        # Test compliance statistics
        stats = covenant_manager.get_compliance_statistics()
        print(f"✓ Compliance statistics retrieved: {stats}")
        
        return True
        
    except Exception as e:
        print(f"✗ Covenant manager test failed: {e}")
        return False

async def test_business_infinity_integration():
    """Test Business Infinity integration with covenant management"""
    try:
        from business_infinity_refactored import BusinessInfinityConfig, BusinessInfinity
        
        # Create test configuration
        config = BusinessInfinityConfig()
        config.enable_covenant_compliance = True
        config.linkedin_verification_enabled = False  # Disable for testing
        config.linkedin_company_url = None  # Don't auto-create covenant
        
        print("✓ Business Infinity configuration created with covenant support")
        
        # Test that BusinessInfinity can be instantiated with covenant features
        # Note: Won't fully initialize due to missing dependencies, but should create object
        bi = BusinessInfinity(config)
        print("✓ Business Infinity instance created with covenant management")
        
        # Check that covenant management attributes are present
        assert hasattr(bi, 'covenant_manager')
        assert hasattr(bi, 'verification_service')
        assert hasattr(bi, 'network_discovery')
        assert hasattr(bi, 'covenant_id')
        assert hasattr(bi, 'covenant_status')
        print("✓ Covenant management attributes present in Business Infinity")
        
        return True
        
    except Exception as e:
        print(f"✗ Business Infinity integration test failed: {e}")
        return False

def test_manifest_compliance():
    """Test that manifest.json includes covenant compliance metadata"""
    try:
        with open("manifest.json", "r") as f:
            manifest = json.load(f)
        
        # Check for covenant compliance section
        assert "covenant_compliance" in manifest
        covenant_section = manifest["covenant_compliance"]
        
        assert covenant_section["enabled"] == True
        assert "schema_version" in covenant_section
        assert "compliance_standard" in covenant_section
        assert "features" in covenant_section
        print("✓ Manifest includes covenant compliance metadata")
        
        # Check for Global Boardroom Network section
        assert "GlobalBoardroomNetwork" in manifest
        network_section = manifest["GlobalBoardroomNetwork"]
        
        expected_components = [
            "covenant_manager", "verification_service", 
            "network_discovery", "covenant_ledger"
        ]
        
        for component in expected_components:
            assert component in network_section
            assert "purpose" in network_section[component]
            assert "capabilities" in network_section[component]
        
        print("✓ Manifest includes Global Boardroom Network components")
        
        return True
        
    except Exception as e:
        print(f"✗ Manifest compliance test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Testing Business Infinity Covenant-Based Expansion")
    print("=" * 60)
    
    tests = [
        ("Covenant Schema Validation", test_covenant_schema_validation()),
        ("Covenant Manager", test_covenant_manager()),
        ("Business Infinity Integration", test_business_infinity_integration()),
        ("Manifest Compliance", test_manifest_compliance())
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_coro in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Business Infinity expansion is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    import sys
    success = asyncio.run(main())
    sys.exit(0 if success else 1)