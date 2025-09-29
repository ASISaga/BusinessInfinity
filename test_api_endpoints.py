"""
Simple test runner for the new API endpoints
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock Azure Functions request and response objects for testing
class MockHttpRequest:
    def __init__(self, method="GET", params=None, headers=None, body=None):
        self.method = method
        self.params = params or {}
        self.headers = headers or {}
        self._body = body or {}
    
    def get_json(self):
        return self._body


class MockHttpResponse:
    def __init__(self, body, mimetype="application/json", status_code=200, headers=None):
        self.body = body
        self.mimetype = mimetype
        self.status_code = status_code
        self.headers = headers or {}


def test_export_data_endpoint():
    """Test the data export endpoint"""
    print("Testing /api/onboarding/export-data endpoint...")
    
    try:
        # Import the endpoint function
        from function_app import export_customer_data
        import asyncio
        
        # Create mock request
        request = MockHttpRequest(
            method="GET",
            params={"customer_id": "test_customer"},
            headers={"x-user-id": "test_user", "x-customer-id": "test_customer"}
        )
        
        # Call endpoint
        response = asyncio.run(export_customer_data(request))
        
        # Verify response
        assert response.status_code == 200
        response_data = json.loads(response.body)
        
        assert "export_id" in response_data
        assert "customer_id" in response_data
        assert "data" in response_data
        assert "integrity_hash" in response_data
        assert response_data["customer_id"] == "test_customer"
        
        print("✓ Export data endpoint test passed")
        return True
        
    except Exception as e:
        print(f"✗ Export data endpoint test failed: {e}")
        return False


def test_request_deletion_endpoint():
    """Test the data deletion request endpoint"""
    print("Testing /api/onboarding/request-deletion endpoint...")
    
    try:
        from function_app import request_data_deletion
        import asyncio
        
        # Test initial deletion request
        request = MockHttpRequest(
            method="POST",
            headers={"x-user-id": "test_user", "x-customer-id": "test_customer"},
            body={"customer_id": "test_customer"}
        )
        
        response = asyncio.run(request_data_deletion(request))
        
        assert response.status_code == 200
        response_data = json.loads(response.body)
        
        assert "request_id" in response_data
        assert response_data["status"] == "pending_confirmation"
        assert response_data["confirmation_required"] is True
        
        # Test confirmation step
        request_confirmation = MockHttpRequest(
            method="POST",
            headers={"x-user-id": "test_user", "x-customer-id": "test_customer"},
            body={
                "customer_id": "test_customer", 
                "confirm": True,
                "request_id": response_data["request_id"]
            }
        )
        
        response_confirm = asyncio.run(request_data_deletion(request_confirmation))
        assert response_confirm.status_code == 200
        
        confirm_data = json.loads(response_confirm.body)
        assert confirm_data["status"] == "confirmed"
        assert confirm_data["confirmed"] is True
        
        print("✓ Request deletion endpoint test passed")
        return True
        
    except Exception as e:
        print(f"✗ Request deletion endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rbac_endpoint():
    """Test the RBAC info endpoint"""
    print("Testing /api/onboarding/rbac endpoint...")
    
    try:
        from function_app import get_rbac_info
        import asyncio
        
        request = MockHttpRequest(
            method="GET",
            headers={"x-user-id": "test_user", "x-customer-id": "test_customer"}
        )
        
        response = asyncio.run(get_rbac_info(request))
        
        assert response.status_code == 200
        response_data = json.loads(response.body)
        
        assert "user_id" in response_data
        assert "role" in response_data
        assert "permissions" in response_data
        assert "governance_defaults" in response_data
        
        print("✓ RBAC endpoint test passed")
        return True
        
    except Exception as e:
        print(f"✗ RBAC endpoint test failed: {e}")
        return False


def test_incident_contact_endpoint():
    """Test the incident contact endpoint"""
    print("Testing /api/onboarding/incident-contact endpoint...")
    
    try:
        from function_app import get_incident_contact_info
        import asyncio
        
        request = MockHttpRequest(method="GET")
        
        response = asyncio.run(get_incident_contact_info(request))
        
        assert response.status_code == 200
        response_data = json.loads(response.body)
        
        assert "incident_response" in response_data
        assert "escalation_path" in response_data["incident_response"]
        assert "breach_notification" in response_data
        
        print("✓ Incident contact endpoint test passed")
        return True
        
    except Exception as e:
        print(f"✗ Incident contact endpoint test failed: {e}")
        return False


def test_retention_policy_endpoint():
    """Test the retention policy endpoint"""
    print("Testing /api/onboarding/retention-policy endpoint...")
    
    try:
        from function_app import get_retention_policy
        import asyncio
        
        request = MockHttpRequest(method="GET")
        
        response = asyncio.run(get_retention_policy(request))
        
        assert response.status_code == 200
        response_data = json.loads(response.body)
        
        assert "data_retention" in response_data
        assert "deletion_policies" in response_data
        assert "gdpr_compliance" in response_data
        
        print("✓ Retention policy endpoint test passed")
        return True
        
    except Exception as e:
        print(f"✗ Retention policy endpoint test failed: {e}")
        return False


def test_enhanced_consent_logging():
    """Test the enhanced consent logging in existing endpoints"""
    print("Testing enhanced consent logging...")
    
    try:
        from function_app import handle_quick_action, connect_system
        import asyncio
        
        # Test quick action endpoint
        quick_action_request = MockHttpRequest(
            method="POST",
            body={
                "message": "a", 
                "user_id": "test_user",
                "customer_id": "test_customer"
            }
        )
        
        response = asyncio.run(handle_quick_action(quick_action_request))
        assert response.status_code == 200
        
        response_data = json.loads(response.body)
        assert response_data["consent_logged"] is True
        assert response_data["action_type"] == "cfo_analysis"
        
        # Test connect system endpoint
        connect_request = MockHttpRequest(
            method="POST",
            body={
                "system": "salesforce",
                "user_id": "test_user",
                "customer_id": "test_customer"
            }
        )
        
        connect_response = asyncio.run(connect_system(connect_request))
        assert connect_response.status_code == 200
        
        connect_data = json.loads(connect_response.body)
        assert connect_data["consent_logged"] is True
        
        print("✓ Enhanced consent logging test passed")
        return True
        
    except Exception as e:
        print(f"✗ Enhanced consent logging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_endpoint_tests():
    """Run all endpoint tests"""
    print("Running Trust and Compliance API endpoint tests...")
    print("=" * 50)
    
    tests = [
        test_export_data_endpoint,
        test_request_deletion_endpoint,
        test_rbac_endpoint,
        test_incident_contact_endpoint,
        test_retention_policy_endpoint,
        test_enhanced_consent_logging
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API endpoint tests passed successfully!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = run_endpoint_tests()
    sys.exit(0 if success else 1)