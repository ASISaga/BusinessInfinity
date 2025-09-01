"""
Unified Environment Management System
Enhanced version of api/EnvManager.py with additional functionality
"""
import os
from typing import Any, Optional, Union


class UnifiedEnvManager:
    """
    Centralized environment variable access with enhanced functionality
    """

    @staticmethod
    def get(key: str, default: Any = None) -> Optional[str]:
        """Get an environment variable, with optional default"""
        return os.getenv(key, default)

    @staticmethod
    def get_required(key: str) -> str:
        """Get a required environment variable, raise if missing"""
        value = os.getenv(key)
        if value is None:
            raise EnvironmentError(f"Missing required environment variable: {key}")
        return value

    @staticmethod
    def get_optional(key: str, default: Any = None) -> Optional[str]:
        """Get an optional environment variable (alias for get)"""
        return UnifiedEnvManager.get(key, default)

    @staticmethod
    def get_int(key: str, default: Optional[int] = None) -> Optional[int]:
        """Get an environment variable as int, with optional default"""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Environment variable {key} is not a valid integer: {value}")

    @staticmethod
    def get_float(key: str, default: Optional[float] = None) -> Optional[float]:
        """Get an environment variable as float, with optional default"""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Environment variable {key} is not a valid float: {value}")

    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        """Get an environment variable as bool"""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ("1", "true", "yes", "on", "enabled")

    @staticmethod
    def get_list(key: str, separator: str = ",", default: Optional[list] = None) -> list:
        """Get an environment variable as a list, split by separator"""
        value = os.getenv(key)
        if value is None:
            return default or []
        return [item.strip() for item in value.split(separator) if item.strip()]

    @staticmethod
    def get_json(key: str, default: Any = None) -> Any:
        """Get an environment variable as JSON"""
        import json
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise ValueError(f"Environment variable {key} is not valid JSON: {value}")

    @staticmethod
    def require_any(keys: list, error_message: str = None) -> str:
        """Require at least one of the specified environment variables"""
        for key in keys:
            value = os.getenv(key)
            if value:
                return value
        
        error_msg = error_message or f"At least one of these environment variables is required: {', '.join(keys)}"
        raise EnvironmentError(error_msg)

    @staticmethod
    def get_azure_connection_string(service: str = "storage") -> str:
        """Get Azure connection string with fallback patterns"""
        patterns = {
            "storage": [
                "AzureWebJobsStorage",
                "AZURE_STORAGE_CONNECTION_STRING",
                "STORAGE_CONNECTION_STRING"
            ],
            "tables": [
                "AZURE_TABLES_CONNECTION_STRING",
                "AzureWebJobsStorage",
                "AZURE_STORAGE_CONNECTION_STRING"
            ],
            "queues": [
                "AZURE_QUEUES_CONNECTION_STRING", 
                "AzureWebJobsStorage",
                "AZURE_STORAGE_CONNECTION_STRING"
            ],
            "servicebus": [
                "AZURE_SERVICE_BUS_CONNECTION_STRING",
                "SERVICE_BUS_CONNECTION_STRING"
            ]
        }
        
        keys = patterns.get(service, [f"AZURE_{service.upper()}_CONNECTION_STRING"])
        return UnifiedEnvManager.require_any(keys, f"Missing Azure {service} connection string")

    @staticmethod
    def get_ml_config() -> dict:
        """Get Azure ML configuration"""
        return {
            "subscription_id": UnifiedEnvManager.get("AZURESUBSCRIPTION_ID"),
            "resource_group": UnifiedEnvManager.get("AZURERESOURCEGROUP"),
            "workspace": UnifiedEnvManager.get("AZUREML_WORKSPACE"),
            "pipeline_name": UnifiedEnvManager.get("PIPELINEENDPOINT_NAME"),
            "ml_url": UnifiedEnvManager.get("MLENDPOINT_URL"),
            "ml_key": UnifiedEnvManager.get("MLENDPOINT_KEY")
        }

    @staticmethod
    def get_agent_endpoints() -> dict:
        """Get agent endpoint configurations"""
        return {
            "cmo": {
                "scoring_uri": UnifiedEnvManager.get("AML_CMO_SCORING_URI", ""),
                "key": UnifiedEnvManager.get("AML_CMO_KEY", "")
            },
            "cfo": {
                "scoring_uri": UnifiedEnvManager.get("AML_CFO_SCORING_URI", ""),
                "key": UnifiedEnvManager.get("AML_CFO_KEY", "")
            },
            "cto": {
                "scoring_uri": UnifiedEnvManager.get("AML_CTO_SCORING_URI", ""),
                "key": UnifiedEnvManager.get("AML_CTO_KEY", "")
            }
        }

    @staticmethod
    def validate_environment() -> dict:
        """Validate environment configuration"""
        issues = []
        warnings = []
        
        # Check critical variables
        try:
            UnifiedEnvManager.get_azure_connection_string("storage")
        except EnvironmentError:
            issues.append("Missing Azure Storage connection string")
        
        # Check ML configuration
        ml_config = UnifiedEnvManager.get_ml_config()
        missing_ml = [k for k, v in ml_config.items() if not v]
        if missing_ml:
            warnings.append(f"Missing ML configuration: {', '.join(missing_ml)}")
        
        # Check agent endpoints
        agent_endpoints = UnifiedEnvManager.get_agent_endpoints()
        configured_agents = [
            agent for agent, config in agent_endpoints.items() 
            if config["scoring_uri"] and config["key"]
        ]
        if not configured_agents:
            warnings.append("No agent endpoints configured")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "configured_agents": configured_agents,
            "ml_configured": all(ml_config.values()),
            "storage_configured": True  # If we got here, storage is configured
        }

    @staticmethod
    def get_all_env_vars() -> dict:
        """Get all environment variables (for debugging)"""
        return dict(os.environ)

    @staticmethod
    def get_env_vars_by_prefix(prefix: str) -> dict:
        """Get environment variables with a specific prefix"""
        return {k: v for k, v in os.environ.items() if k.startswith(prefix)}


# Convenience instance and backwards compatibility
env_manager = UnifiedEnvManager()

# Backwards compatibility class
class EnvManager(UnifiedEnvManager):
    """Backwards compatibility wrapper"""
    pass