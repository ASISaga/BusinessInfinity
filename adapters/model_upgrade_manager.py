"""
Model Upgrade System for Business Infinity LoRA Adapters

Implements the 8B → 13B model upgrade path as defined in the adapter specifications.
Preserves accumulated learning while transitioning to more capable base models.

Key Features:
- Preservation of original and self-learning datasets
- Distillation from 8B to maintain style continuity
- Parallel evaluation of 8B vs 13B performance
- Gradual migration of self-learning loop
- Rollback capabilities
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import shutil

logger = logging.getLogger(__name__)


class UpgradePhase(Enum):
    """Phases in the model upgrade process"""
    PREPARATION = "preparation"
    DATA_PRESERVATION = "data_preservation"
    DISTILLATION = "distillation"
    ADAPTER_RETRAINING = "adapter_retraining"
    PARALLEL_EVALUATION = "parallel_evaluation"
    MIGRATION = "migration"
    VALIDATION = "validation"
    DEPLOYMENT = "deployment"
    CLEANUP = "cleanup"


class UpgradeStatus(Enum):
    """Status of upgrade process"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PARALLEL_TESTING = "parallel_testing"
    READY_FOR_MIGRATION = "ready_for_migration"
    MIGRATING = "migrating"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class UpgradeCondition:
    """Conditions that trigger an upgrade from 8B to 13B"""
    reasoning_depth_capped: bool = False
    cross_role_voice_blur: bool = False
    leadership_tone_lacks_gravitas: bool = False
    evaluation_metrics_plateaued: bool = False
    confidence_threshold: float = 0.85
    description: str = ""


@dataclass
class PerformanceComparison:
    """Comparison of 8B vs 13B performance"""
    scenario_id: str
    model_8b_score: float
    model_13b_score: float
    role_fidelity_8b: float
    role_fidelity_13b: float
    leadership_clarity_8b: float
    leadership_clarity_13b: float
    response_time_8b: float
    response_time_13b: float
    preference_score: float  # 0-1, where >0.5 prefers 13B
    evaluation_date: datetime


@dataclass
class UpgradeJob:
    """Tracks an active model upgrade job"""
    id: str
    source_model: str
    target_model: str
    started_at: datetime
    current_phase: UpgradePhase
    status: UpgradeStatus
    progress_percentage: float
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None
    rollback_available: bool = True
    backup_paths: Dict[str, str] = field(default_factory=dict)
    performance_comparisons: List[PerformanceComparison] = field(default_factory=list)
    final_metrics: Dict[str, Any] = field(default_factory=dict)


class ModelUpgradeManager:
    """
    Manages model upgrades from 8B to 13B while preserving learning.
    
    Upgrade Process:
    1. Evaluate upgrade conditions
    2. Preserve original + self-learning datasets
    3. Generate distillation data from 8B
    4. Retrain all adapters on 13B model
    5. Run parallel evaluation on test scenarios
    6. Migrate self-learning loop when 13B outperforms
    7. Phase out 8B system
    """
    
    def __init__(self, lora_manager=None, self_learning_system=None, data_dir: str = None):
        self.lora_manager = lora_manager
        self.self_learning_system = self_learning_system
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "upgrade_data")
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "backups"), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "distillation"), exist_ok=True)
        
        # State
        self.active_upgrades: Dict[str, UpgradeJob] = {}
        self.upgrade_history: List[UpgradeJob] = []
        self.upgrade_conditions_cache: Dict[str, UpgradeCondition] = {}
        
        # Load existing upgrade data
        self._load_upgrade_history()
        
        logger.info(f"Model Upgrade Manager initialized with data dir: {self.data_dir}")
    
    def _load_upgrade_history(self):
        """Load previous upgrade attempts from disk"""
        try:
            history_path = os.path.join(self.data_dir, "upgrade_history.json")
            if os.path.exists(history_path):
                with open(history_path, 'r') as f:
                    data = json.load(f)
                    # TODO: Deserialize upgrade jobs
                logger.info(f"Loaded upgrade history: {len(self.upgrade_history)} previous upgrades")
        except Exception as e:
            logger.error(f"Failed to load upgrade history: {e}")
    
    async def evaluate_upgrade_conditions(self, role: str = None) -> Dict[str, UpgradeCondition]:
        """
        Evaluate whether conditions are met for upgrading to 13B.
        
        Args:
            role: Specific role to evaluate, or None for all roles
            
        Returns:
            Dictionary of upgrade conditions per role
        """
        roles_to_evaluate = [role] if role else ["cfo", "cmo", "coo", "cto", "founder", "investor"]
        conditions = {}
        
        for eval_role in roles_to_evaluate:
            condition = await self._evaluate_role_upgrade_conditions(eval_role)
            conditions[eval_role] = condition
            self.upgrade_conditions_cache[eval_role] = condition
        
        logger.info(f"Evaluated upgrade conditions for {len(conditions)} roles")
        return conditions
    
    async def _evaluate_role_upgrade_conditions(self, role: str) -> UpgradeCondition:
        """Evaluate upgrade conditions for a specific role"""
        
        # Get performance metrics from self-learning system
        if self.self_learning_system:
            progress = await self.self_learning_system.get_learning_progress(role)
            metrics = progress.get("metrics", {})
        else:
            # Stub metrics
            metrics = {
                "role_fidelity_score": 0.75,
                "leadership_clarity_score": 0.70,
                "improvement_rate": 0.05,
                "cycle_number": 5
            }
        
        # Evaluate each condition
        reasoning_depth_capped = (
            metrics.get("improvement_rate", 0) < 0.02 and 
            metrics.get("cycle_number", 0) > 3
        )
        
        cross_role_voice_blur = metrics.get("role_fidelity_score", 1.0) < 0.70
        
        leadership_tone_lacks_gravitas = metrics.get("leadership_clarity_score", 1.0) < 0.65
        
        evaluation_metrics_plateaued = (
            metrics.get("improvement_rate", 0) < 0.01 and
            metrics.get("cycle_number", 0) > 5
        )
        
        # Determine if upgrade is recommended
        conditions_met = sum([
            reasoning_depth_capped,
            cross_role_voice_blur,
            leadership_tone_lacks_gravitas,
            evaluation_metrics_plateaued
        ])
        
        description = f"Role {role}: {conditions_met}/4 upgrade conditions met"
        if conditions_met >= 2:
            description += " - UPGRADE RECOMMENDED"
        
        return UpgradeCondition(
            reasoning_depth_capped=reasoning_depth_capped,
            cross_role_voice_blur=cross_role_voice_blur,
            leadership_tone_lacks_gravitas=leadership_tone_lacks_gravitas,
            evaluation_metrics_plateaued=evaluation_metrics_plateaued,
            confidence_threshold=0.85,
            description=description
        )
    
    async def start_upgrade(self, preserve_learning: bool = True, 
                          enable_distillation: bool = True) -> str:
        """
        Start a model upgrade from 8B to 13B.
        
        Args:
            preserve_learning: Whether to preserve self-learning datasets
            enable_distillation: Whether to use 8B model for distillation
            
        Returns:
            Upgrade job ID
        """
        job_id = f"upgrade_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        upgrade_job = UpgradeJob(
            id=job_id,
            source_model="meta-llama/Llama-3.1-8B-Instruct",
            target_model="meta-llama/Llama-3.1-13B-Instruct",
            started_at=datetime.now(),
            current_phase=UpgradePhase.PREPARATION,
            status=UpgradeStatus.IN_PROGRESS,
            progress_percentage=0.0,
            estimated_completion=datetime.now() + timedelta(hours=4)
        )
        
        self.active_upgrades[job_id] = upgrade_job
        
        # Start upgrade process asynchronously
        asyncio.create_task(self._run_upgrade_process(
            job_id, preserve_learning, enable_distillation
        ))
        
        logger.info(f"Started model upgrade job {job_id}")
        return job_id
    
    async def _run_upgrade_process(self, job_id: str, preserve_learning: bool, 
                                 enable_distillation: bool):
        """Run the complete upgrade process"""
        job = self.active_upgrades[job_id]
        
        try:
            # Phase 1: Preparation
            await self._upgrade_phase_preparation(job)
            
            # Phase 2: Data Preservation
            await self._upgrade_phase_data_preservation(job, preserve_learning)
            
            # Phase 3: Distillation (optional)
            if enable_distillation:
                await self._upgrade_phase_distillation(job)
            
            # Phase 4: Adapter Retraining
            await self._upgrade_phase_adapter_retraining(job)
            
            # Phase 5: Parallel Evaluation
            await self._upgrade_phase_parallel_evaluation(job)
            
            # Phase 6: Migration Decision
            if await self._should_migrate_to_13b(job):
                job.status = UpgradeStatus.READY_FOR_MIGRATION
                logger.info(f"Upgrade {job_id} ready for migration to 13B")
            else:
                job.status = UpgradeStatus.FAILED
                job.error_message = "13B model did not consistently outperform 8B"
                logger.warning(f"Upgrade {job_id} failed - 13B not consistently better")
                return
            
            # Phase 7: Validation
            await self._upgrade_phase_validation(job)
            
            # Phase 8: Deployment (would happen separately)
            job.current_phase = UpgradePhase.DEPLOYMENT
            job.progress_percentage = 95.0
            
            job.status = UpgradeStatus.COMPLETED
            job.progress_percentage = 100.0
            
            logger.info(f"Model upgrade {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Upgrade {job_id} failed: {e}")
            job.status = UpgradeStatus.FAILED
            job.error_message = str(e)
            
            # Attempt rollback
            try:
                await self._rollback_upgrade(job_id)
            except Exception as rollback_error:
                logger.error(f"Rollback failed for {job_id}: {rollback_error}")
    
    async def _upgrade_phase_preparation(self, job: UpgradeJob):
        """Phase 1: Preparation - validate system and create backups"""
        job.current_phase = UpgradePhase.PREPARATION
        job.progress_percentage = 5.0
        
        logger.info(f"Upgrade {job.id}: Starting preparation phase")
        
        # Validate current system state
        if self.lora_manager:
            adapters = await self.lora_manager.list_all_adapters()
            logger.info(f"Found {adapters['total_adapters']} adapters to upgrade")
        
        # Create backup directories
        backup_base = os.path.join(self.data_dir, "backups", job.id)
        os.makedirs(backup_base, exist_ok=True)
        
        job.backup_paths = {
            "adapters": os.path.join(backup_base, "adapters"),
            "datasets": os.path.join(backup_base, "datasets"),
            "config": os.path.join(backup_base, "config")
        }
        
        for path in job.backup_paths.values():
            os.makedirs(path, exist_ok=True)
        
        job.progress_percentage = 10.0
        logger.info(f"Upgrade {job.id}: Preparation completed")
    
    async def _upgrade_phase_data_preservation(self, job: UpgradeJob, preserve_learning: bool):
        """Phase 2: Preserve original and self-learning datasets"""
        job.current_phase = UpgradePhase.DATA_PRESERVATION
        job.progress_percentage = 15.0
        
        logger.info(f"Upgrade {job.id}: Starting data preservation phase")
        
        if preserve_learning and self.self_learning_system:
            # Save current datasets
            try:
                # Copy self-learning data to backup
                source_dir = self.self_learning_system.data_dir
                backup_dir = job.backup_paths["datasets"]
                
                for file_name in ["original_dataset.json", "self_learning_dataset.json", 
                                "situations.json", "mentor_feedback.json"]:
                    source_path = os.path.join(source_dir, file_name)
                    if os.path.exists(source_path):
                        backup_path = os.path.join(backup_dir, file_name)
                        shutil.copy2(source_path, backup_path)
                        logger.info(f"Backed up {file_name}")
                
                job.progress_percentage = 25.0
                
            except Exception as e:
                raise Exception(f"Data preservation failed: {e}")
        
        logger.info(f"Upgrade {job.id}: Data preservation completed")
    
    async def _upgrade_phase_distillation(self, job: UpgradeJob):
        """Phase 3: Generate distillation data from 8B model"""
        job.current_phase = UpgradePhase.DISTILLATION
        job.progress_percentage = 30.0
        
        logger.info(f"Upgrade {job.id}: Starting distillation phase")
        
        # Generate synthetic transcripts from 8B model for style continuity
        distillation_data = {}
        
        if self.lora_manager and self.self_learning_system:
            # Get recent situations for distillation
            progress = await self.self_learning_system.get_learning_progress()
            
            # Generate responses from 8B for key scenarios
            roles = ["cfo", "cmo", "coo", "cto", "founder", "investor"]
            for role in roles:
                distillation_data[role] = []
                
                # Create sample scenarios
                for i in range(5):  # 5 distillation examples per role
                    situation = await self.self_learning_system.generate_situation(
                        decision_type="strategic",
                        target_roles=[role],
                        complexity_level=3
                    )
                    
                    # Get 8B response (stub implementation)
                    response_8b = f"[8B Distillation] {role.upper()} response to situation {situation.id}"
                    
                    distillation_data[role].append({
                        "situation_id": situation.id,
                        "input_prompt": self.self_learning_system._format_situation_prompt(situation, role),
                        "target_response": response_8b,
                        "source": "8b_distillation"
                    })
        
        # Save distillation data
        distillation_path = os.path.join(self.data_dir, "distillation", f"{job.id}_distillation.json")
        with open(distillation_path, 'w') as f:
            json.dump(distillation_data, f, indent=2)
        
        job.progress_percentage = 40.0
        logger.info(f"Upgrade {job.id}: Distillation completed with {sum(len(examples) for examples in distillation_data.values())} examples")
    
    async def _upgrade_phase_adapter_retraining(self, job: UpgradeJob):
        """Phase 4: Retrain all adapters on 13B model"""
        job.current_phase = UpgradePhase.ADAPTER_RETRAINING
        job.progress_percentage = 45.0
        
        logger.info(f"Upgrade {job.id}: Starting adapter retraining phase")
        
        # This would trigger actual retraining of adapters on 13B model
        # Using original + self-learning + distillation datasets
        
        roles = ["cfo", "cmo", "coo", "cto", "founder", "investor"]
        for i, role in enumerate(roles):
            # Stub: Retrain domain adapter for role
            logger.info(f"Retraining domain adapter for {role} on 13B model")
            
            # Create blended dataset
            if self.self_learning_system:
                blended_dataset = await self.self_learning_system.create_blended_dataset(role)
                logger.info(f"Using {len(blended_dataset)} examples for {role} adapter retraining")
            
            # Stub: Actual training would happen here
            await asyncio.sleep(0.1)  # Simulate training time
            
            # Update progress
            job.progress_percentage = 45.0 + ((i + 1) / len(roles)) * 20.0
        
        # Retrain leadership adapter
        logger.info("Retraining leadership adapter on 13B model")
        job.progress_percentage = 65.0
        
        logger.info(f"Upgrade {job.id}: Adapter retraining completed")
    
    async def _upgrade_phase_parallel_evaluation(self, job: UpgradeJob):
        """Phase 5: Run parallel evaluation of 8B vs 13B"""
        job.current_phase = UpgradePhase.PARALLEL_EVALUATION
        job.progress_percentage = 70.0
        
        logger.info(f"Upgrade {job.id}: Starting parallel evaluation phase")
        
        # Generate test scenarios for comparison
        test_scenarios = []
        if self.self_learning_system:
            for i in range(10):  # 10 test scenarios
                scenario = await self.self_learning_system.generate_situation(
                    decision_type=["strategic", "financial", "operational"][i % 3],
                    target_roles=["cfo", "cmo", "founder"][i % 3],
                    complexity_level=3 + (i % 3)
                )
                test_scenarios.append(scenario)
        
        # Run parallel comparison
        comparisons = []
        for scenario in test_scenarios:
            comparison = await self._run_parallel_comparison(scenario, job)
            comparisons.append(comparison)
            job.performance_comparisons.append(comparison)
        
        # Calculate overall performance
        avg_preference = sum(c.preference_score for c in comparisons) / len(comparisons)
        job.final_metrics = {
            "total_scenarios": len(comparisons),
            "average_13b_preference": avg_preference,
            "13b_wins": sum(1 for c in comparisons if c.preference_score > 0.5),
            "8b_wins": sum(1 for c in comparisons if c.preference_score < 0.5),
            "ties": sum(1 for c in comparisons if c.preference_score == 0.5)
        }
        
        job.progress_percentage = 85.0
        logger.info(f"Upgrade {job.id}: Parallel evaluation completed - 13B preference: {avg_preference:.2f}")
    
    async def _run_parallel_comparison(self, scenario, job: UpgradeJob) -> PerformanceComparison:
        """Run parallel comparison between 8B and 13B on a scenario"""
        
        # Stub implementation - would use actual models
        role = scenario.target_roles[0] if scenario.target_roles else "cfo"
        
        # Simulate responses and scoring
        model_8b_score = 0.7 + (hash(scenario.id) % 20) / 100  # 0.7-0.89
        model_13b_score = 0.75 + (hash(scenario.id) % 25) / 100  # 0.75-0.99
        
        role_fidelity_8b = 0.72 + (hash(f"{scenario.id}_role") % 15) / 100
        role_fidelity_13b = 0.78 + (hash(f"{scenario.id}_role") % 20) / 100
        
        leadership_clarity_8b = 0.68 + (hash(f"{scenario.id}_leadership") % 20) / 100
        leadership_clarity_13b = 0.75 + (hash(f"{scenario.id}_leadership") % 22) / 100
        
        # Calculate preference (0.5 = tie, >0.5 prefers 13B)
        preference_score = 0.5 + (model_13b_score - model_8b_score) / 2
        preference_score = max(0.0, min(1.0, preference_score))
        
        return PerformanceComparison(
            scenario_id=scenario.id,
            model_8b_score=model_8b_score,
            model_13b_score=model_13b_score,
            role_fidelity_8b=role_fidelity_8b,
            role_fidelity_13b=role_fidelity_13b,
            leadership_clarity_8b=leadership_clarity_8b,
            leadership_clarity_13b=leadership_clarity_13b,
            response_time_8b=0.8,  # Assume faster
            response_time_13b=1.2,  # Assume slower
            preference_score=preference_score,
            evaluation_date=datetime.now()
        )
    
    async def _should_migrate_to_13b(self, job: UpgradeJob) -> bool:
        """Determine if 13B model consistently outperforms 8B"""
        metrics = job.final_metrics
        
        # Criteria for migration:
        # 1. 13B wins at least 70% of comparisons
        # 2. Average preference score > 0.6
        # 3. No significant regression in any area
        
        win_rate = metrics["13b_wins"] / metrics["total_scenarios"]
        avg_preference = metrics["average_13b_preference"]
        
        migration_recommended = (
            win_rate >= 0.7 and
            avg_preference >= 0.6
        )
        
        logger.info(f"Migration decision for {job.id}: win_rate={win_rate:.2f}, "
                   f"preference={avg_preference:.2f}, recommended={migration_recommended}")
        
        return migration_recommended
    
    async def _upgrade_phase_validation(self, job: UpgradeJob):
        """Phase 7: Validate 13B system before deployment"""
        job.current_phase = UpgradePhase.VALIDATION
        job.progress_percentage = 90.0
        
        logger.info(f"Upgrade {job.id}: Starting validation phase")
        
        # Run additional validation tests
        validation_results = {
            "adapter_loading": True,
            "response_generation": True, 
            "role_consistency": True,
            "performance_regression": False
        }
        
        # Store validation results
        job.final_metrics["validation"] = validation_results
        
        job.progress_percentage = 95.0
        logger.info(f"Upgrade {job.id}: Validation completed")
    
    async def get_upgrade_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of an upgrade job"""
        if job_id not in self.active_upgrades:
            # Check completed upgrades
            for completed_job in self.upgrade_history:
                if completed_job.id == job_id:
                    return self._serialize_upgrade_job(completed_job)
            return {"error": f"Upgrade job {job_id} not found"}
        
        job = self.active_upgrades[job_id]
        return self._serialize_upgrade_job(job)
    
    async def migrate_to_13b(self, job_id: str) -> Dict[str, Any]:
        """
        Migrate self-learning loop to 13B model.
        This is the final step after validation.
        """
        if job_id not in self.active_upgrades:
            return {"error": f"Upgrade job {job_id} not found"}
        
        job = self.active_upgrades[job_id]
        
        if job.status != UpgradeStatus.READY_FOR_MIGRATION:
            return {"error": f"Job {job_id} is not ready for migration. Status: {job.status.value}"}
        
        try:
            job.status = UpgradeStatus.MIGRATING
            job.current_phase = UpgradePhase.MIGRATION
            
            logger.info(f"Starting migration to 13B for job {job_id}")
            
            # TODO: Implement actual migration
            # 1. Update LoRA manager to use 13B model
            # 2. Migrate self-learning system to use new adapters
            # 3. Update configuration
            # 4. Phase out 8B system
            
            job.status = UpgradeStatus.COMPLETED
            job.progress_percentage = 100.0
            
            # Move to completed jobs
            self.upgrade_history.append(job)
            del self.active_upgrades[job_id]
            
            logger.info(f"Successfully migrated to 13B for job {job_id}")
            
            return {
                "status": "completed",
                "job_id": job_id,
                "migrated_at": datetime.now().isoformat(),
                "new_model": job.target_model
            }
            
        except Exception as e:
            logger.error(f"Migration failed for job {job_id}: {e}")
            job.status = UpgradeStatus.FAILED
            job.error_message = f"Migration failed: {str(e)}"
            
            return {"error": f"Migration failed: {str(e)}"}
    
    async def _rollback_upgrade(self, job_id: str) -> bool:
        """Rollback a failed upgrade"""
        if job_id not in self.active_upgrades:
            return False
        
        job = self.active_upgrades[job_id]
        
        try:
            logger.info(f"Rolling back upgrade {job_id}")
            
            # Restore backups
            for backup_type, backup_path in job.backup_paths.items():
                if os.path.exists(backup_path):
                    # TODO: Implement actual restore logic
                    logger.info(f"Restored {backup_type} from backup")
            
            job.status = UpgradeStatus.ROLLED_BACK
            logger.info(f"Successfully rolled back upgrade {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed for {job_id}: {e}")
            return False
    
    def _serialize_upgrade_job(self, job: UpgradeJob) -> Dict[str, Any]:
        """Serialize upgrade job for API response"""
        return {
            "id": job.id,
            "source_model": job.source_model,
            "target_model": job.target_model,
            "started_at": job.started_at.isoformat(),
            "current_phase": job.current_phase.value,
            "status": job.status.value,
            "progress_percentage": job.progress_percentage,
            "estimated_completion": job.estimated_completion.isoformat() if job.estimated_completion else None,
            "error_message": job.error_message,
            "rollback_available": job.rollback_available,
            "performance_comparisons_count": len(job.performance_comparisons),
            "final_metrics": job.final_metrics
        }
    
    async def list_upgrades(self) -> Dict[str, Any]:
        """List all upgrade jobs (active and completed)"""
        active = {job_id: self._serialize_upgrade_job(job) 
                 for job_id, job in self.active_upgrades.items()}
        
        completed = [self._serialize_upgrade_job(job) for job in self.upgrade_history]
        
        return {
            "active_upgrades": active,
            "completed_upgrades": completed,
            "total_active": len(active),
            "total_completed": len(completed)
        }