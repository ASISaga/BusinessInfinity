"""
Adapter Orchestrator for Business Infinity

Main integration point for LoRA adapter management, self-learning, and model upgrades.
Coordinates all adapter-related functionality and provides a unified API for the
Business Infinity system.

This module serves as the primary interface between the boardroom agents and
the LoRA adapter system, handling:
- Adapter loading and orchestration
- Self-learning loop management
- Model upgrade coordination
- Performance evaluation and monitoring
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# Import local adapter components
from .lora_adapter_manager import LoRAAdapterManager, BoardroomRole, ModelConfig
from .self_learning_system import SelfLearningSystem, LearningPhase, DatasetType
from .model_upgrade_manager import ModelUpgradeManager, UpgradeStatus
from .evaluation_harness import EvaluationHarness, MetricType

logger = logging.getLogger(__name__)


class SystemStatus(Enum):
    """Overall system status"""
    INITIALIZING = "initializing"
    READY = "ready"
    LEARNING = "learning"
    EVALUATING = "evaluating"
    UPGRADING = "upgrading" 
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class SystemMetrics:
    """Overall system performance metrics"""
    total_adapters_loaded: int
    active_learning_cycles: int
    average_role_fidelity: float
    average_leadership_clarity: float
    average_conflict_index: float
    system_uptime_hours: float
    last_evaluation: Optional[datetime] = None
    last_learning_cycle: Optional[datetime] = None
    pending_upgrades: int = 0


class AdapterOrchestrator:
    """
    Main orchestrator for the Business Infinity LoRA adapter system.
    
    Responsibilities:
    - Initialize and manage all adapter-related components
    - Coordinate self-learning cycles across roles
    - Monitor system performance and trigger upgrades when needed
    - Provide unified API for boardroom agent integration
    - Handle system maintenance and monitoring
    """
    
    def __init__(self, config_path: str = None, data_dir: str = None):
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), "adapter_configs.json")
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "data")
        
        # Ensure data directory structure
        os.makedirs(self.data_dir, exist_ok=True)
        for subdir in ["learning", "evaluation", "upgrades", "backups"]:
            os.makedirs(os.path.join(self.data_dir, subdir), exist_ok=True)
        
        # System state
        self.status = SystemStatus.INITIALIZING
        self.initialization_time = datetime.now()
        
        # Core components
        self.lora_manager: Optional[LoRAAdapterManager] = None
        self.learning_system: Optional[SelfLearningSystem] = None
        self.upgrade_manager: Optional[ModelUpgradeManager] = None
        self.evaluation_harness: Optional[EvaluationHarness] = None
        
        # Configuration
        self.config: Dict[str, Any] = {}
        
        logger.info(f"Adapter Orchestrator initialized with config: {self.config_path}")
    
    async def initialize(self):
        """Initialize all adapter system components"""
        try:
            logger.info("Initializing Adapter Orchestrator...")
            self.status = SystemStatus.INITIALIZING
            
            # Load configuration
            await self._load_configuration()
            
            # Initialize LoRA Adapter Manager
            model_config = ModelConfig(
                model_name=self.config.get("model_config", {}).get("base_model", "meta-llama/Llama-3.1-8B-Instruct"),
                quantization=self.config.get("model_config", {}).get("quantization", "QLoRA-4bit"),
                device=self.config.get("model_config", {}).get("device", "auto")
            )
            
            self.lora_manager = LoRAAdapterManager(
                config_path=self.config_path,
                model_config=model_config
            )
            await self.lora_manager.initialize_model()
            
            # Initialize Self-Learning System
            learning_data_dir = os.path.join(self.data_dir, "learning")
            self.learning_system = SelfLearningSystem(
                data_dir=learning_data_dir,
                lora_manager=self.lora_manager
            )
            
            # Initialize Model Upgrade Manager
            upgrade_data_dir = os.path.join(self.data_dir, "upgrades")
            self.upgrade_manager = ModelUpgradeManager(
                lora_manager=self.lora_manager,
                self_learning_system=self.learning_system,
                data_dir=upgrade_data_dir
            )
            
            # Initialize Evaluation Harness
            eval_data_dir = os.path.join(self.data_dir, "evaluation")
            self.evaluation_harness = EvaluationHarness(data_dir=eval_data_dir)
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.status = SystemStatus.READY
            logger.info("Adapter Orchestrator initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize Adapter Orchestrator: {e}")
            self.status = SystemStatus.ERROR
            raise
    
    async def _load_configuration(self):
        """Load adapter system configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info("Loaded adapter configuration")
            else:
                logger.warning(f"Config file not found: {self.config_path}")
                self.config = {}
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = {}
    
    async def _start_background_tasks(self):
        """Start background monitoring and learning tasks"""
        
        # Start periodic self-learning cycles
        if self.config.get("self_learning", {}).get("enabled", True):
            cycle_hours = self.config.get("self_learning", {}).get("cycle_frequency_hours", 24)
            asyncio.create_task(self._periodic_learning_cycles(cycle_hours))
            logger.info(f"Started periodic learning cycles (every {cycle_hours} hours)")
        
        # Start system monitoring
        asyncio.create_task(self._system_monitoring())
        logger.info("Started system monitoring")
    
    async def _periodic_learning_cycles(self, cycle_hours: int):
        """Run periodic self-learning cycles for all roles"""
        while True:
            try:
                if self.status == SystemStatus.READY:
                    logger.info("Starting periodic learning cycle for all roles")
                    await self.run_learning_cycle_all_roles()
                
                # Wait for next cycle
                await asyncio.sleep(cycle_hours * 3600)  # Convert hours to seconds
                
            except Exception as e:
                logger.error(f"Error in periodic learning cycle: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    async def _system_monitoring(self):
        """Monitor system health and performance"""
        while True:
            try:
                # Check for upgrade conditions every 6 hours
                if self.upgrade_manager and self.status == SystemStatus.READY:
                    upgrade_conditions = await self.upgrade_manager.evaluate_upgrade_conditions()
                    
                    # Check if any role meets upgrade criteria
                    upgrade_recommended = any(
                        sum([
                            condition.reasoning_depth_capped,
                            condition.cross_role_voice_blur,
                            condition.leadership_tone_lacks_gravitas,
                            condition.evaluation_metrics_plateaued
                        ]) >= 2
                        for condition in upgrade_conditions.values()
                    )
                    
                    if upgrade_recommended:
                        logger.info("Upgrade conditions met - consider starting model upgrade")
                        # Note: Actual upgrade would be triggered manually or through API
                
                await asyncio.sleep(6 * 3600)  # Check every 6 hours
                
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    # Public API Methods
    
    async def generate_agent_response(self, role: str, prompt: str, 
                                    max_length: int = 512) -> Dict[str, Any]:
        """
        Generate response from a boardroom agent using LoRA adapters.
        
        Args:
            role: Agent role (cfo, cmo, coo, cto, founder, investor)
            prompt: Input prompt for the agent
            max_length: Maximum response length
            
        Returns:
            Generated response with metadata
        """
        if not self.lora_manager:
            return {"error": "LoRA manager not initialized"}
        
        try:
            boardroom_role = BoardroomRole(role)
            response = await self.lora_manager.generate_response(
                role=boardroom_role,
                prompt=prompt,
                max_length=max_length
            )
            
            return {
                "success": True,
                "role": role,
                "response": response,
                "adapter_info": await self.lora_manager.get_adapter_metrics(f"domain_{role}"),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate response for {role}: {e}")
            return {"error": f"Failed to generate response: {str(e)}"}
    
    async def evaluate_response(self, role: str, response_text: str, 
                              scenario_id: str = None) -> Dict[str, Any]:
        """
        Evaluate an agent response using the evaluation harness.
        
        Args:
            role: Agent role
            response_text: Response to evaluate
            scenario_id: Optional evaluation scenario ID
            
        Returns:
            Evaluation results
        """
        if not self.evaluation_harness:
            return {"error": "Evaluation harness not initialized"}
        
        try:
            # Use default scenario if none provided
            if not scenario_id:
                scenarios = list(self.evaluation_harness.evaluation_scenarios.keys())
                scenario_id = scenarios[0] if scenarios else None
                
            if not scenario_id:
                return {"error": "No evaluation scenarios available"}
            
            result = await self.evaluation_harness.evaluate_response(
                response_text=response_text,
                agent_role=role,
                scenario_id=scenario_id
            )
            
            return {
                "success": True,
                "evaluation_result": {
                    "overall_score": result.overall_score,
                    "role_fidelity": result.role_fidelity.overall_score,
                    "leadership_clarity": result.leadership_clarity.overall_score,
                    "conflict_index": result.conflict_index.overall_score,
                    "guardrail_compliance": result.guardrail_compliance.overall_score
                },
                "response_id": result.response_id,
                "scenario_id": result.scenario_id
            }
            
        except Exception as e:
            logger.error(f"Failed to evaluate response: {e}")
            return {"error": f"Evaluation failed: {str(e)}"}
    
    async def run_learning_cycle(self, role: str) -> Dict[str, Any]:
        """
        Run a self-learning cycle for a specific role.
        
        Args:
            role: Agent role to improve
            
        Returns:
            Learning cycle results
        """
        if not self.learning_system:
            return {"error": "Learning system not initialized"}
        
        try:
            self.status = SystemStatus.LEARNING
            
            logger.info(f"Starting learning cycle for {role}")
            result = await self.learning_system.run_learning_cycle(role)
            
            self.status = SystemStatus.READY
            return {"success": True, "learning_results": result}
            
        except Exception as e:
            logger.error(f"Learning cycle failed for {role}: {e}")
            self.status = SystemStatus.ERROR
            return {"error": f"Learning cycle failed: {str(e)}"}
    
    async def run_learning_cycle_all_roles(self) -> Dict[str, Any]:
        """Run self-learning cycles for all boardroom roles"""
        roles = ["cfo", "cmo", "coo", "cto", "founder", "investor"]
        results = {}
        
        logger.info("Starting learning cycles for all roles")
        
        for role in roles:
            result = await self.run_learning_cycle(role)
            results[role] = result
            
            # Small delay between roles to prevent system overload
            await asyncio.sleep(1)
        
        return {
            "success": True,
            "role_results": results,
            "total_roles": len(roles),
            "completed_at": datetime.now().isoformat()
        }
    
    async def start_model_upgrade(self, preserve_learning: bool = True,
                                enable_distillation: bool = True) -> Dict[str, Any]:
        """
        Start model upgrade from 8B to 13B.
        
        Args:
            preserve_learning: Preserve self-learning datasets
            enable_distillation: Use 8B model for distillation
            
        Returns:
            Upgrade job information
        """
        if not self.upgrade_manager:
            return {"error": "Upgrade manager not initialized"}
        
        try:
            self.status = SystemStatus.UPGRADING
            
            job_id = await self.upgrade_manager.start_upgrade(
                preserve_learning=preserve_learning,
                enable_distillation=enable_distillation
            )
            
            return {
                "success": True,
                "upgrade_job_id": job_id,
                "status": "started",
                "started_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to start model upgrade: {e}")
            self.status = SystemStatus.ERROR
            return {"error": f"Upgrade failed to start: {str(e)}"}
    
    async def get_upgrade_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a model upgrade job"""
        if not self.upgrade_manager:
            return {"error": "Upgrade manager not initialized"}
        
        return await self.upgrade_manager.get_upgrade_status(job_id)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status and metrics"""
        try:
            metrics = await self._calculate_system_metrics()
            
            return {
                "status": self.status.value,
                "uptime_hours": (datetime.now() - self.initialization_time).total_seconds() / 3600,
                "components": {
                    "lora_manager": "initialized" if self.lora_manager else "not_initialized",
                    "learning_system": "initialized" if self.learning_system else "not_initialized", 
                    "upgrade_manager": "initialized" if self.upgrade_manager else "not_initialized",
                    "evaluation_harness": "initialized" if self.evaluation_harness else "not_initialized"
                },
                "metrics": metrics,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {"error": f"Status check failed: {str(e)}"}
    
    async def get_learning_progress(self, role: str = None) -> Dict[str, Any]:
        """Get learning progress for role(s)"""
        if not self.learning_system:
            return {"error": "Learning system not initialized"}
        
        return await self.learning_system.get_learning_progress(role)
    
    async def get_performance_trends(self, role: str = None, days: int = 30) -> Dict[str, Any]:
        """Get performance trends over time"""
        if not self.evaluation_harness:
            return {"error": "Evaluation harness not initialized"}
        
        return await self.evaluation_harness.get_performance_trends(role, days)
    
    async def list_adapters(self) -> Dict[str, Any]:
        """List all available LoRA adapters"""
        if not self.lora_manager:
            return {"error": "LoRA manager not initialized"}
        
        return await self.lora_manager.list_all_adapters()
    
    async def _calculate_system_metrics(self) -> SystemMetrics:
        """Calculate overall system performance metrics"""
        try:
            # Get adapter info
            adapters_info = await self.lora_manager.list_all_adapters() if self.lora_manager else {}
            total_adapters = adapters_info.get("total_adapters", 0)
            
            # Get learning progress
            learning_progress = await self.learning_system.get_learning_progress() if self.learning_system else {}
            
            # Calculate averages across all roles
            roles_data = learning_progress.get("roles", {})
            if roles_data:
                role_fidelity_scores = [
                    role_data.get("metrics", {}).get("role_fidelity_score", 0)
                    for role_data in roles_data.values()
                    if isinstance(role_data.get("metrics"), dict)
                ]
                
                leadership_scores = [
                    role_data.get("metrics", {}).get("leadership_clarity_score", 0)
                    for role_data in roles_data.values()
                    if isinstance(role_data.get("metrics"), dict)
                ]
                
                avg_role_fidelity = sum(role_fidelity_scores) / len(role_fidelity_scores) if role_fidelity_scores else 0
                avg_leadership = sum(leadership_scores) / len(leadership_scores) if leadership_scores else 0
                
                active_cycles = sum(
                    role_data.get("dataset_info", {}).get("learning_cycles", 0)
                    for role_data in roles_data.values()
                    if isinstance(role_data.get("dataset_info"), dict)
                )
            else:
                avg_role_fidelity = 0
                avg_leadership = 0
                active_cycles = 0
            
            # Get pending upgrades
            pending_upgrades = 0
            if self.upgrade_manager:
                upgrades = await self.upgrade_manager.list_upgrades()
                pending_upgrades = upgrades.get("total_active", 0)
            
            uptime_hours = (datetime.now() - self.initialization_time).total_seconds() / 3600
            
            return SystemMetrics(
                total_adapters_loaded=total_adapters,
                active_learning_cycles=active_cycles,
                average_role_fidelity=avg_role_fidelity,
                average_leadership_clarity=avg_leadership,
                average_conflict_index=0.3,  # Mock value - would calculate from actual evaluations
                system_uptime_hours=uptime_hours,
                last_evaluation=datetime.now(),  # Mock - would track actual evaluations
                last_learning_cycle=datetime.now(),  # Mock - would track actual cycles
                pending_upgrades=pending_upgrades
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate system metrics: {e}")
            return SystemMetrics(
                total_adapters_loaded=0,
                active_learning_cycles=0,
                average_role_fidelity=0,
                average_leadership_clarity=0,
                average_conflict_index=0,
                system_uptime_hours=0
            )


# Global instance for easy access
adapter_orchestrator = AdapterOrchestrator()


# Convenience functions for external use
async def initialize_adapter_system():
    """Initialize the adapter system"""
    await adapter_orchestrator.initialize()
    return adapter_orchestrator


async def generate_boardroom_response(role: str, prompt: str, max_length: int = 512):
    """Generate response from boardroom agent"""
    return await adapter_orchestrator.generate_agent_response(role, prompt, max_length)


async def evaluate_boardroom_response(role: str, response_text: str, scenario_id: str = None):
    """Evaluate boardroom agent response"""
    return await adapter_orchestrator.evaluate_response(role, response_text, scenario_id)


async def start_learning_cycle(role: str = None):
    """Start learning cycle for role or all roles"""
    if role:
        return await adapter_orchestrator.run_learning_cycle(role)
    else:
        return await adapter_orchestrator.run_learning_cycle_all_roles()


async def get_system_status():
    """Get overall adapter system status"""
    return await adapter_orchestrator.get_system_status()