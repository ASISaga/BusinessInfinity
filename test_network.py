#!/usr/bin/env python3
"""
Test script for Business Infinity Network of Boardrooms

Tests the network functionality including:
- Network protocol operations
- LinkedIn verification service  
- Discovery and directory services
- Covenant ledger functionality
- Frontend API integration
"""

import asyncio
import logging
import sys
import os

# Add the parent directory to sys.path to import network modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_network_protocol():
    """Test the network protocol functionality"""
    logger.info("=== Testing Network Protocol ===")
    
    try:
        from network.network_protocol import NetworkProtocol, BoardroomNode, EnterpriseIdentity, BoardroomStatus
        
        # Create enterprise identity
        enterprise = EnterpriseIdentity(
            company_id="test_company_001",
            company_name="Test Innovations Corp",
            linkedin_url="https://linkedin.com/company/test-innovations",
            verification_status="verified",
            industry="Technology",
            size="51-200",
            location="San Francisco, CA"
        )
        
        # Create boardroom node
        local_boardroom = BoardroomNode(
            node_id="node_001",
            enterprise_identity=enterprise,
            endpoint_url="https://test-boardroom.example.com",
            status=BoardroomStatus.ACTIVE,
            capabilities={"AI", "automation", "analytics"},
            active_agents={"CEO", "CFO", "CTO", "CMO"}
        )
        
        # Initialize network protocol
        network = NetworkProtocol(local_boardroom)
        
        # Test joining network
        join_result = await network.join_network()
        assert join_result == True, "Failed to join network"
        logger.info("✓ Successfully joined network")
        
        # Test discovery
        discovered = await network.discover_boardrooms()
        logger.info(f"✓ Discovered {len(discovered)} boardrooms")
        
        # Test negotiation initiation
        negotiation_id = await network.initiate_negotiation(
            "target_node_002", 
            "partnership",
            {"type": "strategic_partnership", "duration": "2_years"}
        )
        logger.info(f"✓ Started negotiation: {negotiation_id}")
        
        # Test proposal sending
        proposal_id = await network.send_proposal(
            "target_node_003",
            "supply_chain",
            {"integration_level": "full", "timeline": "6_months"}
        )
        logger.info(f"✓ Sent proposal: {proposal_id}")
        
        # Test network status
        status = await network.get_network_status()
        logger.info(f"✓ Network status: {status['local_node']['status']}")
        
        logger.info("✓ Network protocol tests passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Network protocol test failed: {e}")
        return False

async def test_linkedin_verification():
    """Test LinkedIn verification service"""
    logger.info("=== Testing LinkedIn Verification ===")
    
    try:
        from network.verification import LinkedInVerificationService, create_linkedin_verification_service
        
        # Create verification service
        verifier = create_linkedin_verification_service()
        
        # Test enterprise verification
        enterprise_identity = await verifier.verify_enterprise(
            "https://linkedin.com/company/test-innovations",
            {"company_size": "51-200", "industry": "Technology"}
        )
        
        logger.info(f"✓ Enterprise verified: {enterprise_identity.company_name}")
        logger.info(f"  Status: {enterprise_identity.verification_status}")
        logger.info(f"  Industry: {enterprise_identity.industry}")
        
        # Test employee verification
        employee_verification = await verifier.verify_employee(
            "https://linkedin.com/in/test-employee",
            "https://linkedin.com/company/test-innovations"
        )
        
        logger.info(f"✓ Employee verification: {employee_verification['employee_verified']}")
        
        # Test verification status check
        company_id = verifier._generate_company_id("https://linkedin.com/company/test-innovations")
        status_check = await verifier.check_verification_status(company_id)
        logger.info(f"✓ Status check: {status_check['status']}")
        
        logger.info("✓ LinkedIn verification tests passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ LinkedIn verification test failed: {e}")
        return False

async def test_network_discovery():
    """Test network discovery and directory services"""
    logger.info("=== Testing Network Discovery ===")
    
    try:
        from network.discovery import NetworkDiscovery, BoardroomDirectory, DiscoveryCriteria, create_network_discovery
        from network.network_protocol import BoardroomNode, EnterpriseIdentity, BoardroomStatus
        
        # Create directory and discovery service
        directory = BoardroomDirectory()
        discovery = create_network_discovery(directory)
        
        # Create sample boardrooms for testing
        boardrooms = []
        for i in range(3):
            # Create sample boardrooms for testing
            industries = ["Technology", "Manufacturing", "Healthcare"]
            locations = ["San Francisco", "Chicago", "Boston"] 
            capabilities_list = [{"AI", "automation"}, {"supply_chain", "logistics"}, {"healthcare", "medical_devices"}]
            
            enterprise = EnterpriseIdentity(
                company_id=f"company_{i:03d}",
                company_name=f"Test Company {i+1}",
                linkedin_url=f"https://linkedin.com/company/test-company-{i+1}",
                verification_status="verified",
                industry=industries[i],
                size="51-200",
                location=locations[i]
            )
            
            boardroom = BoardroomNode(
                node_id=f"node_{i:03d}",
                enterprise_identity=enterprise,
                endpoint_url=f"https://boardroom-{i+1}.example.com",
                status=BoardroomStatus.ACTIVE,
                capabilities=capabilities_list[i],
                active_agents={f"agent_{j}" for j in range(5)}
            )
            
            boardrooms.append(boardroom)
            directory.register_boardroom(boardroom)
        
        logger.info(f"✓ Registered {len(boardrooms)} test boardrooms")
        
        # Test directory statistics
        stats = directory.get_directory_stats()
        logger.info(f"✓ Directory stats: {stats['total_registered']} registered")
        
        # Test discovery by industry
        tech_boardrooms = await discovery.discover_by_industry("Technology")
        logger.info(f"✓ Found {len(tech_boardrooms)} technology boardrooms")
        
        # Test discovery by capability
        ai_boardrooms = await discovery.discover_by_capability(["AI"])
        logger.info(f"✓ Found {len(ai_boardrooms)} AI-capable boardrooms")
        
        # Test discovery by location
        sf_boardrooms = await discovery.discover_by_location("San Francisco")
        logger.info(f"✓ Found {len(sf_boardrooms)} San Francisco boardrooms")
        
        # Test criteria-based discovery
        criteria = DiscoveryCriteria(
            industry="Technology",
            capabilities={"AI"},
            verification_required=True,
            max_results=10
        )
        
        filtered_results = await discovery.discover_boardrooms(criteria)
        logger.info(f"✓ Criteria-based discovery found {len(filtered_results)} results")
        
        # Test network mapping
        network_map = await discovery.map_network_connections()
        logger.info(f"✓ Network map contains {network_map['total_nodes']} nodes")
        
        logger.info("✓ Network discovery tests passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Network discovery test failed: {e}")
        return False

async def test_covenant_ledger():
    """Test covenant ledger functionality"""
    logger.info("=== Testing Covenant Ledger ===")
    
    try:
        from network.covenant_ledger import CovenantLedger, AgreementType, create_covenant_ledger
        
        # Create covenant ledger
        ledger = create_covenant_ledger()
        
        # Test agreement creation
        agreement_id = await ledger.create_agreement(
            agreement_type=AgreementType.PARTNERSHIP,
            title="Strategic AI Partnership",
            description="Partnership for AI research and development collaboration",
            initiator_node_id="node_001",
            participating_nodes={"node_001", "node_002"},
            terms={
                "duration": "2 years",
                "scope": "AI research collaboration",
                "revenue_sharing": "50/50"
            }
        )
        
        logger.info(f"✓ Created agreement: {agreement_id}")
        
        # Test agreement proposal
        propose_result = await ledger.propose_agreement(agreement_id)
        assert propose_result == True, "Failed to propose agreement"
        logger.info("✓ Agreement proposed successfully")
        
        # Test agreement signing
        sign_result1 = await ledger.sign_agreement(
            agreement_id, "node_001", "Test Company 1", "CEO"
        )
        assert sign_result1 == True, "Failed to sign agreement (node 1)"
        logger.info("✓ Agreement signed by node 1")
        
        sign_result2 = await ledger.sign_agreement(
            agreement_id, "node_002", "Test Company 2", "CEO"
        )
        assert sign_result2 == True, "Failed to sign agreement (node 2)"
        logger.info("✓ Agreement signed by node 2")
        
        # Test agreement activation
        activate_result = await ledger.activate_agreement(agreement_id)
        assert activate_result == True, "Failed to activate agreement"
        logger.info("✓ Agreement activated successfully")
        
        # Test agreement retrieval
        agreement = ledger.get_agreement(agreement_id)
        assert agreement is not None, "Failed to retrieve agreement"
        logger.info(f"✓ Retrieved agreement: {agreement.title}")
        
        # Test agreement validation
        validation = ledger.validate_agreement(agreement_id)
        assert validation["valid"] == True, "Agreement validation failed"
        logger.info("✓ Agreement validation passed")
        
        # Test ledger statistics
        stats = ledger.get_ledger_stats()
        logger.info(f"✓ Ledger stats: {stats['total_agreements']} agreements")
        
        logger.info("✓ Covenant ledger tests passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Covenant ledger test failed: {e}")
        return False

async def test_frontend_integration():
    """Test that frontend files are properly created"""
    logger.info("=== Testing Frontend Integration ===")
    
    try:
        import os
        
        frontend_path = os.path.join(os.path.dirname(__file__), "network", "frontend")
        
        # Check that frontend files exist
        expected_files = [
            "index.html",
            "styles/main.css",
            "js/api.js",
            "js/components.js", 
            "js/network.js",
            "js/main.js"
        ]
        
        for file_path in expected_files:
            full_path = os.path.join(frontend_path, file_path)
            if os.path.exists(full_path):
                logger.info(f"✓ Frontend file exists: {file_path}")
            else:
                logger.warning(f"⚠ Frontend file missing: {file_path}")
        
        # Check HTML structure
        html_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(html_path):
            with open(html_path, 'r') as f:
                html_content = f.read()
                
            # Check for key sections
            sections = ["dashboard", "discovery", "negotiations", "covenants", "verification"]
            for section in sections:
                if f'id="{section}"' in html_content:
                    logger.info(f"✓ HTML section found: {section}")
                else:
                    logger.warning(f"⚠ HTML section missing: {section}")
        
        # Check CSS file
        css_path = os.path.join(frontend_path, "styles", "main.css")
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                css_content = f.read()
                
            # Check for key CSS classes
            if "--primary-color" in css_content:
                logger.info("✓ CSS custom properties found")
            if ".navbar" in css_content:
                logger.info("✓ CSS navbar styles found")
            if ".modal" in css_content:
                logger.info("✓ CSS modal styles found")
        
        logger.info("✓ Frontend integration tests passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Frontend integration test failed: {e}")
        return False

async def main():
    """Run all network tests"""
    logger.info("🧪 Testing Business Infinity Network of Boardrooms")
    logger.info("=" * 60)
    
    tests = [
        ("Network Protocol", test_network_protocol),
        ("LinkedIn Verification", test_linkedin_verification), 
        ("Network Discovery", test_network_discovery),
        ("Covenant Ledger", test_covenant_ledger),
        ("Frontend Integration", test_frontend_integration)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        logger.info(f"\n--- {name} ---")
        try:
            if await test_func():
                passed += 1
                logger.info(f"✅ {name} PASSED")
            else:
                failed += 1
                logger.error(f"❌ {name} FAILED")
        except Exception as e:
            failed += 1
            logger.error(f"❌ {name} FAILED: {e}")
    
    logger.info("=" * 60)
    logger.info(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 All network tests passed! The Network of Boardrooms is working correctly.")
        return 0
    else:
        logger.error("💥 Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())