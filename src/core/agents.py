"""
Unified Agent Management System for Business Infinity

This module provides the core agent management system that integrates with
the new AOS-based business agents architecture. It provides a unified interface for
managing and orchestrating all business-specific agents built on top of AOS.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union

# Import the new Business Infinity system
try:
    from ..business_infinity import BusinessInfinity, BusinessInfinityConfig, get_business_infinity
    from ..business_agents import (
        ChiefExecutiveOfficer, BusinessCFO, BusinessCTO, 
        FounderAgent, InvestorAgent,
        create_ceo, create_cfo, create_cto, 
        create_founder, create_investor
    )
    BUSINESS_INFINITY_AVAILABLE = True
except ImportError:
    BUSINESS_INFINITY_AVAILABLE = False
    logging.warning("Business Infinity system not available")

# Fallback to MVP agents
if not BUSINESS_INFINITY_AVAILABLE:
    try:
        from ..mvp_agents import AgentManager
        MVP_AGENTS_AVAILABLE = True
    except ImportError:
        MVP_AGENTS_AVAILABLE = False

# Optional imports with fallbacks
try:
    from semantic_kernel import Kernel
    from semantic_kernel.contents import ChatHistory
    AGENT_FRAMEWORK_AVAILABLE = True
except ImportError:
    AGENT_FRAMEWORK_AVAILABLE = False

logger = logging.getLogger(__name__)


class UnifiedAgentManager:
    """
    Unified agent management system that provides:
    - Business Infinity agent instantiation and management
    - Agent orchestration and coordination
    - Backward compatibility with legacy systems
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the unified agent manager.
        
        Args:
            config: Configuration dictionary for agents
        """
        self.config = config or {}
        self.business_infinity = None
        self.mvp_manager = None
        self.agents: Dict[str, Any] = {}
        self.initialized = False
        
        # Initialize appropriate system
        if BUSINESS_INFINITY_AVAILABLE:
            self._initialize_business_infinity()
        elif MVP_AGENTS_AVAILABLE:
            self._initialize_mvp_agents()
        else:
            logger.error("No agent system available")
    
    def _initialize_business_infinity(self):
        """Initialize Business Infinity system"""
        try:
            bi_config = BusinessInfinityConfig()
            
            # Apply custom config if provided
            if self.config:
                for key, value in self.config.items():
                    if hasattr(bi_config, key):
                        setattr(bi_config, key, value)
            
            self.business_infinity = BusinessInfinity(bi_config)
            self.initialized = True
            logger.info("Business Infinity system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Business Infinity system: {e}")
            self.initialized = False
    
    def _initialize_mvp_agents(self):
        """Initialize MVP agent fallback"""
        try:
            self.mvp_manager = AgentManager()
            self.initialized = True
            logger.info("MVP agent system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MVP agent system: {e}")
            self.initialized = False
    
    def get_agent(self, agent_name: str) -> Optional[Any]:
        """
        Get a specific agent by name.
        
        Args:
            agent_name: Name of the agent (CEO, CFO, etc.)
            
        Returns:
            Agent instance or None if not found
        """
        if self.business_infinity:
            return self.business_infinity.get_agent(agent_name)
        elif self.mvp_manager:
            return self.mvp_manager.get_agent(agent_name.lower())
        
        return None
    
    def get_all_agents(self) -> Dict[str, Any]:
        """Get all initialized agents."""
        if self.business_infinity:
            agents = {}
            for agent_info in self.business_infinity.list_agents():
                role = agent_info["role"]
                agent = self.business_infinity.get_agent(role)
                if agent:
                    agents[role] = agent
            return agents
        elif self.mvp_manager:
            return {agent["role"]: self.mvp_manager.get_agent(agent["role"].lower()) 
                   for agent in self.mvp_manager.list_agents()}
        
        return {}
    
    def get_agent_profiles(self) -> str:
        """
        Get JSON string of all agent profiles for backward compatibility.
        
        Returns:
            JSON string of agent profiles
        """
        if not self.initialized:
            return "[]"
        
        profiles = []
        
        if self.business_infinity:
            agents_list = self.business_infinity.list_agents()
            for agent_info in agents_list:
                role = agent_info["role"]
                profiles.append({
                    "agentId": role.lower(),
                    "name": f"Business Infinity {role}",
                    "role": role,
                    "type": agent_info.get("type", "Business"),
                    "status": agent_info.get("status", "active"),
                    "leadership_style": "strategic",
                    "active": agent_info.get("status") == "active"
                })
        elif self.mvp_manager:
            profiles = self.mvp_manager.list_agents()
            
        return json.dumps(profiles, indent=2)
    
    async def execute_agent_task(self, agent_name: str, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a task with a specific agent.
        
        Args:
            agent_name: Name of the agent
            task: Task description
            context: Optional context
            
        Returns:
            Task execution result
        """
        try:
            if self.business_infinity:
                response = await self.business_infinity.ask_agent(agent_name, task, context)
                return {
                    "status": "success",
                    "agent": agent_name,
                    "task": task,
                    "response": response,
                    "system": "business_infinity"
                }
            elif self.mvp_manager:
                response = await self.mvp_manager.ask_agent(agent_name.lower(), task, context)
                return {
                    "status": "success",
                    "agent": agent_name,
                    "task": task,
                    "response": response,
                    "system": "mvp"
                }
            else:
                return {
                    "status": "error",
                    "error": "No agent system available"
                }
                
        except Exception as e:
            logger.error(f"Failed to execute task for {agent_name}: {e}")
            return {
                "status": "error",
                "agent": agent_name,
                "task": task,
                "error": str(e)
            }
    
    async def orchestrate_leadership_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate a leadership decision across multiple agents.
        
        Args:
            decision_context: Context and parameters for the decision
            
        Returns:
            Decision result
        """
        try:
            if self.business_infinity:
                return await self.business_infinity.make_strategic_decision(decision_context)
            else:
                # Fallback implementation
                return {
                    "status": "completed",
                    "decision": "fallback_decision_process",
                    "system": "fallback",
                    "context": decision_context
                }
                
        except Exception as e:
            logger.error(f"Failed to orchestrate leadership decision: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def execute_business_workflow(self, workflow_name: str, workflow_params: Dict[str, Any]) -> str:
        """
        Execute a business workflow.
        
        Args:
            workflow_name: Name of the workflow to execute
            workflow_params: Parameters for the workflow
            
        Returns:
            Workflow execution ID
        """
        try:
            if self.business_infinity:
                return await self.business_infinity.execute_business_workflow(workflow_name, workflow_params)
            else:
                # Fallback workflow execution
                return f"fallback_{workflow_name}_{asyncio.get_event_loop().time()}"
                
        except Exception as e:
            logger.error(f"Failed to execute workflow {workflow_name}: {e}")
            return f"error_{asyncio.get_event_loop().time()}"
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        base_status = {
            "initialized": self.initialized,
            "business_infinity_available": BUSINESS_INFINITY_AVAILABLE,
            "mvp_agents_available": MVP_AGENTS_AVAILABLE,
            "semantic_kernel_available": AGENT_FRAMEWORK_AVAILABLE,
            "system_type": "UnifiedAgentManager"
        }
        
        if self.business_infinity:
            # Get Business Infinity status asynchronously
            asyncio.create_task(self._get_bi_status_async(base_status))
        
        return base_status
    
    async def _get_bi_status_async(self, base_status: Dict[str, Any]):
        """Get Business Infinity status asynchronously"""
        try:
            bi_status = await self.business_infinity.get_business_status()
            base_status["business_infinity_status"] = bi_status
        except Exception as e:
            base_status["business_infinity_error"] = str(e)
    
    async def get_complete_system_status(self) -> Dict[str, Any]:
        """Get complete system status including async data"""
        base_status = self.get_system_status()
        
        if self.business_infinity:
            try:
                bi_status = await self.business_infinity.get_business_status()
                base_status["business_infinity_status"] = bi_status
            except Exception as e:
                base_status["business_infinity_error"] = str(e)
        
        return base_status


# Global unified manager instance
_unified_manager = None

def get_unified_manager(config: Dict[str, Any] = None) -> UnifiedAgentManager:
    """Get global unified manager instance"""
    global _unified_manager
    if _unified_manager is None:
        _unified_manager = UnifiedAgentManager(config)
    return _unified_manager

def initialize_unified_manager(config: Dict[str, Any] = None) -> UnifiedAgentManager:
    """Initialize and return unified manager"""
    global _unified_manager
    _unified_manager = UnifiedAgentManager(config)
    return _unified_manager


# Backward compatibility functions
async def ask_agent(agent_name: str, message: str, context: Dict[str, Any] = None) -> Optional[str]:
    """Ask an agent a question (backward compatibility)"""
    manager = get_unified_manager()
    result = await manager.execute_agent_task(agent_name, message, context)
    return result.get("response") if result.get("status") == "success" else None

def get_agent_profiles_json() -> str:
    """Get agent profiles JSON (backward compatibility)"""
    manager = get_unified_manager()
    return manager.get_agent_profiles()

def get_agent_by_name(agent_name: str):
    """Get agent by name (backward compatibility)"""
    manager = get_unified_manager()
    return manager.get_agent(agent_name)


# Export the main functions for backward compatibility
__all__ = [
    'UnifiedAgentManager',
    'get_unified_manager',
    'initialize_unified_manager',
    'ask_agent',
    'get_agent_profiles_json',
    'get_agent_by_name'
]