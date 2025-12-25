# API Specification

**Document ID**: SPEC-BI-02  
**Version**: 1.0.0  
**Last Updated**: 2025-12-25  
**Status**: Active

## 1. Introduction

### 1.1 Purpose

This specification defines the HTTP API surface of BusinessInfinity, including endpoints, request/response formats, error handling, and authentication requirements.

### 1.2 Base URL

- **Local Development**: `http://localhost:7071/api`
- **Staging**: `https://businessinfinity-staging.azurewebsites.net/api`
- **Production**: `https://businessinfinity.azurewebsites.net/api`

### 1.3 API Version

Current API Version: v1 (implied in all endpoints)

## 2. Authentication

### 2.1 Authentication Levels

**SEC-API-001**: The system SHALL support the following authentication levels:

- `ANONYMOUS`: No authentication required (health checks only)
- `FUNCTION`: Function key required
- `ADMIN`: Admin key required

### 2.2 Authentication Methods

**SEC-API-002**: The system SHALL support authentication via:

- Function keys (x-functions-key header)
- Azure B2C tokens (Authorization: Bearer header)
- LinkedIn OAuth tokens (for network features)

### 2.3 API Keys

**SEC-API-003**: Function keys SHALL be passed in the request header:

```http
x-functions-key: <function-key>
```

## 3. Core Endpoints

### 3.1 Health & Status

#### 3.1.1 Health Check

**REQ-API-001**: The system SHALL expose a health check endpoint.

```
GET /health
```

**Authentication**: Anonymous

**Response** (200 OK):
```json
{
  "status": "ok" | "degraded" | "unhealthy",
  "timestamp": "2025-12-25T00:00:00Z",
  "components": {
    "aos": {
      "status": "ok" | "degraded" | "unavailable",
      "message": "AOS operational"
    },
    "serviceBus": {
      "status": "ok" | "degraded" | "unavailable",
      "message": "Service Bus connected"
    },
    "storage": {
      "status": "ok" | "degraded" | "unavailable",
      "message": "Storage accessible"
    },
    "mcp": {
      "status": "ok" | "degraded" | "unavailable",
      "message": "MCP servers available"
    },
    "agents": {
      "status": "ok" | "degraded" | "unavailable",
      "active_count": 8,
      "message": "8 agents operational"
    }
  }
}
```

**Response Codes**:
- 200: System healthy or degraded
- 503: System unhealthy

#### 3.1.2 System Status

**REQ-API-002**: The system SHALL expose a detailed system status endpoint.

```
GET /status
```

**Authentication**: Function key required

**Response** (200 OK):
```json
{
  "version": "2.0.0",
  "uptime_seconds": 86400,
  "agents": {
    "total": 8,
    "active": 8,
    "idle": 0
  },
  "workflows": {
    "active": 3,
    "pending": 1,
    "completed_24h": 15
  },
  "decisions": {
    "pending": 2,
    "completed_24h": 42
  },
  "performance": {
    "avg_response_time_ms": 150,
    "error_rate_percent": 0.05
  }
}
```

### 3.2 Agent Endpoints

#### 3.2.1 List Agents

**REQ-API-003**: The system SHALL provide an endpoint to list all available agents.

```
GET /agents
```

**Authentication**: Function key required

**Response** (200 OK):
```json
{
  "agents": [
    {
      "role": "CEO",
      "name": "Chief Executive Officer",
      "status": "active" | "idle" | "busy",
      "capabilities": [
        "strategic_planning",
        "decision_making",
        "leadership"
      ],
      "current_load": 0.3,
      "metadata": {
        "version": "1.0.0",
        "last_active": "2025-12-25T00:00:00Z"
      }
    }
  ],
  "total": 8
}
```

#### 3.2.2 Get Agent Details

**REQ-API-004**: The system SHALL provide an endpoint to get agent details.

```
GET /agents/{agent_id}
```

**Path Parameters**:
- `agent_id`: Agent identifier (e.g., "CEO", "CFO", "CTO")

**Authentication**: Function key required

**Response** (200 OK):
```json
{
  "agent_id": "CEO",
  "role": "CEO",
  "name": "Chief Executive Officer",
  "status": "active",
  "capabilities": [
    "strategic_planning",
    "decision_making",
    "leadership",
    "vision_setting"
  ],
  "expertise_areas": [
    "business_strategy",
    "organizational_leadership",
    "stakeholder_management"
  ],
  "performance_metrics": {
    "decisions_made": 142,
    "avg_confidence": 0.85,
    "response_time_ms": 120
  },
  "current_tasks": [
    {
      "task_id": "task_123",
      "type": "strategic_decision",
      "status": "in_progress"
    }
  ]
}
```

**Response Codes**:
- 200: Agent found
- 404: Agent not found

#### 3.2.3 Ask Agent

**REQ-API-005**: The system SHALL provide an endpoint to query an agent.

```
POST /agents/{agent_role}/ask
```

**Path Parameters**:
- `agent_role`: Agent role (e.g., "CEO", "CFO")

**Authentication**: Function key required

**Request Body**:
```json
{
  "message": "What are our top strategic priorities for Q1 2025?",
  "context": {
    "business_unit": "global",
    "timeframe": "Q1 2025",
    "priority_level": "high"
  }
}
```

**Response** (200 OK):
```json
{
  "answer": "Based on our current market position and business objectives...",
  "confidence": 0.87,
  "metadata": {
    "agent": "CEO",
    "timestamp": "2025-12-25T00:00:00Z",
    "processing_time_ms": 1200,
    "reasoning": "Analysis based on business strategy framework..."
  },
  "recommendations": [
    {
      "priority": 1,
      "recommendation": "Expand into emerging markets",
      "rationale": "High growth potential with minimal risk"
    }
  ]
}
```

**Response Codes**:
- 200: Successful response
- 400: Invalid request
- 404: Agent not found
- 408: Request timeout
- 503: Agent unavailable

### 3.3 Decision Endpoints

#### 3.3.1 Make Strategic Decision

**REQ-API-006**: The system SHALL provide an endpoint to initiate strategic decisions.

```
POST /decisions
```

**Authentication**: Function key required

**Request Body**:
```json
{
  "type": "strategic" | "financial" | "technical" | "operational",
  "title": "Q1 2025 Market Expansion",
  "context": "We have opportunity to enter 3 new markets",
  "stakeholders": ["CEO", "CFO", "CMO"],
  "params": {
    "budget_limit": 1000000,
    "timeline": "Q1 2025",
    "risk_tolerance": "medium"
  },
  "mode": "consensus" | "delegation" | "voting"
}
```

**Response** (202 Accepted):
```json
{
  "decision_id": "dec_a1b2c3d4",
  "status": "queued" | "in_progress",
  "expected_completion_time": "2025-12-25T00:05:00Z",
  "tracking_url": "/decisions/dec_a1b2c3d4"
}
```

**Response Codes**:
- 202: Decision queued
- 400: Invalid request
- 503: Service unavailable

#### 3.3.2 Get Decision Status

**REQ-API-007**: The system SHALL provide an endpoint to check decision status.

```
GET /decisions/{decision_id}
```

**Path Parameters**:
- `decision_id`: Decision identifier

**Authentication**: Function key required

**Response** (200 OK):
```json
{
  "decision_id": "dec_a1b2c3d4",
  "type": "strategic",
  "title": "Q1 2025 Market Expansion",
  "status": "completed" | "in_progress" | "failed",
  "created_at": "2025-12-25T00:00:00Z",
  "completed_at": "2025-12-25T00:04:32Z",
  "created_by": "user_123",
  "inputs": { /* original request */ },
  "agent_votes": [
    {
      "agent": "CEO",
      "vote": "approve",
      "confidence": 0.9,
      "reasoning": "Strong strategic alignment...",
      "timestamp": "2025-12-25T00:02:00Z"
    },
    {
      "agent": "CFO",
      "vote": "approve_with_conditions",
      "confidence": 0.75,
      "reasoning": "Financially viable with budget controls...",
      "conditions": ["Monthly budget review", "ROI tracking"],
      "timestamp": "2025-12-25T00:03:00Z"
    }
  ],
  "outcome": {
    "decision": "approved",
    "confidence": 0.85,
    "action_items": [
      "Prepare market entry strategy",
      "Allocate budget",
      "Establish KPIs"
    ],
    "next_steps": "Execute market analysis phase"
  },
  "provenance": {
    "mcp_analysis": { /* MCP data */ },
    "spec_version": "1.0"
  }
}
```

#### 3.3.3 List Decisions

**REQ-API-008**: The system SHALL provide an endpoint to list decisions.

```
GET /decisions?status={status}&type={type}&limit={limit}
```

**Query Parameters**:
- `status`: Filter by status (optional)
- `type`: Filter by decision type (optional)
- `limit`: Maximum results (default: 20, max: 100)
- `offset`: Pagination offset (default: 0)

**Authentication**: Function key required

**Response** (200 OK):
```json
{
  "decisions": [ /* array of decision summaries */ ],
  "total": 142,
  "limit": 20,
  "offset": 0,
  "has_more": true
}
```

### 3.4 Workflow Endpoints

#### 3.4.1 Execute Workflow

**REQ-API-009**: The system SHALL provide an endpoint to execute workflows.

```
POST /workflows/{workflow_name}
```

**Path Parameters**:
- `workflow_name`: Name of workflow (e.g., "product_launch", "funding_round")

**Authentication**: Function key required

**Request Body**:
```json
{
  "params": {
    "product_name": "AI Analytics Platform",
    "target_date": "2025-06-01",
    "market_segment": "enterprise"
  }
}
```

**Response** (202 Accepted):
```json
{
  "execution_id": "wf_exec_xyz789",
  "workflow_name": "product_launch",
  "status": "queued",
  "tracking_url": "/workflows/executions/wf_exec_xyz789"
}
```

#### 3.4.2 Get Workflow Execution Status

**REQ-API-010**: The system SHALL provide an endpoint to check workflow status.

```
GET /workflows/executions/{execution_id}
```

**Path Parameters**:
- `execution_id`: Workflow execution identifier

**Authentication**: Function key required

**Response** (200 OK):
```json
{
  "execution_id": "wf_exec_xyz789",
  "workflow_name": "product_launch",
  "status": "in_progress" | "completed" | "failed",
  "started_at": "2025-12-25T00:00:00Z",
  "current_step": 3,
  "total_steps": 6,
  "steps": [
    {
      "step": 1,
      "name": "Market Analysis",
      "status": "completed",
      "agent": "CMO",
      "completed_at": "2025-12-25T00:10:00Z",
      "output": { /* step output */ }
    },
    {
      "step": 2,
      "name": "Product Strategy",
      "status": "completed",
      "agent": "CEO",
      "completed_at": "2025-12-25T00:15:00Z"
    },
    {
      "step": 3,
      "name": "Technical Planning",
      "status": "in_progress",
      "agent": "CTO",
      "started_at": "2025-12-25T00:15:30Z"
    }
  ]
}
```

### 3.5 Analytics Endpoints

#### 3.5.1 Get Business Metrics

**REQ-API-011**: The system SHALL provide an endpoint to retrieve business metrics.

```
GET /analytics/metrics?type={type}&period={period}
```

**Query Parameters**:
- `type`: Metric type (financial, operational, customer, etc.)
- `period`: Time period (day, week, month, quarter, year)

**Authentication**: Function key required

**Response** (200 OK):
```json
{
  "period": "month",
  "metrics": [
    {
      "metric_id": "revenue_growth",
      "name": "Revenue Growth Rate",
      "type": "financial",
      "current_value": 15.2,
      "unit": "percentage",
      "target_value": 12.0,
      "trend": "increasing",
      "last_updated": "2025-12-25T00:00:00Z"
    }
  ]
}
```

#### 3.5.2 Get Agent Performance

**REQ-API-012**: The system SHALL provide an endpoint to retrieve agent performance metrics.

```
GET /analytics/agents/{agent_id}/performance
```

**Path Parameters**:
- `agent_id`: Agent identifier

**Authentication**: Function key required

**Response** (200 OK):
```json
{
  "agent_id": "CEO",
  "period": "30days",
  "metrics": {
    "decisions_made": 87,
    "avg_confidence": 0.84,
    "avg_response_time_ms": 1250,
    "success_rate": 0.92
  },
  "trend": "improving"
}
```

### 3.6 Network Endpoints

#### 3.6.1 Get Covenant Status

**REQ-API-013**: The system SHALL provide an endpoint to retrieve covenant status.

```
GET /network/covenant
```

**Authentication**: Function key required

**Response** (200 OK):
```json
{
  "covenant_id": "cov_123abc",
  "status": "recognized" | "pending" | "draft",
  "schema_version": "1.0.0",
  "compliance_level": "gold",
  "verified": true,
  "peer_recognitions": 12,
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### 3.6.2 Discover Peers

**REQ-API-014**: The system SHALL provide an endpoint to discover network peers.

```
GET /network/peers?industry={industry}&location={location}
```

**Query Parameters**:
- `industry`: Filter by industry (optional)
- `location`: Filter by location (optional)
- `capabilities`: Filter by capabilities (optional)

**Authentication**: Function key required

**Response** (200 OK):
```json
{
  "peers": [
    {
      "boardroom_id": "br_xyz789",
      "company_name": "Acme Corporation",
      "industry": "technology",
      "compliance_level": "gold",
      "verified": true,
      "capabilities": ["strategic_planning", "financial_analysis"]
    }
  ],
  "total": 45
}
```

## 4. Error Handling

### 4.1 Error Response Format

**REQ-API-015**: All error responses SHALL follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    },
    "timestamp": "2025-12-25T00:00:00Z",
    "request_id": "req_abc123"
  }
}
```

### 4.2 Common Error Codes

| HTTP Code | Error Code | Description |
|-----------|------------|-------------|
| 400 | BAD_REQUEST | Invalid request parameters |
| 401 | UNAUTHORIZED | Authentication required |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 408 | REQUEST_TIMEOUT | Request processing timeout |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests |
| 500 | INTERNAL_ERROR | Internal server error |
| 503 | SERVICE_UNAVAILABLE | Service temporarily unavailable |

### 4.3 Rate Limiting

**REQ-API-016**: The system SHALL implement rate limiting:

- 100 requests per minute per API key (standard)
- 1000 requests per minute per API key (premium)

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640400000
```

## 5. Request/Response Headers

### 5.1 Standard Request Headers

**REQ-API-017**: Clients SHOULD include the following headers:

```http
Content-Type: application/json
Accept: application/json
x-functions-key: <api-key>
User-Agent: <client-identifier>
```

### 5.2 Standard Response Headers

**REQ-API-018**: Responses SHALL include:

```http
Content-Type: application/json
X-Request-ID: <unique-request-id>
X-Response-Time-Ms: <processing-time>
```

## 6. Pagination

**REQ-API-019**: List endpoints SHALL support pagination using:

- `limit`: Maximum number of results (default: 20, max: 100)
- `offset`: Number of results to skip (default: 0)

Response includes:
```json
{
  "data": [ /* results */ ],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 142,
    "has_more": true
  }
}
```

## 7. Versioning

**REQ-API-020**: API versioning SHALL be handled through URL path:

- Current: `/api/...` (v1 implied)
- Future: `/api/v2/...`

## 8. Related Specifications

- [01-SYSTEM-OVERVIEW.md](01-SYSTEM-OVERVIEW.md): System architecture
- [03-AGENT-SPECIFICATION.md](03-AGENT-SPECIFICATION.md): Agent behaviors
- [07-SECURITY-AUTH-SPECIFICATION.md](07-SECURITY-AUTH-SPECIFICATION.md): Security details

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-25 | AI System | Initial specification |
