"""
Generic Runtime Configuration Loader

Provides generic configuration loading for any application built on
AgentOperatingSystem runtime.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RuntimeConfig:
    """
    Generic runtime configuration for applications built on AgentOperatingSystem.
    
    This is a minimal, generic configuration that can be extended by specific
    applications (e.g., BusinessInfinity, other apps).
    """
    
    # Application Identity
    app_name: str = "GenericApp"
    app_version: str = "1.0.0"
    app_environment: str = "development"  # development, staging, production
    
    # Azure Functions Configuration
    azure_functions_enabled: bool = True
    auth_level: str = "FUNCTION"  # ANONYMOUS, FUNCTION, ADMIN
    
    # Agent Framework Configuration
    agent_framework_enabled: bool = False
    agent_framework_endpoint: Optional[str] = None
    
    # AgentOperatingSystem Configuration
    aos_enabled: bool = True
    aos_config_path: Optional[str] = None
    
    # Storage Configuration
    storage_type: str = "memory"  # memory, blob, table, cosmos
    storage_connection_string: Optional[str] = None
    
    # Messaging Configuration
    messaging_type: str = "memory"  # memory, servicebus, eventhub
    messaging_connection_string: Optional[str] = None
    
    # Observability Configuration
    observability_enabled: bool = True
    log_level: str = "INFO"
    application_insights_key: Optional[str] = None
    
    # Reliability Configuration
    circuit_breaker_enabled: bool = True
    retry_enabled: bool = True
    max_retries: int = 3
    
    # Custom Configuration (for application-specific settings)
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls) -> 'RuntimeConfig':
        """Load configuration from environment variables."""
        return cls(
            app_name=os.getenv('APP_NAME', 'GenericApp'),
            app_version=os.getenv('APP_VERSION', '1.0.0'),
            app_environment=os.getenv('APP_ENVIRONMENT', 'development'),
            azure_functions_enabled=os.getenv('AZURE_FUNCTIONS_ENABLED', 'true').lower() == 'true',
            auth_level=os.getenv('AUTH_LEVEL', 'FUNCTION'),
            agent_framework_enabled=os.getenv('AGENT_FRAMEWORK_ENABLED', 'false').lower() == 'true',
            agent_framework_endpoint=os.getenv('AGENT_FRAMEWORK_ENDPOINT'),
            aos_enabled=os.getenv('AOS_ENABLED', 'true').lower() == 'true',
            aos_config_path=os.getenv('AOS_CONFIG_PATH'),
            storage_type=os.getenv('STORAGE_TYPE', 'memory'),
            storage_connection_string=os.getenv('STORAGE_CONNECTION_STRING'),
            messaging_type=os.getenv('MESSAGING_TYPE', 'memory'),
            messaging_connection_string=os.getenv('MESSAGING_CONNECTION_STRING'),
            observability_enabled=os.getenv('OBSERVABILITY_ENABLED', 'true').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            application_insights_key=os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING'),
            circuit_breaker_enabled=os.getenv('CIRCUIT_BREAKER_ENABLED', 'true').lower() == 'true',
            retry_enabled=os.getenv('RETRY_ENABLED', 'true').lower() == 'true',
            max_retries=int(os.getenv('MAX_RETRIES', '3')),
        )
    
    @classmethod
    def from_json(cls, config_path: str) -> 'RuntimeConfig':
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        return cls(**config_data)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'RuntimeConfig':
        """Create configuration from dictionary."""
        custom_config = config_dict.pop('custom_config', {})
        config = cls(**{k: v for k, v in config_dict.items() if k in cls.__dataclass_fields__})
        config.custom_config = custom_config
        return config


def load_runtime_config(
    config_path: Optional[str] = None,
    config_dict: Optional[Dict[str, Any]] = None,
    use_env: bool = True
) -> RuntimeConfig:
    """
    Load runtime configuration from various sources.
    
    Priority order:
    1. config_dict (if provided)
    2. config_path (if provided)
    3. Environment variables (if use_env=True)
    4. Default configuration
    
    Args:
        config_path: Path to JSON configuration file
        config_dict: Configuration dictionary
        use_env: Whether to use environment variables
        
    Returns:
        RuntimeConfig instance
    """
    if config_dict:
        return RuntimeConfig.from_dict(config_dict)
    elif config_path and os.path.exists(config_path):
        return RuntimeConfig.from_json(config_path)
    elif use_env:
        return RuntimeConfig.from_env()
    else:
        return RuntimeConfig()


def merge_configs(base: RuntimeConfig, override: Dict[str, Any]) -> RuntimeConfig:
    """
    Merge override configuration into base configuration.
    
    Args:
        base: Base RuntimeConfig
        override: Dictionary with override values
        
    Returns:
        New RuntimeConfig with merged values
    """
    base_dict = {
        'app_name': base.app_name,
        'app_version': base.app_version,
        'app_environment': base.app_environment,
        'azure_functions_enabled': base.azure_functions_enabled,
        'auth_level': base.auth_level,
        'agent_framework_enabled': base.agent_framework_enabled,
        'agent_framework_endpoint': base.agent_framework_endpoint,
        'aos_enabled': base.aos_enabled,
        'aos_config_path': base.aos_config_path,
        'storage_type': base.storage_type,
        'storage_connection_string': base.storage_connection_string,
        'messaging_type': base.messaging_type,
        'messaging_connection_string': base.messaging_connection_string,
        'observability_enabled': base.observability_enabled,
        'log_level': base.log_level,
        'application_insights_key': base.application_insights_key,
        'circuit_breaker_enabled': base.circuit_breaker_enabled,
        'retry_enabled': base.retry_enabled,
        'max_retries': base.max_retries,
        'custom_config': base.custom_config.copy(),
    }
    
    # Merge override values
    for key, value in override.items():
        if key == 'custom_config' and isinstance(value, dict):
            base_dict['custom_config'].update(value)
        else:
            base_dict[key] = value
    
    return RuntimeConfig.from_dict(base_dict)
