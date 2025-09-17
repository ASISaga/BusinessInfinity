"""
Unified Utilities System
Consolidates functionality from utils/ directory
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path


class GovernanceError(Exception):
    """Exception raised when governance validation fails"""
    pass


class UnifiedUtilsManager:
    """
    Unified utilities manager that consolidates:
    - Governance and validation functions
    - Configuration management utilities  
    - Common helper functions
    - Manifest and schema utilities
    """
    
    def __init__(self):
        # Configuration paths
        self.config_dir = Path(__file__).parent.parent / "config"
        self.docs_dir = Path(__file__).parent.parent / "docs"
        self.dashboard_dir = Path(__file__).parent.parent / "dashboard"
        
        # Cached data
        self._ui_schemas: Dict[str, Any] = {}
        self._manifests: Dict[str, Any] = {}
    
    # === Governance Functions ===
    
    def validate_request(self, context: str, payload: Dict[str, Any]) -> None:
        """
        Validate requests based on context and payload
        Context ∈ {"inference","message","training"}
        
        Args:
            context: Type of request (inference, message, training)
            payload: Request payload containing role, scope, etc.
            
        Raises:
            GovernanceError: If validation fails
        """
        try:
            # Basic validation rules
            if context == "training":
                role = payload.get("role")
                demo = payload.get("demo", False)
                
                # Only governance role can do non-demo training
                if role != "Governance" and not demo:
                    raise GovernanceError("Training not permitted for this role.")
                
                # Check model name requirements for training
                model_name = payload.get("payload", {}).get("modelName")
                if not model_name:
                    raise GovernanceError("Model name required for training.")
            
            elif context == "inference":
                # Validate inference permissions
                role = payload.get("role", "")
                agent_id = payload.get("payload", {}).get("agentId")
                
                if not agent_id:
                    raise GovernanceError("Agent ID required for inference.")
                
                # Could add role-based agent access controls here
                
            elif context == "message":
                # Validate message permissions
                scope = payload.get("scope", "local")
                role = payload.get("role", "")
                
                # Network scope requires governance role
                if scope == "network" and role != "Governance":
                    raise GovernanceError("Network scope not permitted for this role.")
            
            # Additional custom validation rules can be added here
            
        except GovernanceError:
            raise
        except Exception as e:
            raise GovernanceError(f"Validation error: {str(e)}")
    
    def validate_agent_access(self, user_role: str, agent_id: str, operation: str) -> bool:
        """Validate if a user role can access a specific agent for an operation"""
        try:
            # Load agent access rules (could be from config)
            access_rules = self.load_config("agent_access_rules.json", default={})
            
            role_permissions = access_rules.get(user_role, {})
            agent_permissions = role_permissions.get(agent_id, [])
            
            return operation in agent_permissions
            
        except Exception as e:
            logging.warning(f"Error validating agent access: {e}")
            return True  # Default to allow if validation fails
    
    def validate_scope_permissions(self, user_role: str, scope: str) -> bool:
        """Validate if a user role can access a specific scope"""
        try:
            scope_rules = {
                "local": ["Founder", "Investor", "Employee", "Governance"],
                "network": ["Governance"],
                "global": ["Governance"]
            }
            
            allowed_roles = scope_rules.get(scope, [])
            return user_role in allowed_roles
            
        except Exception as e:
            logging.warning(f"Error validating scope permissions: {e}")
            return True  # Default to allow if validation fails
    
    # === Configuration Management ===
    
    def load_config(self, filename: str, default: Any = None) -> Any:
        """Load configuration from JSON file"""
        config_path = self.config_dir / filename
        
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logging.warning(f"Config file not found: {filename}")
                return default
        except Exception as e:
            logging.error(f"Error loading config {filename}: {e}")
            return default
    
    def save_config(self, filename: str, data: Any) -> bool:
        """Save configuration to JSON file"""
        config_path = self.config_dir / filename
        
        try:
            # Ensure config directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"Error saving config {filename}: {e}")
            return False
    
    def get_config_value(self, config_name: str, key_path: str, default: Any = None) -> Any:
        """Get a specific value from a config file using dot notation"""
        config = self.load_config(config_name)
        if not config:
            return default
        
        try:
            keys = key_path.split('.')
            value = config
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
        except Exception as e:
            logging.error(f"Error getting config value {key_path} from {config_name}: {e}")
            return default
    
    # === UI Schema and Manifest Management ===
    
    def get_ui_schema(self, role: str = None, scope: str = "local") -> Dict[str, Any]:
        """Get UI schema based on role and scope"""
        cache_key = f"{role}_{scope}"
        
        if cache_key not in self._ui_schemas:
            try:
                # Load base schema
                schema_file = f"ui_schema_{role}.json" if role else "ui_schema_default.json"
                schema = self.load_config(schema_file)
                
                if not schema:
                    # Fallback to basic schema
                    schema = {
                        "version": "1.0",
                        "role": role or "default",
                        "scope": scope,
                        "components": [],
                        "actions": []
                    }
                
                # Apply scope-based filtering
                if scope != "global":
                    schema = self._filter_schema_by_scope(schema, scope)
                
                self._ui_schemas[cache_key] = schema
                
            except Exception as e:
                logging.error(f"Error loading UI schema for {role}/{scope}: {e}")
                self._ui_schemas[cache_key] = {"error": f"Failed to load schema: {str(e)}"}
        
        return self._ui_schemas[cache_key]
    
    def _filter_schema_by_scope(self, schema: Dict[str, Any], scope: str) -> Dict[str, Any]:
        """Filter schema components based on scope"""
        try:
            filtered_schema = schema.copy()
            
            # Filter components
            if "components" in schema:
                filtered_components = []
                for component in schema["components"]:
                    component_scope = component.get("scope", ["local"])
                    if isinstance(component_scope, str):
                        component_scope = [component_scope]
                    
                    if scope in component_scope or "all" in component_scope:
                        filtered_components.append(component)
                
                filtered_schema["components"] = filtered_components
            
            # Filter actions
            if "actions" in schema:
                filtered_actions = []
                for action in schema["actions"]:
                    action_scope = action.get("scope", ["local"])
                    if isinstance(action_scope, str):
                        action_scope = [action_scope]
                    
                    if scope in action_scope or "all" in action_scope:
                        filtered_actions.append(action)
                
                filtered_schema["actions"] = filtered_actions
            
            return filtered_schema
            
        except Exception as e:
            logging.error(f"Error filtering schema by scope {scope}: {e}")
            return schema
    
    def get_manifest(self, manifest_name: str = "main") -> Dict[str, Any]:
        """Get application manifest"""
        if manifest_name not in self._manifests:
            try:
                # Try dashboard directory first
                manifest_path = self.dashboard_dir / f"{manifest_name}_manifest.json"
                if not manifest_path.exists():
                    manifest_path = self.dashboard_dir / "manifest.json"
                
                if manifest_path.exists():
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                else:
                    # Default manifest
                    manifest = {
                        "name": "Business Infinity",
                        "version": "1.0.0",
                        "description": "AI-powered business automation platform",
                        "features": ["agents", "orchestration", "analytics"],
                        "endpoints": []
                    }
                
                self._manifests[manifest_name] = manifest
                
            except Exception as e:
                logging.error(f"Error loading manifest {manifest_name}: {e}")
                self._manifests[manifest_name] = {"error": f"Failed to load manifest: {str(e)}"}
        
        return self._manifests[manifest_name]
    
    # === Helper Functions ===
    
    def extract_name_from_request(self, req_params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract name from request parameters (legacy compatibility)"""
        try:
            name = req_params.get("name", "World")
            
            if name:
                message = f"Hello, {name}. This HTTP triggered function executed successfully."
                return {"message": message, "status_code": 200}
            else:
                return {
                    "message": "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
                    "status_code": 200
                }
        except Exception as e:
            return {"message": f"Error processing request: {str(e)}", "status_code": 500}
    
    def validate_json_payload(self, payload: Any, required_fields: List[str] = None) -> Dict[str, Any]:
        """Validate JSON payload structure"""
        try:
            if not isinstance(payload, dict):
                return {"valid": False, "error": "Payload must be a JSON object"}
            
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in payload:
                        missing_fields.append(field)
                
                if missing_fields:
                    return {
                        "valid": False, 
                        "error": f"Missing required fields: {', '.join(missing_fields)}"
                    }
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    def format_error_response(self, error: Union[str, Exception], status_code: int = 500) -> Dict[str, Any]:
        """Format error response consistently"""
        error_msg = str(error) if isinstance(error, Exception) else error
        
        return {
            "error": error_msg,
            "status_code": status_code,
            "timestamp": self.get_current_timestamp()
        }
    
    def format_success_response(self, data: Any = None, message: str = None) -> Dict[str, Any]:
        """Format success response consistently"""
        response = {
            "status": "success",
            "timestamp": self.get_current_timestamp()
        }
        
        if data is not None:
            response["data"] = data
        if message:
            response["message"] = message
        
        return response
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
    
    def sanitize_input(self, input_text: str, max_length: int = 1000) -> str:
        """Sanitize user input"""
        if not isinstance(input_text, str):
            input_text = str(input_text)
        
        # Truncate to max length
        if len(input_text) > max_length:
            input_text = input_text[:max_length]
        
        # Basic sanitization (could be enhanced)
        input_text = input_text.strip()
        
        return input_text
    
    def parse_query_params(self, query_string: str) -> Dict[str, str]:
        """Parse query string into dictionary"""
        try:
            from urllib.parse import parse_qs
            
            params = {}
            parsed = parse_qs(query_string)
            
            for key, values in parsed.items():
                # Take first value if multiple
                params[key] = values[0] if values else ""
            
            return params
            
        except Exception as e:
            logging.error(f"Error parsing query params: {e}")
            return {}
    
    # === Configuration Validation ===
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate utilities configuration"""
        issues = []
        
        # Check if config directory exists
        if not self.config_dir.exists():
            issues.append(f"Config directory not found: {self.config_dir}")
        
        # Check essential config files
        essential_configs = [
            "orchestrator_config.json",
            "agents-profile.json",
            "domain_contexts.json"
        ]
        
        missing_configs = []
        for config_file in essential_configs:
            config_path = self.config_dir / config_file
            if not config_path.exists():
                missing_configs.append(config_file)
        
        if missing_configs:
            issues.append(f"Missing config files: {', '.join(missing_configs)}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config_dir_exists": self.config_dir.exists(),
            "missing_configs": missing_configs,
            "cached_schemas": len(self._ui_schemas),
            "cached_manifests": len(self._manifests)
        }


# Create singleton instance
utils_manager = UnifiedUtilsManager()

# Export individual functions for backward compatibility
def validate_request(context: str, payload: Dict[str, Any]) -> None:
    """Backward compatibility wrapper"""
    return utils_manager.validate_request(context, payload)

def get_ui_schema(role: str = None, scope: str = "local") -> Dict[str, Any]:
    """Backward compatibility wrapper"""
    return utils_manager.get_ui_schema(role, scope)

# Export all
__all__ = [
    'utils_manager', 'UnifiedUtilsManager', 'GovernanceError',
    'validate_request', 'get_ui_schema'
]