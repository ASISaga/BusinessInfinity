"""Tests for BusinessInfinity workflows."""

import pytest

from business_infinity.workflows import (
    C_SUITE_AGENT_IDS,
    C_SUITE_TYPES,
    app,
    select_c_suite_agents,
)


class TestCSuiteSelection:
    """Test C-suite agent selection logic."""

    def test_c_suite_agent_ids(self):
        assert "ceo" in C_SUITE_AGENT_IDS
        assert "cfo" in C_SUITE_AGENT_IDS
        assert "cmo" in C_SUITE_AGENT_IDS
        assert "coo" in C_SUITE_AGENT_IDS
        assert "cto" in C_SUITE_AGENT_IDS
        assert "cso" in C_SUITE_AGENT_IDS
        assert "chro" in C_SUITE_AGENT_IDS

    def test_c_suite_types(self):
        assert "LeadershipAgent" in C_SUITE_TYPES
        assert "CMOAgent" in C_SUITE_TYPES


class TestAOSAppWorkflows:
    """Test AOSApp workflow registration."""

    def test_app_name(self):
        assert app.name == "business-infinity"

    def test_workflows_registered(self):
        names = app.get_workflow_names()
        assert "strategic-review" in names
        assert "market-analysis" in names
        assert "budget-approval" in names
        assert "risk-assessment" in names
        assert "boardroom-session" in names
        assert "covenant-compliance" in names
        assert "talent-management" in names
        assert "technology-review" in names

    def test_enterprise_workflows_registered(self):
        """Verify enterprise capability workflows from SDK v4.0.0."""
        names = app.get_workflow_names()
        assert "knowledge-search" in names
        assert "risk-register" in names
        assert "risk-assess" in names
        assert "log-decision" in names
        assert "covenant-create" in names
        assert "ask-agent" in names

    def test_v5_workflows_registered(self):
        """Verify new workflows from SDK v5.0.0."""
        names = app.get_workflow_names()
        assert "risk-heatmap" in names
        assert "risk-summary" in names
        assert "compliance-report" in names
        assert "create-alert" in names
        assert "register-webhook" in names

    def test_workflow_count(self):
        assert len(app.get_workflow_names()) == 29

    def test_all_workflow_names_are_kebab_case(self):
        for name in app.get_workflow_names():
            assert "-" in name or name.isalpha(), f"Workflow name '{name}' should be kebab-case"
            assert " " not in name, f"Workflow name '{name}' should not contain spaces"
            assert name == name.lower(), f"Workflow name '{name}' should be lowercase"


class TestAOSAppEnterpriseFeatures:
    """Test enterprise features added in v4.0.0."""

    def test_update_handler_registered(self):
        assert "strategic-review" in app.get_update_handler_names()

    def test_mcp_tool_registered(self):
        assert "erp-search" in app.get_mcp_tool_names()

    def test_observability_configured(self):
        assert app.observability is not None


class TestAOSAppV5Features:
    """Test v5.0.0 features: covenant events, MCP events, webhooks."""

    def test_covenant_event_handlers(self):
        handlers = app.get_covenant_event_handler_names()
        assert "violated" in handlers
        assert "expiring" in handlers

    def test_mcp_event_handlers(self):
        handlers = app.get_mcp_event_handler_names()
        assert "erpnext:order_created" in handlers

    def test_webhook_handlers(self):
        handlers = app.get_webhook_names()
        assert "slack-notifications" in handlers


# ── Beyond-SDK Feature Tests ─────────────────────────────────────────────────

from unittest.mock import AsyncMock, MagicMock, patch

from business_infinity.workflows import (
    RateLimiter,
    WORKFLOW_DEPENDENCIES,
    _ORCHESTRATION_GROUPS,
    _WEBHOOK_FILTERS,
    _MIDDLEWARE,
    default_rate_limiter,
    encrypt_sensitive_fields,
    decrypt_sensitive_fields,
    evaluate_webhook_filter,
    use_middleware,
)
from aos_client import WorkflowRequest


class TestRateLimiter:
    """Enhancement #2 — Rate limiting."""

    def test_default_rate_limiter_exists(self):
        assert default_rate_limiter is not None
        assert isinstance(default_rate_limiter, RateLimiter)

    def test_rate_limiter_defaults(self):
        rl = RateLimiter()
        assert rl.requests_per_minute == 100
        assert rl.burst_limit == 20

    def test_rate_limiter_custom(self):
        rl = RateLimiter(requests_per_minute=60, burst_limit=10)
        assert rl.requests_per_minute == 60
        assert rl.burst_limit == 10

    def test_get_quota_usage(self):
        rl = RateLimiter(requests_per_minute=100, burst_limit=20)
        quota = rl.get_quota_usage()
        assert "tokens_remaining" in quota
        assert "burst_limit" in quota
        assert "requests_per_minute" in quota
        assert quota["burst_limit"] == 20
        assert quota["requests_per_minute"] == 100

    async def test_acquire_reduces_tokens(self):
        rl = RateLimiter(requests_per_minute=600, burst_limit=5)
        before = rl.get_quota_usage()["tokens_remaining"]
        await rl.acquire()
        after = rl.get_quota_usage()["tokens_remaining"]
        assert after < before


class TestEncryption:
    """Enhancement #1 — Field-level encryption."""

    def test_encrypt_fields(self):
        data = {"name": "Alice", "secret": "s3cr3t", "other": "visible"}
        result = encrypt_sensitive_fields(data, fields=["secret"])
        assert result["name"] == "Alice"
        assert result["other"] == "visible"
        assert result["secret"].startswith("enc:")
        assert result["secret"] != "s3cr3t"

    def test_encrypt_does_not_mutate(self):
        data = {"key": "value"}
        result = encrypt_sensitive_fields(data, fields=["key"])
        assert data["key"] == "value"  # original untouched
        assert result["key"] != "value"  # returned value is encrypted
        assert result["key"].startswith("enc:")

    def test_decrypt_round_trip(self):
        data = {"salary": "100000", "name": "Bob"}
        encrypted = encrypt_sensitive_fields(data, fields=["salary"])
        decrypted = decrypt_sensitive_fields(encrypted, fields=["salary"])
        assert decrypted["salary"] == "100000"
        assert decrypted["name"] == "Bob"

    def test_decrypt_skips_non_enc(self):
        data = {"field": "plain_value"}
        result = decrypt_sensitive_fields(data, fields=["field"])
        assert result["field"] == "plain_value"

    def test_encrypt_missing_field_no_error(self):
        data = {"a": 1}
        result = encrypt_sensitive_fields(data, fields=["missing"])
        assert result == {"a": 1}


class TestWorkflowDependencies:
    """Enhancement #3 — Workflow dependency chains."""

    def test_compliance_report_depends_on_covenant_compliance(self):
        assert "covenant-compliance" in WORKFLOW_DEPENDENCIES["compliance-report"]

    def test_risk_summary_depends_on_risk_assess(self):
        assert "risk-assess" in WORKFLOW_DEPENDENCIES["risk-summary"]

    def test_risk_heatmap_dependencies(self):
        deps = WORKFLOW_DEPENDENCIES["risk-heatmap"]
        assert "risk-register" in deps
        assert "risk-assess" in deps

    def test_start_workflow_chain_registered(self):
        assert "start-workflow-chain" in app.get_workflow_names()


class TestOrchestrationGroups:
    """Enhancement #4 — Bulk orchestration management."""

    def test_group_workflows_registered(self):
        names = app.get_workflow_names()
        assert "start-orchestration-group" in names
        assert "get-group-status" in names
        assert "stop-orchestration-group" in names

    def test_orchestration_groups_dict_exists(self):
        assert isinstance(_ORCHESTRATION_GROUPS, dict)


class TestAgentCapabilityMatching:
    """Enhancement #5 — Agent capability matching."""

    def test_find_agents_workflow_registered(self):
        assert "find-agents" in app.get_workflow_names()


class TestCheckpointing:
    """Enhancement #6 — Orchestration checkpointing."""

    def test_checkpoint_workflows_registered(self):
        names = app.get_workflow_names()
        assert "checkpoint-orchestration" in names
        assert "resume-orchestration" in names


class TestConditionalWebhooks:
    """Enhancement #7 — Conditional webhooks with filters."""

    def test_register_conditional_webhook_registered(self):
        assert "register-conditional-webhook" in app.get_workflow_names()

    def test_webhook_filters_dict_exists(self):
        assert isinstance(_WEBHOOK_FILTERS, dict)

    def test_evaluate_filter_no_rule_passes(self):
        assert evaluate_webhook_filter("nonexistent-id", {"priority": "low"}) is True

    def test_evaluate_filter_eq_match(self):
        _WEBHOOK_FILTERS["wh-eq"] = {"field": "priority", "op": "eq", "value": "critical"}
        assert evaluate_webhook_filter("wh-eq", {"priority": "critical"}) is True
        assert evaluate_webhook_filter("wh-eq", {"priority": "low"}) is False

    def test_evaluate_filter_gt(self):
        _WEBHOOK_FILTERS["wh-gt"] = {"field": "score", "op": "gt", "value": 8.0}
        assert evaluate_webhook_filter("wh-gt", {"score": 9.0}) is True
        assert evaluate_webhook_filter("wh-gt", {"score": 7.0}) is False

    def test_evaluate_filter_contains(self):
        _WEBHOOK_FILTERS["wh-contains"] = {"field": "tags", "op": "contains", "value": "urgent"}
        assert evaluate_webhook_filter("wh-contains", {"tags": ["urgent", "review"]}) is True
        assert evaluate_webhook_filter("wh-contains", {"tags": ["routine"]}) is False

    def test_evaluate_filter_type_error_returns_false(self):
        _WEBHOOK_FILTERS["wh-bad"] = {"field": "val", "op": "gt", "value": "notanumber"}
        result = evaluate_webhook_filter("wh-bad", {"val": 5})
        assert result is False


class TestAuditIntegrity:
    """Enhancement #8 — Audit trail tamper detection."""

    def test_verify_audit_integrity_registered(self):
        assert "verify-audit-integrity" in app.get_workflow_names()


class TestMiddleware:
    """Enhancement #9 — Plugin/middleware architecture."""

    def test_middleware_list_exists(self):
        assert isinstance(_MIDDLEWARE, list)

    def test_use_middleware_appends(self):
        initial_count = len(_MIDDLEWARE)

        async def my_middleware(workflow_name, request):
            pass

        use_middleware(my_middleware)
        assert len(_MIDDLEWARE) == initial_count + 1
        _MIDDLEWARE.remove(my_middleware)  # clean up


class TestApiDocumentation:
    """Enhancement #10 — Workflow documentation generation."""

    def test_generate_api_docs_registered(self):
        assert "generate-api-docs" in app.get_workflow_names()


class TestBeyondSDKWorkflowCount:
    """Ensure all 10 beyond-SDK workflows are registered."""

    BEYOND_SDK_WORKFLOWS = [
        "find-agents",
        "start-orchestration-group",
        "get-group-status",
        "stop-orchestration-group",
        "checkpoint-orchestration",
        "resume-orchestration",
        "register-conditional-webhook",
        "verify-audit-integrity",
        "start-workflow-chain",
        "generate-api-docs",
    ]

    def test_all_beyond_sdk_workflows_registered(self):
        names = app.get_workflow_names()
        for workflow in self.BEYOND_SDK_WORKFLOWS:
            assert workflow in names, f"Missing beyond-SDK workflow: {workflow}"

    def test_beyond_sdk_workflow_count(self):
        names = app.get_workflow_names()
        registered = [w for w in self.BEYOND_SDK_WORKFLOWS if w in names]
        assert len(registered) == 10
