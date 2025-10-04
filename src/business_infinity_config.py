"""
BusinessInfinityConfig - Configuration for Business Infinity autonomous boardroom
"""
import os
from AgentOperatingSystem.config import default_config, AOSConfig

class BusinessInfinityConfig:
    def __init__(self):
        self.aos_config = default_config
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
