"""
BusinessInfinity Configuration

This module provides the canonical BusinessInfinity-specific configuration
that extends the generic runtime configuration.

All application-specific settings are consolidated here.
"""

import os
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime import RuntimeConfig, load_runtime_config


@dataclass
class BusinessInfinityConfig:
    """
    BusinessInfinity-specific configuration.

    This extends RuntimeConfig with business-specific settings like:
    - C-Suite agent configurations
    - Business workflows and analytics
    - Covenant and compliance settings
    - LinkedIn integration settings
    """

    # Company Identity
    company_name: str = "Business Infinity"
    company_domain: str = "businessinfinity.com"
    business_model: str = "enterprise_saas"
    industry: str = "technology"

    # C-Suite Agents Configuration
    enabled_agents: List[str] = field(
        default_factory=lambda: ["ceo", "cfo", "cto", "cmo", "cso", "coo", "chro"]
    )

    # Boardroom Configuration
    boardroom_enabled: bool = True
    autonomous_boardroom: bool = True

    # Covenant and Compliance
    covenant_enabled: bool = True
    linkedin_verification_enabled: bool = True

    # Business Workflows
    workflows_enabled: bool = True
    strategic_planning_interval: int = 3600  # seconds
    performance_monitoring_interval: int = 300  # seconds

    # Business Analytics
    analytics_enabled: bool = True
    kpi_tracking_enabled: bool = True

    # MCP Integration
    mcp_servers: List[str] = field(
        default_factory=lambda: ["linkedin-mcp-server", "ERPNext-MCP", "mcp-reddit"]
    )

    # Feature Flags
    mentor_mode_enabled: bool = True
    onboarding_enabled: bool = True
    network_discovery_enabled: bool = True

    # Runtime Configuration (generic)
    runtime_config: RuntimeConfig = field(default_factory=RuntimeConfig)

    @classmethod
    def from_env(cls) -> "BusinessInfinityConfig":
        """Load BusinessInfinity configuration from environment variables."""
        return cls(
            company_name=os.getenv("COMPANY_NAME", "Business Infinity"),
            company_domain=os.getenv("COMPANY_DOMAIN", "businessinfinity.com"),
            business_model=os.getenv("BUSINESS_MODEL", "enterprise_saas"),
            industry=os.getenv("INDUSTRY", "technology"),
            boardroom_enabled=os.getenv("BOARDROOM_ENABLED", "true").lower() == "true",
            autonomous_boardroom=os.getenv("AUTONOMOUS_BOARDROOM", "true").lower()
            == "true",
            covenant_enabled=os.getenv("COVENANT_ENABLED", "true").lower() == "true",
            linkedin_verification_enabled=os.getenv(
                "LINKEDIN_VERIFICATION_ENABLED", "true"
            ).lower()
            == "true",
            workflows_enabled=os.getenv("WORKFLOWS_ENABLED", "true").lower() == "true",
            analytics_enabled=os.getenv("ANALYTICS_ENABLED", "true").lower() == "true",
            mentor_mode_enabled=os.getenv("MENTOR_MODE_ENABLED", "true").lower()
            == "true",
            onboarding_enabled=os.getenv("ONBOARDING_ENABLED", "true").lower()
            == "true",
            network_discovery_enabled=os.getenv(
                "NETWORK_DISCOVERY_ENABLED", "true"
            ).lower()
            == "true",
            runtime_config=RuntimeConfig.from_env(),
        )

    @classmethod
    def from_json(cls, config_path: str) -> "BusinessInfinityConfig":
        """Load BusinessInfinity configuration from JSON file."""
        with open(config_path, "r") as f:
            config_data = json.load(f)

        # Extract runtime config if present
        runtime_config_data = config_data.pop("runtime_config", {})
        runtime_config = (
            RuntimeConfig.from_dict(runtime_config_data)
            if runtime_config_data
            else RuntimeConfig()
        )

        # Create BI config
        bi_config = cls(
            **{k: v for k, v in config_data.items() if k in cls.__dataclass_fields__}
        )
        bi_config.runtime_config = runtime_config

        return bi_config

    def to_runtime_config(self) -> RuntimeConfig:
        """
        Convert BusinessInfinity config to RuntimeConfig.

        This merges BI-specific settings into the runtime config's custom_config.
        """
        return RuntimeConfig(
            app_name="BusinessInfinity",
            app_version="2.0.0",
            app_environment=self.runtime_config.app_environment,
            azure_functions_enabled=self.runtime_config.azure_functions_enabled,
            auth_level=self.runtime_config.auth_level,
            agent_framework_enabled=self.runtime_config.agent_framework_enabled,
            aos_enabled=self.runtime_config.aos_enabled,
            storage_type=self.runtime_config.storage_type,
            messaging_type=self.runtime_config.messaging_type,
            observability_enabled=self.runtime_config.observability_enabled,
            log_level=self.runtime_config.log_level,
            circuit_breaker_enabled=self.runtime_config.circuit_breaker_enabled,
            retry_enabled=self.runtime_config.retry_enabled,
            max_retries=self.runtime_config.max_retries,
            custom_config={
                # BusinessInfinity-specific settings
                "company_name": self.company_name,
                "company_domain": self.company_domain,
                "business_model": self.business_model,
                "industry": self.industry,
                "enabled_agents": self.enabled_agents,
                "boardroom_enabled": self.boardroom_enabled,
                "autonomous_boardroom": self.autonomous_boardroom,
                "covenant_enabled": self.covenant_enabled,
                "linkedin_verification_enabled": self.linkedin_verification_enabled,
                "workflows_enabled": self.workflows_enabled,
                "strategic_planning_interval": self.strategic_planning_interval,
                "performance_monitoring_interval": self.performance_monitoring_interval,
                "analytics_enabled": self.analytics_enabled,
                "kpi_tracking_enabled": self.kpi_tracking_enabled,
                "mcp_servers": self.mcp_servers,
                "mentor_mode_enabled": self.mentor_mode_enabled,
                "onboarding_enabled": self.onboarding_enabled,
                "network_discovery_enabled": self.network_discovery_enabled,
            },
        )


def load_bi_config(
    config_path: Optional[str] = None, use_env: bool = True
) -> BusinessInfinityConfig:
    """
    Load BusinessInfinity configuration from various sources.

    Priority order:
    1. config_path (if provided)
    2. Environment variables (if use_env=True)
    3. Default configuration

    Args:
        config_path: Path to JSON configuration file
        use_env: Whether to use environment variables

    Returns:
        BusinessInfinityConfig instance
    """
    # Try loading from default config paths
    default_paths = [
        Path("config/businessinfinity.json"),
        Path("config/businessInfinity.json"),
        Path("local.settings.json"),
    ]

    if config_path:
        return BusinessInfinityConfig.from_json(config_path)

    for path in default_paths:
        if path.exists():
            try:
                return BusinessInfinityConfig.from_json(str(path))
            except Exception:
                continue

    if use_env:
        return BusinessInfinityConfig.from_env()

    return BusinessInfinityConfig()


# Convenience factory functions
def create_default_config() -> BusinessInfinityConfig:
    """Create a default BusinessInfinity configuration."""
    return BusinessInfinityConfig()


def create_production_config() -> BusinessInfinityConfig:
    """Create a production BusinessInfinity configuration."""
    config = BusinessInfinityConfig.from_env()
    config.runtime_config.app_environment = "production"
    config.runtime_config.log_level = "WARNING"
    return config


def create_development_config() -> BusinessInfinityConfig:
    """Create a development BusinessInfinity configuration."""
    config = BusinessInfinityConfig()
    config.runtime_config.app_environment = "development"
    config.runtime_config.log_level = "DEBUG"
    return config
