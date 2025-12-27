"""
BusinessInfinityConfig - Configuration for Business Infinity autonomous boardroom

REFACTORED: Now uses runtime abstractions with fallback to AOS

Note: The canonical configuration is in src/bi_config.py which extends runtime.RuntimeConfig.
This module provides backward compatibility for existing code.
"""
import os

# Try to import from runtime first
try:
    from runtime import RuntimeConfig
    RUNTIME_AVAILABLE = True
except ImportError:
    RUNTIME_AVAILABLE = False

# Import AOS config with fallback
try:
    from AgentOperatingSystem.config import default_config, AOSConfig
    AOS_AVAILABLE = True
except ImportError:
    AOS_AVAILABLE = False
    default_config = None
    AOSConfig = None

class BusinessInfinityConfig:
    def __init__(self):
        # Use AOS config if available
        self.aos_config = default_config if AOS_AVAILABLE else None
        
        # Business configuration
        self.business_name = os.getenv("BUSINESS_NAME", "Business Infinity")
        self.industry = os.getenv("BUSINESS_INDUSTRY", "Technology")
        self.stage = os.getenv("BUSINESS_STAGE", "Growth")
        self.market = os.getenv("TARGET_MARKET", "Global")
        self.enable_autonomous_boardroom = True
        self.perpetual_operation = True
        self.session_frequency_hours = int(os.getenv("BOARDROOM_SESSION_FREQUENCY", "1"))
        self.enable_lora_adapters = True
        self.mentor_mode_enabled = bool(os.getenv("MENTOR_MODE_ENABLED", "false").lower() == "true")
        self.legendary_profiles_path = os.getenv("LEGENDARY_PROFILES_PATH", "config/legendary_profiles.json")
        self.mcp_servers = {
            "linkedin": os.getenv("LINKEDIN_MCP_QUEUE", "bi-linkedin-mcp"),
            "reddit": os.getenv("REDDIT_MCP_QUEUE", "bi-reddit-mcp"),
            "erpnext": os.getenv("ERPNEXT_MCP_QUEUE", "bi-erpnext-mcp")
        }
        self.service_bus_connection = os.getenv("AZURE_SERVICEBUS_CONNECTION_STRING")
        self.decision_threshold = float(os.getenv("DECISION_THRESHOLD", "0.7"))
        self.collaboration_mode = "legendary_consensus"
        self.reporting_enabled = True
        self.metrics_collection = True
        self.performance_tracking = True
    
    def to_runtime_config(self):
        """Convert to runtime configuration."""
        if not RUNTIME_AVAILABLE:
            raise RuntimeError("Runtime is not available")
        return RuntimeConfig(
            app_name="BusinessInfinity",
            app_version="2.0.0",
            custom_config={
                "business_name": self.business_name,
                "industry": self.industry,
                "stage": self.stage,
                "market": self.market,
                "enable_autonomous_boardroom": self.enable_autonomous_boardroom,
                "mentor_mode_enabled": self.mentor_mode_enabled,
                "mcp_servers": self.mcp_servers,
                "decision_threshold": self.decision_threshold
            }
        )
