"""
Business Infinity Configuration Management

REFACTORED: Now imports from runtime with fallback to AOS

This module provides configuration management for Business Infinity application,
integrating with runtime configuration system while adding business-specific
configuration options.

Note: The canonical configuration is in src/bi_config.py which extends runtime.RuntimeConfig.
This module provides backward compatibility and additional AOS-specific configuration.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

# Try to import from runtime first
try:
    from runtime import RuntimeConfig
    RUNTIME_AVAILABLE = True
except ImportError:
    RUNTIME_AVAILABLE = False
    RuntimeConfig = None

# Fallback to AOS
try:
    from AgentOperatingSystem.config import AOSConfig
    AOS_AVAILABLE = True
except ImportError:
    AOS_AVAILABLE = False
    AOSConfig = None


@dataclass
class BusinessInfinityConfig:
    """
    Configuration for Business Infinity application.
    
    Extends AOS configuration with business-specific settings
    for C-Suite agents, business workflows, analytics, and
    covenant management.
    """
    
    # Business Identity
    company_name: str = "Business Infinity"
    company_domain: str = "businessinfinity.com"
    business_model: str = "enterprise_saas"
    industry: str = "technology"
    
    # Business Operations
    enable_autonomous_boardroom: bool = True
    enable_strategic_planning: bool = True
    enable_performance_monitoring: bool = True
    enable_covenant_management: bool = True
    
    # C-Suite Configuration
    ceo_enabled: bool = True
    cfo_enabled: bool = True
    cto_enabled: bool = True
    cmo_enabled: bool = True
    coo_enabled: bool = True
    chro_enabled: bool = True
    founder_enabled: bool = True
    
    # Business Analytics
    kpi_collection_enabled: bool = True
    performance_metrics_enabled: bool = True
    business_intelligence_enabled: bool = True
    
    # Workflow Configuration
    strategic_decision_threshold: float = 0.7
    consensus_requirement: bool = True
    escalation_enabled: bool = True
    
    # Integration Settings
    linkedin_integration_enabled: bool = False
    azure_integration_enabled: bool = True
    mcp_integration_enabled: bool = True
    
    # AOS Configuration Components
    agent_config: Dict[str, Any] = field(default_factory=lambda: {
        "max_agents": 50,
        "agent_timeout": 300,
        "health_check_interval": 60
    })
    
    messaging_config: Dict[str, Any] = field(default_factory=lambda: {
        "queue_size": 10000,
        "message_timeout": 30,
        "priority_enabled": True,
        "routing_enabled": True
    })
    
    storage_config: Dict[str, Any] = field(default_factory=lambda: {
        "backend": "file",  # file, azure, s3
        "base_path": "./data/business_infinity",
        "encryption_enabled": False,
        "backup_enabled": True
    })
    
    monitoring_config: Dict[str, Any] = field(default_factory=lambda: {
        "metrics_enabled": True,
        "logging_level": "INFO",
        "telemetry_enabled": True,
        "health_checks_enabled": True
    })
    
    ml_config: Dict[str, Any] = field(default_factory=lambda: {
        "model_path": "./models",
        "training_enabled": False,
        "inference_enabled": True,
        "lora_enabled": False
    })
    
    auth_config: Dict[str, Any] = field(default_factory=lambda: {
        "provider": "jwt",  # jwt, azure_b2c, oauth
        "session_timeout": 3600,
        "multi_factor_enabled": False
    })
    
    environment_config: Dict[str, Any] = field(default_factory=lambda: {
        "environment": "development",  # development, staging, production
        "debug_enabled": True,
        "config_validation": True
    })
    
    mcp_config: Dict[str, Any] = field(default_factory=lambda: {
        "servers_enabled": True,
        "auto_discovery": True,
        "connection_timeout": 30,
        "retry_attempts": 3
    })
    
    # Business-specific configuration
    covenant_config: Dict[str, Any] = field(default_factory=lambda: {
        "auto_publish": False,
        "peer_discovery_enabled": True,
        "compliance_monitoring": True,
        "amendment_voting_enabled": True
    })
    
    analytics_config: Dict[str, Any] = field(default_factory=lambda: {
        "collection_interval": 300,  # 5 minutes
        "retention_days": 90,
        "aggregation_enabled": True,
        "real_time_enabled": True
    })
    
    workflow_config: Dict[str, Any] = field(default_factory=lambda: {
        "parallel_execution": True,
        "timeout_seconds": 3600,  # 1 hour
        "retry_attempts": 3,
        "state_persistence": True
    })
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Load from environment variables if available
        self._load_from_environment()
        
        # Validate configuration
        self._validate_config()
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # Business Identity
        self.company_name = os.getenv("BI_COMPANY_NAME", self.company_name)
        self.company_domain = os.getenv("BI_COMPANY_DOMAIN", self.company_domain)
        self.business_model = os.getenv("BI_BUSINESS_MODEL", self.business_model)
        self.industry = os.getenv("BI_INDUSTRY", self.industry)
        
        # Feature toggles
        self.enable_autonomous_boardroom = os.getenv("BI_AUTONOMOUS_BOARDROOM", "true").lower() == "true"
        self.enable_strategic_planning = os.getenv("BI_STRATEGIC_PLANNING", "true").lower() == "true"
        self.enable_performance_monitoring = os.getenv("BI_PERFORMANCE_MONITORING", "true").lower() == "true"
        self.enable_covenant_management = os.getenv("BI_COVENANT_MANAGEMENT", "true").lower() == "true"
        
        # Integration settings
        self.linkedin_integration_enabled = os.getenv("BI_LINKEDIN_ENABLED", "false").lower() == "true"
        self.azure_integration_enabled = os.getenv("BI_AZURE_ENABLED", "true").lower() == "true"
        self.mcp_integration_enabled = os.getenv("BI_MCP_ENABLED", "true").lower() == "true"
        
        # Update nested configs from environment
        if os.getenv("STORAGE_BACKEND"):
            self.storage_config["backend"] = os.getenv("STORAGE_BACKEND")
        if os.getenv("STORAGE_BASE_PATH"):
            self.storage_config["base_path"] = os.getenv("STORAGE_BASE_PATH")
        
        if os.getenv("LOGGING_LEVEL"):
            self.monitoring_config["logging_level"] = os.getenv("LOGGING_LEVEL")
        
        if os.getenv("ENVIRONMENT"):
            self.environment_config["environment"] = os.getenv("ENVIRONMENT")
    
    def _validate_config(self):
        """Validate configuration values."""
        # Validate thresholds
        if not 0 <= self.strategic_decision_threshold <= 1:
            raise ValueError("strategic_decision_threshold must be between 0 and 1")
        
        # Validate environment
        valid_environments = ["development", "staging", "production"]
        if self.environment_config["environment"] not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        
        # Validate storage backend
        valid_backends = ["file", "azure", "s3"]
        if self.storage_config["backend"] not in valid_backends:
            raise ValueError(f"Storage backend must be one of: {valid_backends}")
        
        # Validate auth provider
        valid_providers = ["jwt", "azure_b2c", "oauth"]
        if self.auth_config["provider"] not in valid_providers:
            raise ValueError(f"Auth provider must be one of: {valid_providers}")
    
    def to_aos_config(self) -> Any:
        """Convert to AOS configuration object."""
        if not AOS_AVAILABLE:
            raise RuntimeError("AgentOperatingSystem is not available")
        return AOSConfig(
            agent_config=self.agent_config,
            messaging_config=self.messaging_config,
            storage_config=self.storage_config,
            monitoring_config=self.monitoring_config,
            ml_config=self.ml_config,
            auth_config=self.auth_config,
            environment_config=self.environment_config,
            mcp_config=self.mcp_config
        )
    
    def to_runtime_config(self) -> Any:
        """Convert to runtime configuration object."""
        if not RUNTIME_AVAILABLE:
            raise RuntimeError("Runtime is not available")
        return RuntimeConfig(
            app_name="BusinessInfinity",
            app_version="2.0.0",
            app_environment=self.environment_config.get("environment", "development"),
            azure_functions_enabled=True,
            auth_level="FUNCTION",
            aos_enabled=True,
            storage_type=self.storage_config.get("backend", "file"),
            messaging_type="servicebus" if self.azure_integration_enabled else "memory",
            observability_enabled=self.monitoring_config.get("metrics_enabled", True),
            log_level=self.monitoring_config.get("logging_level", "INFO"),
            circuit_breaker_enabled=True,
            retry_enabled=True,
            max_retries=self.workflow_config.get("retry_attempts", 3),
            custom_config=self.get_business_config()
        )
    
    def get_business_config(self) -> Dict[str, Any]:
        """Get business-specific configuration."""
        return {
            "company_name": self.company_name,
            "company_domain": self.company_domain,
            "business_model": self.business_model,
            "industry": self.industry,
            "covenant_config": self.covenant_config,
            "analytics_config": self.analytics_config,
            "workflow_config": self.workflow_config,
            "features": {
                "autonomous_boardroom": self.enable_autonomous_boardroom,
                "strategic_planning": self.enable_strategic_planning,
                "performance_monitoring": self.enable_performance_monitoring,
                "covenant_management": self.enable_covenant_management
            },
            "integrations": {
                "linkedin": self.linkedin_integration_enabled,
                "azure": self.azure_integration_enabled,
                "mcp": self.mcp_integration_enabled
            }
        }
    
    def update_from_dict(self, config_dict: Dict[str, Any]):
        """Update configuration from dictionary."""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
            elif key.endswith("_config") and hasattr(self, key):
                # Update nested config dictionaries
                current_config = getattr(self, key)
                if isinstance(current_config, dict) and isinstance(value, dict):
                    current_config.update(value)
    
    @classmethod
    def from_file(cls, config_path: str) -> "BusinessInfinityConfig":
        """Load configuration from file."""
        import json
        import yaml
        
        if config_path.endswith(".json"):
            with open(config_path, "r") as f:
                config_dict = json.load(f)
        elif config_path.endswith((".yml", ".yaml")):
            with open(config_path, "r") as f:
                config_dict = yaml.safe_load(f)
        else:
            raise ValueError("Configuration file must be JSON or YAML")
        
        config = cls()
        config.update_from_dict(config_dict)
        return config
    
    def save_to_file(self, config_path: str):
        """Save configuration to file."""
        import json
        import yaml
        
        config_dict = {
            "company_name": self.company_name,
            "company_domain": self.company_domain,
            "business_model": self.business_model,
            "industry": self.industry,
            "enable_autonomous_boardroom": self.enable_autonomous_boardroom,
            "enable_strategic_planning": self.enable_strategic_planning,
            "enable_performance_monitoring": self.enable_performance_monitoring,
            "enable_covenant_management": self.enable_covenant_management,
            "strategic_decision_threshold": self.strategic_decision_threshold,
            "consensus_requirement": self.consensus_requirement,
            "escalation_enabled": self.escalation_enabled,
            "linkedin_integration_enabled": self.linkedin_integration_enabled,
            "azure_integration_enabled": self.azure_integration_enabled,
            "mcp_integration_enabled": self.mcp_integration_enabled,
            "agent_config": self.agent_config,
            "messaging_config": self.messaging_config,
            "storage_config": self.storage_config,
            "monitoring_config": self.monitoring_config,
            "ml_config": self.ml_config,
            "auth_config": self.auth_config,
            "environment_config": self.environment_config,
            "mcp_config": self.mcp_config,
            "covenant_config": self.covenant_config,
            "analytics_config": self.analytics_config,
            "workflow_config": self.workflow_config
        }
        
        if config_path.endswith(".json"):
            with open(config_path, "w") as f:
                json.dump(config_dict, f, indent=2)
        elif config_path.endswith((".yml", ".yaml")):
            with open(config_path, "w") as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        else:
            raise ValueError("Configuration file must be JSON or YAML")


# Factory functions
def create_default_config() -> BusinessInfinityConfig:
    """Create default Business Infinity configuration."""
    return BusinessInfinityConfig()


def create_production_config() -> BusinessInfinityConfig:
    """Create production-optimized Business Infinity configuration."""
    config = BusinessInfinityConfig()
    
    # Production settings
    config.environment_config["environment"] = "production"
    config.environment_config["debug_enabled"] = False
    
    config.monitoring_config["logging_level"] = "WARNING"
    config.monitoring_config["telemetry_enabled"] = True
    
    config.storage_config["encryption_enabled"] = True
    config.storage_config["backup_enabled"] = True
    
    config.auth_config["multi_factor_enabled"] = True
    config.auth_config["session_timeout"] = 1800  # 30 minutes
    
    return config


def create_development_config() -> BusinessInfinityConfig:
    """Create development-optimized Business Infinity configuration."""
    config = BusinessInfinityConfig()
    
    # Development settings
    config.environment_config["environment"] = "development"
    config.environment_config["debug_enabled"] = True
    
    config.monitoring_config["logging_level"] = "DEBUG"
    config.monitoring_config["telemetry_enabled"] = False
    
    config.ml_config["training_enabled"] = True
    
    return config