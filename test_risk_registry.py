"""
Tests for Risk Management System

Basic tests to validate Risk Registry functionality.
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from risk import RiskRegistry, RiskSeverity, RiskStatus, RiskCategory


async def test_risk_registry():
    """Test Risk Registry basic functionality"""
    print("Testing Risk Registry...")
    
    # Initialize registry
    registry = RiskRegistry()
    
    # Test 1: Register a risk
    print("\n1. Testing risk registration...")
    risk_data = {
        'title': 'Test Security Risk',
        'description': 'This is a test security risk',
        'category': 'security',
        'owner': 'test@company.com',
        'tags': ['test', 'security']
    }
    
    risk = await registry.register_risk(risk_data)
    assert risk is not None, "Risk should be created"
    assert risk.title == 'Test Security Risk', "Risk title should match"
    assert risk.category == RiskCategory.SECURITY, "Risk category should be security"
    assert risk.status == RiskStatus.IDENTIFIED, "Initial status should be IDENTIFIED"
    print("✅ Risk registration successful")
    
    # Test 2: Assess a risk
    print("\n2. Testing risk assessment...")
    assessed_risk = await registry.assess_risk(
        risk_id=risk.id,
        likelihood=0.9,
        impact=0.9,
        assessor='assessor@company.com',
        notes='Critical risk assessment'
    )
    
    assert assessed_risk.assessment is not None, "Assessment should exist"
    assert assessed_risk.assessment.severity == RiskSeverity.CRITICAL, "Should be critical severity (0.9 * 0.9 = 0.81)"
    assert assessed_risk.status == RiskStatus.ASSESSING, "Status should be ASSESSING"
    print(f"✅ Risk assessment successful - Severity: {assessed_risk.assessment.severity.value}")
    
    # Test 3: Add mitigation plan
    print("\n3. Testing mitigation plan...")
    mitigated_risk = await registry.add_mitigation_plan(
        risk_id=risk.id,
        mitigation_plan='Implement security patches',
        mitigation_owner='security@company.com',
        deadline_days=1
    )
    
    assert mitigated_risk.mitigation_plan is not None, "Mitigation plan should exist"
    assert mitigated_risk.status == RiskStatus.MITIGATING, "Status should be MITIGATING"
    print("✅ Mitigation plan added successfully")
    
    # Test 4: Update risk status
    print("\n4. Testing status update...")
    resolved_risk = await registry.update_risk_status(
        risk_id=risk.id,
        status=RiskStatus.RESOLVED
    )
    
    assert resolved_risk.status == RiskStatus.RESOLVED, "Status should be RESOLVED"
    assert resolved_risk.resolution_date is not None, "Resolution date should be set"
    print("✅ Risk status updated successfully")
    
    # Test 5: Query risks
    print("\n5. Testing risk queries...")
    
    # Add another risk for querying
    risk_data_2 = {
        'title': 'Test Operational Risk',
        'description': 'This is a test operational risk',
        'category': 'operational',
        'owner': 'ops@company.com'
    }
    risk2 = await registry.register_risk(risk_data_2)
    
    # Get all risks by status
    identified_risks = await registry.get_risks_by_status(RiskStatus.IDENTIFIED)
    assert len(identified_risks) == 1, "Should have 1 identified risk"
    
    # Get risks by owner
    owner_risks = await registry.get_risks_by_owner('test@company.com')
    assert len(owner_risks) == 1, "Should have 1 risk for test@company.com"
    
    # Get summary
    summary = await registry.get_risks_summary()
    assert summary['total_risks'] == 2, "Should have 2 total risks"
    print("✅ Risk queries successful")
    print(f"   Total risks: {summary['total_risks']}")
    print(f"   By status: {summary['by_status']}")
    
    # Test 6: Severity calculation
    print("\n6. Testing severity calculation...")
    test_cases = [
        (0.9, 0.9, RiskSeverity.CRITICAL),  # 0.81 >= 0.8
        (0.8, 0.8, RiskSeverity.HIGH),      # 0.64 >= 0.6
        (0.5, 0.6, RiskSeverity.MEDIUM),    # 0.30 >= 0.3
        (0.4, 0.3, RiskSeverity.LOW),       # 0.12 >= 0.1
        (0.1, 0.5, RiskSeverity.INFO)       # 0.05 < 0.1
    ]
    
    for likelihood, impact, expected_severity in test_cases:
        severity = registry._calculate_severity(likelihood, impact)
        assert severity == expected_severity, f"Severity should be {expected_severity.value}"
    
    print("✅ Severity calculation successful")
    
    print("\n" + "="*60)
    print("All Risk Registry tests passed! ✅")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(test_risk_registry())
