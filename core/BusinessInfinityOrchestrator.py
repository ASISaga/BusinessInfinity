"""
Business Infinity Orchestrator

This orchestrator extends the generic AgentOperatingSystem with business-specific functionality:
- Decision engine integration for business decision making
- MCP (Model Context Protocol) handler for external system integration  
- Governance validation for business rule compliance
- Business event handling and process automation
- Integration with Business Infinity storage and environment managers

Generic orchestration capabilities are provided by the base AOS class.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone

# Import core Business Infinity components
from .agents import agent_manager, UnifiedAgentManager
from .mcp import mcp_handler

# Import decision engine components (business-specific)
try:
    from ..shared.framework.server.decision_engine import DecisionEngine
    from ..shared.framework.server.config_loader import load_principles, load_decision_tree, load_adapters
    DECISION_ENGINE_AVAILABLE = True
except ImportError:
    DECISION_ENGINE_AVAILABLE = False
    DecisionEngine = None

# Import governance utilities (business-specific)
try:
    from ..utils.governance import validate_request, GovernanceError
except ImportError:
    def validate_request(request):
        return True
    
    class GovernanceError(Exception):
        pass

# Import Business Infinity storage and environment managers (business-specific)
try:
    from ..storage import storage_manager
except ImportError:
    storage_manager = None

try:
    from ..environment import env_manager
except ImportError:
    env_manager = None

# Import generic orchestration from AOS
from RealmOfAgents.AgentOperatingSystem.AgentOperatingSystem import AgentOperatingSystem

class BusinessInfinityOrchestrator(AgentOperatingSystem):
    """
    Business Infinity specific orchestrator that extends AOS with:
    1. Business decision making through decision engine
    2. External system integration via MCP
    3. Business rule compliance through governance
    4. Business event handling and process automation
    
    Generic agent coordination and workflow management is inherited from AOS.
    """
    
    def __init__(self):
        # Initialize base AOS with Business Infinity's agent manager
        super().__init__(agent_manager=agent_manager)
        
        # Business-specific components
        self.agent_manager = agent_manager
        self.mcp_handler = mcp_handler
        
        # Initialize decision engine (business-specific)
        self.decision_engine = None
        if DECISION_ENGINE_AVAILABLE:
            try:
                principles = load_principles()
                tree = load_decision_tree()
                adapters = load_adapters()
                self.decision_engine = DecisionEngine(tree, adapters, principles)
                logging.info("Decision engine initialized successfully")
            except Exception as e:
                logging.warning(f"Could not initialize decision engine: {e}")
        
        # Business-specific storage and environment integration
        self.storage_manager = storage_manager
        self.env_manager = env_manager
        
        # Register business event handlers
        self._register_business_event_handlers()
        
        logging.info("BusinessInfinityOrchestrator initialized")
    
    # Business Decision Making
    async def process_decision(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a business decision using the decision engine.
        
        This method integrates governance validation and business rule compliance
        before processing decisions through the decision engine.
        
        Args:
            evidence: Evidence data for decision making
            
        Returns:
            Dict with decision results or error information
        """
        if not self.decision_engine:
            return {"error": "Decision engine not available"}
        
        try:
            # Validate the request using business governance rules
            if not validate_request(evidence):
                raise GovernanceError("Request validation failed")
            
            # Process the decision through the business decision engine
            result = self.decision_engine.run(evidence)
            
            # Log the business decision
            logging.info(f"Business decision processed: {result}")
            
            # Emit business decision event
            await self.emit_event("business_decision_made", {
                "evidence": evidence,
                "result": result,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            return result
            
        except GovernanceError as e:
            error_result = {"error": f"Governance error: {str(e)}"}
            logging.warning(f"Governance error in decision processing: {e}")
            return error_result
        except Exception as e:
            error_result = {"error": f"Decision processing error: {str(e)}"}
            logging.error(f"Decision processing error: {e}")
            return error_result
    
    # Business Event Handling
    def _register_business_event_handlers(self):
        """Register handlers for business-specific events."""
        self.register_event_handler("budget_alert", self._handle_budget_alert)
        self.register_event_handler("quality_issue", self._handle_quality_issue)  
        self.register_event_handler("market_change", self._handle_market_change)
        self.register_event_handler("operational_alert", self._handle_operational_alert)
        self.register_event_handler("business_decision_made", self._handle_business_decision)
    
    async def _handle_budget_alert(self, event_data: Dict[str, Any]):
        """Handle budget-related alerts."""
        logging.info(f"Processing budget alert: {event_data}")
        # Business-specific budget alert logic
        # This could trigger workflow escalation, notifications, etc.
    
    async def _handle_quality_issue(self, event_data: Dict[str, Any]):
        """Handle quality-related issues."""
        logging.info(f"Processing quality issue: {event_data}")
        # Business-specific quality issue logic
    
    async def _handle_market_change(self, event_data: Dict[str, Any]):
        """Handle market change events."""
        logging.info(f"Processing market change: {event_data}")
        # Business-specific market change logic
    
    async def _handle_operational_alert(self, event_data: Dict[str, Any]):
        """Handle operational alerts."""
        logging.info(f"Processing operational alert: {event_data}")
        # Business-specific operational alert logic
    
    async def _handle_business_decision(self, event_data: Dict[str, Any]):
        """Handle business decision completion events."""
        logging.info(f"Business decision completed: {event_data.get('result', {})}")
        # Could trigger follow-up actions, notifications, audit logging, etc.
    
    # Business Process Integration
    async def handle_business_event(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle business-specific events and trigger appropriate workflows.
        
        Args:
            event_type: Type of business event
            event_data: Event data and context
            
        Returns:
            Dict with event handling results
        """
        try:
            # Emit the event to registered handlers
            await self.emit_event(event_type, event_data)
            
            # Business-specific event processing logic
            if event_type in ["budget_alert", "quality_issue"]:
                # These events might trigger urgent workflows
                workflow_def = self._create_urgent_response_workflow(event_type, event_data)
                workflow_id = await self.execute_workflow(workflow_def)
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "message": f"Urgent response workflow initiated for {event_type}"
                }
            
            return {
                "status": "success", 
                "message": f"Business event {event_type} handled successfully"
            }
            
        except Exception as e:
            logging.error(f"Business event handling failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _create_urgent_response_workflow(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow definition for urgent business events."""
        return {
            "name": f"Urgent Response: {event_type}",
            "steps": [
                {
                    "id": "assess",
                    "agent": "assessment_agent", 
                    "task": f"Assess {event_type} impact: {event_data}",
                    "depends_on": []
                },
                {
                    "id": "notify",
                    "agent": "notification_agent",
                    "task": f"Notify stakeholders about {event_type}",
                    "depends_on": ["assess"]
                },
                {
                    "id": "escalate",
                    "agent": "escalation_agent",
                    "task": "Escalate if needed based on assessment",
                    "depends_on": ["assess", "notify"]
                }
            ]
        }
    
    # System Status with Business Context
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive Business Infinity system status.
        
        Extends base AOS status with business-specific information.
        """
        base_status = await self.get_aos_status()
        
        # Add Business Infinity specific status
        bi_status = {
            **base_status,
            "business_components": {
                "decision_engine": self.decision_engine is not None,
                "mcp_handler": {
                    "active": self.mcp_handler is not None,
                    "methods": len(self.mcp_handler.method_handlers) if self.mcp_handler else 0
                },
                "storage_manager": self.storage_manager is not None,
                "environment_manager": self.env_manager is not None
            },
            "agents": {
                "count": self.agent_manager.get_agent_count() if self.agent_manager else 0,
                "available": self.agent_manager.list_agent_ids() if self.agent_manager else []
            },
            "system_type": "BusinessInfinity"
        }
        
        return bi_status


# Create global orchestrator instance
orchestrator = BusinessInfinityOrchestrator()

# Export for backward compatibility
async def process_decision(evidence: Dict[str, Any]) -> Dict[str, Any]:
    """Process decision through orchestrator"""
    return await orchestrator.process_decision(evidence)

async def coordinate_agents(request: Dict[str, Any]) -> Dict[str, Any]:
    """Coordinate agents through orchestrator"""
    return await orchestrator.coordinate_agents(request)