# Trust and Compliance API Documentation

This document describes the trust and compliance features implemented in the Business Infinity onboarding backend. These features ensure GDPR compliance, data transparency, and customer trust.

## Overview

The trust and compliance system provides:
- Customer data export capabilities (Right to Data Portability)
- Data deletion requests (Right to be Forgotten)
- Role-based access control (RBAC) information
- Incident response contact information
- Data retention policy transparency
- Comprehensive consent logging

## Authentication

All endpoints require authentication using Azure Functions authentication:
- **Auth Level**: `FUNCTION`
- **Headers**: 
  - `x-customer-id`: Customer partition identifier
  - `x-user-id`: User identifier for audit purposes
  - `x-functions-key`: Azure Functions API key

## API Endpoints

### 1. Data Export API

**Endpoint**: `GET /api/onboarding/export-data`

**Purpose**: Allows customers to export all data associated with their partition in compliance with GDPR Article 20 (Right to data portability).

**Headers**:
```
x-customer-id: customer_123
x-user-id: user_456
x-functions-key: your_function_key
```

**Response**:
```json
{
  "export_id": "export_customer_123_20241215_143000",
  "customer_id": "customer_123",
  "export_timestamp": "2024-12-15T14:30:00Z",
  "data_types": ["customer_profile", "onboarding_data", "governance_settings"],
  "data": {
    "customer_profile": {
      "customer_id": "customer_123",
      "business_name": "Business_customer_123",
      "contact_info": {"email": "contact@business_customer_123.com"}
    },
    "onboarding_data": {
      "linkedin_profile": {"connected": true},
      "website_analysis": {"url": "https://business_customer_123.com"},
      "financial_documents": {"uploaded": true, "count": 3}
    },
    "governance_settings": {
      "data_visibility": "private_to_customer",
      "notification_frequency": "weekly"
    }
  },
  "integrity_hash": "a1b2c3d4e5f6...",
  "export_info": {
    "format": "json",
    "compliance": "GDPR Article 20 - Right to data portability",
    "verification": "SHA-256 integrity hash included"
  }
}
```

### 2. Data Deletion Request API

**Endpoint**: `POST /api/onboarding/request-deletion`

**Purpose**: Allows customers to request deletion of their partition data in compliance with GDPR Article 17 (Right to erasure).

**Request Body (Initial Request)**:
```json
{
  "customer_id": "customer_123"
}
```

**Response (Initial Request)**:
```json
{
  "request_id": "del_customer_123_20241215_143000",
  "status": "pending_confirmation",
  "confirmation_required": true,
  "sla_completion_date": "2025-01-14T14:30:00Z",
  "sla_days": 30,
  "message": "Deletion request created. Please confirm by sending another request with 'confirm': true",
  "next_steps": {
    "confirmation": "POST to same endpoint with 'confirm': true",
    "cancellation": "Contact support to cancel request"
  }
}
```

**Request Body (Confirmation)**:
```json
{
  "customer_id": "customer_123",
  "confirm": true,
  "request_id": "del_customer_123_20241215_143000"
}
```

**Response (Confirmation)**:
```json
{
  "request_id": "del_customer_123_20241215_143000",
  "status": "confirmed",
  "confirmed": true,
  "message": "Deletion request confirmed. Processing will begin within 24 hours.",
  "sla_days": 30,
  "gdpr_notice": "This fulfills your right to erasure under GDPR Article 17"
}
```

### 3. RBAC Information API

**Endpoint**: `GET /api/onboarding/rbac`

**Purpose**: Provides transparency about user roles, permissions, and governance defaults.

**Response**:
```json
{
  "user_id": "user_456",
  "customer_id": "customer_123",
  "role": "customer",
  "permissions": [
    "view_own_data",
    "export_own_data",
    "request_deletion"
  ],
  "restrictions": [
    "no_cross_customer_access"
  ],
  "governance_defaults": {
    "data_visibility": "private_to_customer",
    "notification_frequency": "weekly",
    "access_logging": "enabled",
    "retention_period_days": 2555,
    "backup_retention_days": 90
  },
  "last_updated": "2024-12-15T14:30:00Z"
}
```

### 4. Incident Contact Information API

**Endpoint**: `GET /api/onboarding/incident-contact`

**Purpose**: Provides incident response and escalation contact information based on trust-compliance.md specifications.

**Response**:
```json
{
  "incident_response": {
    "primary_contact": {
      "email": "security@businessinfinity.asisaga.com",
      "response_time_sla": "4 hours",
      "escalation_threshold": "critical security incidents"
    },
    "escalation_path": [
      {
        "level": 1,
        "role": "Customer Success",
        "contact": "support@businessinfinity.asisaga.com",
        "response_time": "2 hours"
      },
      {
        "level": 2,
        "role": "App Developers", 
        "contact": "dev@businessinfinity.asisaga.com",
        "response_time": "4 hours"
      },
      {
        "level": 3,
        "role": "Infra Maintainers",
        "contact": "infra@businessinfinity.asisaga.com",
        "response_time": "8 hours"
      }
    ]
  },
  "breach_notification": {
    "contact": "breach@businessinfinity.asisaga.com",
    "sla": "72 hours to regulatory authorities, 24 hours to affected customers"
  },
  "compliance_officer": {
    "contact": "compliance@businessinfinity.asisaga.com",
    "role": "Data Protection Officer"
  }
}
```

### 5. Retention Policy API

**Endpoint**: `GET /api/onboarding/retention-policy`

**Purpose**: Provides comprehensive information about data retention and deletion policies.

**Response**:
```json
{
  "data_retention": {
    "customer_data": {
      "retention_period": "7 years",
      "rationale": "Business records retention requirement",
      "auto_deletion": false
    },
    "audit_logs": {
      "retention_period": "10 years",
      "rationale": "Compliance and audit requirements",
      "immutable": true
    },
    "temporary_data": {
      "retention_period": "90 days",
      "rationale": "Processing and backup purposes",
      "auto_deletion": true
    }
  },
  "deletion_policies": {
    "customer_request": {
      "sla": "30 days",
      "process": "Customer initiated, requires confirmation",
      "exceptions": "Legal hold, active investigations"
    },
    "automated_cleanup": {
      "temporary_files": "Daily cleanup of files older than 24 hours",
      "expired_sessions": "Hourly cleanup of expired user sessions",
      "log_rotation": "Monthly rotation of non-compliance logs"
    }
  },
  "backup_policy": {
    "frequency": "Daily incremental, weekly full backup",
    "retention": "90 days for incremental, 1 year for full backups",
    "encryption": "AES-256 encryption at rest and in transit"
  },
  "gdpr_compliance": {
    "right_to_be_forgotten": "Supported via deletion request process",
    "data_portability": "Supported via data export functionality",
    "consent_management": "Tracked in audit logs with timestamps"
  },
  "policy_version": "1.0"
}
```

## Consent Logging

The system automatically logs user consent for various onboarding activities:

### Enhanced Endpoints

1. **Quick Action Endpoint** (`/api/onboarding/quick-action`)
   - Logs consent when users choose specific agent analyses
   - Tracks service selection preferences

2. **Connect System Endpoint** (`/api/onboarding/connect-system`)
   - Logs consent for system integrations
   - Records read-only access permissions

### Consent Event Structure

All consent events are logged to the audit trail with:
- **Event Type**: `ACCESS_CONTROL`
- **Action**: `consent_given` or `consent_withdrawn`
- **Context**: Detailed consent information
- **Compliance Tags**: `gdpr`, `consent`, `privacy`

## Audit Trail Integration

All trust and compliance operations are logged to the comprehensive audit trail:

- **Data Export**: Logs export requests and completions
- **Data Deletion**: Logs deletion requests and confirmations
- **RBAC Access**: Logs permission information access
- **Consent Events**: Logs all consent decisions with timestamps

## Security Features

1. **Customer Partition Isolation**: All operations are restricted to the requesting customer's partition
2. **Integrity Protection**: Data exports include SHA-256 integrity hashes
3. **Audit Logging**: All operations are logged for compliance purposes
4. **Authentication Required**: All endpoints require proper Azure Functions authentication

## Compliance Features

- **GDPR Article 20**: Right to data portability via export functionality
- **GDPR Article 17**: Right to erasure via deletion request process
- **GDPR Article 13/14**: Transparency via RBAC and policy endpoints
- **SOX Compliance**: Comprehensive audit trail for all operations
- **Data Minimization**: Only customer-specific data is accessible

## Error Handling

All endpoints return standardized error responses:

```json
{
  "error": "Descriptive error message",
  "timestamp": "2024-12-15T14:30:00Z"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (missing parameters)
- `401`: Unauthorized
- `403`: Forbidden (cross-customer access attempt)
- `500`: Internal Server Error

## Implementation Notes

The trust and compliance features are implemented in:
- **Core Module**: `core/trust_compliance.py`
- **API Endpoints**: `function_app.py`
- **Audit Integration**: Extended `core/audit_trail.py`

All functionality is thoroughly tested and includes integrity verification for exported data.