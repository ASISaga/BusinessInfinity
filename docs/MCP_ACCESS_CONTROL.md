# MCP Access Control System

This document describes the configurable, role-based MCP access control system implemented for BusinessInfinity.

## Overview

The MCP Access Control System provides comprehensive role-based access control for all MCP servers in the BusinessInfinity ecosystem, with progressive onboarding capabilities and comprehensive audit logging.

## Key Features

### 1. Role-Based Access Control
- **Granular Permissions**: Each role has specific access levels for each MCP server
- **Access Levels**: none, read_only, limited_write, full_write, admin
- **Override Capabilities**: Privileged roles can override restrictions

### 2. Progressive Onboarding
- **Observer Stage (7 days)**: Read-only access, 10 queries/hour
- **Participant Stage (30 days)**: Limited write access, 50 queries/hour  
- **Trusted Stage (Permanent)**: Full access, 200 queries/hour

### 3. Rate Limiting and Restrictions
- **Hourly Limits**: Configurable per role and onboarding stage
- **Operation Restrictions**: Specific operations can be restricted per stage
- **Automatic Cleanup**: Old usage statistics are automatically cleaned up

### 4. Audit and Compliance
- **Violation Logging**: All access denials are logged with details
- **Access Tracking**: All successful accesses can be logged
- **Retention Policies**: Configurable log retention periods

## Architecture

### Core Components

1. **MCPAccessControlManager** (`core/mcp_access_control.py`)
   - Main access control engine
   - Handles permission validation
   - Manages progressive onboarding
   - Tracks usage and violations

2. **Configuration** (`config/mcp_access_control.json`)
   - Role definitions and permissions
   - Progressive onboarding stages
   - MCP server configurations
   - System settings

3. **Integration** (`core/utils.py`)
   - Integration with existing utils system
   - Backward compatibility functions
   - Exception handling

4. **Dashboard** (`dashboard/mcp_access_control.html`)
   - Web-based administration interface
   - Role permission management
   - Violation monitoring
   - Configuration management

### MCP Server Integration

The system integrates with existing MCP handlers (`dashboard/mcp_handlers.py`) to enforce access control at the protocol level:

```python
# Access control is enforced before operation execution
try:
    validate_mcp_request(user_id, user_role, mcp_server, operation)
except MCPAccessDeniedError as e:
    return access_denied_response(e)
```

## Configuration

### Role Configuration Example

```json
{
  "Founder": {
    "default_stage": "trusted",
    "mcp_access": {
      "linkedin": "admin",
      "reddit": "full_write",
      "erpnext": "admin",
      "businessinfinity_config": "admin"
    },
    "override_restrictions": true
  },
  "Employee": {
    "default_stage": "observer", 
    "mcp_access": {
      "linkedin": "none",
      "reddit": "none",
      "erpnext": "read_only",
      "businessinfinity_config": "none"
    },
    "progressive_onboarding": true
  }
}
```

### MCP Server Configuration

```json
{
  "linkedin": {
    "name": "LinkedIn MCP Server",
    "security_level": "high",
    "data_sensitivity": "personal",
    "operations": {
      "read": ["get_profile", "list_connections"],
      "create": ["post_content", "send_message"],
      "admin": ["manage_company_page", "access_analytics"]
    }
  }
}
```

## Usage

### Basic Access Control

```python
from core.utils import check_mcp_access, validate_mcp_request

# Check if user has access
has_access, reason = check_mcp_access("user123", "Employee", "linkedin", "read")

# Validate and raise exception if denied
validate_mcp_request("user123", "Employee", "erpnext", "create")
```

### User Management

```python
from core.utils import utils_manager

# Get user permissions summary
permissions = utils_manager.get_user_mcp_permissions("user123", "Employee")

# Update user access
utils_manager.update_user_mcp_access("user123", "linkedin", "read_only")

# Bulk update role permissions
utils_manager.bulk_update_role_mcp_access("Employee", {
    "linkedin": "read_only",
    "reddit": "read_only"
})
```

### Monitoring and Auditing

```python
# Get recent violations
violations = utils_manager.get_mcp_access_violations(24)  # Last 24 hours

# Check violation details
for violation in violations:
    print(f"{violation['user_role']} -> {violation['mcp_server']}.{violation['operation']}")
    print(f"Reason: {violation['reason']}")
```

## Progressive Onboarding Workflow

1. **New User Registration**
   - User starts in "observer" stage
   - Limited to read-only operations
   - Low rate limits apply

2. **Automatic Progression**
   - System checks onboarding progress daily
   - Users advance based on time in stage
   - Restrictions gradually lifted

3. **Manual Override**
   - Administrators can manually advance users
   - Emergency access can be granted
   - Audit trails maintained

## Security Features

### Access Validation
- All MCP operations are validated before execution
- Multiple validation layers (role, stage, operation, rate limiting)
- Fail-secure by default (deny unknown operations)

### Audit Logging
- Comprehensive logging of all access attempts
- Structured violation records with context
- Configurable retention and alerting

### Rate Limiting
- Per-user, per-hour operation limits
- Automatic cleanup of old usage data
- Bypass capability for privileged roles

## Future Development

### BusinessInfinity Configuration MCP Server

A dedicated MCP server should be implemented in a separate repository to provide:

- Real-time permission updates across services
- Centralized user and role management
- Advanced audit log analysis
- Integration with external identity providers
- API endpoints for programmatic management

**Repository Structure:**
```
businessinfinity-config-mcp/
├── server/           # MCP server implementation
├── api/             # REST API endpoints
├── web/             # Administrative web interface
├── database/        # Database schemas
├── tests/           # Test suite
└── docs/            # Documentation
```

**Key Features to Implement:**
- PostgreSQL backend for scalability
- Redis for real-time updates
- REST API for integration
- React-based admin interface
- Docker deployment
- Comprehensive monitoring

## Testing

The system includes comprehensive tests covering:

- Role-based access validation
- Progressive onboarding workflows
- Rate limiting functionality
- Violation logging
- Configuration management
- Integration with existing systems

Run tests with:
```bash
python test_mcp_access.py
```

## Administration Dashboard

The web-based dashboard (`/dashboard/mcp_access_control.html`) provides:

- **Role Management**: Configure permissions for each role
- **User Monitoring**: View individual user permissions and status
- **Violation Tracking**: Monitor and investigate access violations
- **System Configuration**: Update global settings and policies

Access the dashboard at: `http://localhost:8080/dashboard/mcp_access_control.html`

## Compliance and Governance

The system supports compliance requirements through:

- **Audit Trails**: Complete record of all access decisions
- **Data Retention**: Configurable retention policies
- **Violation Alerting**: Real-time alerts for security violations
- **Policy Enforcement**: Automated enforcement of access policies
- **Regular Reviews**: Built-in support for access reviews

## Error Handling

The system provides clear error messages and appropriate HTTP status codes:

- **403 Forbidden**: Access denied due to insufficient permissions
- **429 Too Many Requests**: Rate limit exceeded
- **400 Bad Request**: Invalid operation or parameters
- **500 Internal Server Error**: System configuration errors

All errors include detailed context for troubleshooting and audit purposes.