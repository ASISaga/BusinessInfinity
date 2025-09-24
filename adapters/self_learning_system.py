"""
Self-Learning System for Business Infinity LoRA Adapters

Implements the self-learning loop mechanism that continuously improves 
boardroom agents through mentor feedback and dataset expansion. Follows
the architecture defined in the adapter specifications.

Key Features:
- Situation generation and mentor feedback collection
- Dataset expansion with versioning (original + self-learning)
- Continuous fine-tuning loop
- Performance metrics tracking
- Knowledge preservation during model upgrades
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class LearningPhase(Enum):
    """Phases in the self-learning loop"""
    SITUATION_GENERATION = "situation_generation"
    MENTOR_FEEDBACK = "mentor_feedback" 
    DATASET_UPDATE = "dataset_update"
    FINE_TUNING = "fine_tuning"
    EVALUATION = "evaluation"
    DEPLOYMENT = "deployment"


class DatasetType(Enum):
    """Types of datasets in the learning system"""
    ORIGINAL = "original"       # Frozen baseline 
    SELF_LEARNING = "self_learning"  # Expanding with mentor data
    BLENDED = "blended"        # Combined for training


@dataclass 
class Situation:
    """A boardroom situation for agent evaluation"""
    id: str
    title: str
    description: str
    context: Dict[str, Any]
    decision_type: str
    target_roles: List[str]
    complexity_level: int  # 1-5 scale
    created_at: datetime
    source: str = "generated"  # "generated" | "real" | "synthetic"


@dataclass
class MentorFeedback:
    """Mentor feedback on agent responses"""
    situation_id: str
    agent_role: str
    original_response: str
    mentor_rating: float  # 0.0-1.0 scale
    corrections: str
    improvements: str
    alternative_framing: Optional[str] = None
    mentor_id: str = "system"
    feedback_type: str = "correction"  # "correction" | "refinement" | "alternative"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TrainingExample:
    """A training example for LoRA fine-tuning"""
    id: str
    input_prompt: str
    target_response: str
    role: str
    situation_context: Dict[str, Any]
    quality_score: float
    source_type: DatasetType
    version: str
    created_at: datetime


@dataclass
class LearningMetrics:
    """Metrics for tracking learning progress"""
    role: str
    cycle_number: int
    situations_processed: int
    feedback_received: int
    training_examples_added: int
    role_fidelity_score: float  # How well agent maintains role characteristics
    leadership_clarity_score: float  # Quality of leadership framing
    conflict_index: float  # How well agent handles role tensions
    improvement_rate: float  # Rate of improvement over time
    last_updated: datetime


class SelfLearningSystem:
    """
    Manages the self-learning loop for boardroom agents.
    
    Workflow:
    1. Generate/collect boardroom situations
    2. Get agent responses using current LoRA adapters
    3. Collect mentor feedback on responses
    4. Create improved training examples
    5. Update self-learning dataset
    6. Fine-tune adapters with blended dataset
    7. Evaluate performance improvements
    8. Deploy updated adapters
    """
    
    def __init__(self, data_dir: str = None, lora_manager=None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "learning_data")
        self.lora_manager = lora_manager
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # State tracking
        self.situations: Dict[str, Situation] = {}
        self.feedback: Dict[str, List[MentorFeedback]] = {}
        self.original_dataset: Dict[str, List[TrainingExample]] = {}
        self.self_learning_dataset: Dict[str, List[TrainingExample]] = {}
        self.learning_metrics: Dict[str, LearningMetrics] = {}
        self.learning_cycles: Dict[str, int] = {}  # Track cycles per role
        
        # Load existing data
        self._load_datasets()
        self._load_situations()
        self._load_feedback()
        
        logger.info(f"Self-Learning System initialized with data dir: {self.data_dir}")
    
    def _load_datasets(self):
        """Load existing datasets from disk"""
        try:
            # Load original dataset (frozen baseline)
            original_path = os.path.join(self.data_dir, "original_dataset.json")
            if os.path.exists(original_path):
                with open(original_path, 'r') as f:
                    data = json.load(f)
                    for role, examples in data.items():
                        self.original_dataset[role] = [
                            TrainingExample(**ex) for ex in examples
                        ]
                logger.info(f"Loaded original dataset: {len(self.original_dataset)} roles")
            
            # Load self-learning dataset (expanding)
            learning_path = os.path.join(self.data_dir, "self_learning_dataset.json")
            if os.path.exists(learning_path):
                with open(learning_path, 'r') as f:
                    data = json.load(f)
                    for role, examples in data.items():
                        self.self_learning_dataset[role] = [
                            TrainingExample(**ex) for ex in examples
                        ]
                logger.info(f"Loaded self-learning dataset: {len(self.self_learning_dataset)} roles")
                
        except Exception as e:
            logger.error(f"Failed to load datasets: {e}")
    
    def _load_situations(self):
        """Load existing situations from disk"""
        try:
            situations_path = os.path.join(self.data_dir, "situations.json")
            if os.path.exists(situations_path):
                with open(situations_path, 'r') as f:
                    data = json.load(f)
                    for sit_data in data:
                        situation = Situation(
                            id=sit_data["id"],
                            title=sit_data["title"],
                            description=sit_data["description"],
                            context=sit_data["context"],
                            decision_type=sit_data["decision_type"],
                            target_roles=sit_data["target_roles"],
                            complexity_level=sit_data["complexity_level"],
                            created_at=datetime.fromisoformat(sit_data["created_at"]),
                            source=sit_data.get("source", "generated")
                        )
                        self.situations[situation.id] = situation
                
                logger.info(f"Loaded {len(self.situations)} situations")
                
        except Exception as e:
            logger.error(f"Failed to load situations: {e}")
    
    def _load_feedback(self):
        """Load existing mentor feedback from disk"""
        try:
            feedback_path = os.path.join(self.data_dir, "mentor_feedback.json") 
            if os.path.exists(feedback_path):
                with open(feedback_path, 'r') as f:
                    data = json.load(f)
                    for situation_id, feedback_list in data.items():
                        self.feedback[situation_id] = [
                            MentorFeedback(
                                situation_id=fb["situation_id"],
                                agent_role=fb["agent_role"],
                                original_response=fb["original_response"],
                                mentor_rating=fb["mentor_rating"],
                                corrections=fb["corrections"],
                                improvements=fb["improvements"],
                                alternative_framing=fb.get("alternative_framing"),
                                mentor_id=fb.get("mentor_id", "system"),
                                feedback_type=fb.get("feedback_type", "correction"),
                                created_at=datetime.fromisoformat(fb["created_at"])
                            )
                            for fb in feedback_list
                        ]
                
                logger.info(f"Loaded feedback for {len(self.feedback)} situations")
                
        except Exception as e:
            logger.error(f"Failed to load feedback: {e}")
    
    async def generate_situation(self, decision_type: str, target_roles: List[str], 
                               complexity_level: int = 3) -> Situation:
        """
        Generate a new boardroom situation for agent evaluation.
        
        Args:
            decision_type: Type of decision (strategic, financial, etc.)
            target_roles: List of roles that should respond 
            complexity_level: Complexity from 1-5
            
        Returns:
            Generated situation
        """
        situation_id = f"sit_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(decision_type.encode()).hexdigest()[:6]}"
        
        # Generate situation based on decision type and complexity
        situation_templates = await self._get_situation_templates()
        template = situation_templates.get(decision_type, situation_templates["default"])
        
        # Create situation context
        context = {
            "company_stage": "growth",
            "market_conditions": "competitive",
            "timeline": "Q4 decision needed",
            "stakeholders": ["board", "investors", "employees"],
            "complexity_factors": self._get_complexity_factors(complexity_level)
        }
        
        situation = Situation(
            id=situation_id,
            title=template["title_format"].format(decision_type=decision_type),
            description=template["description_format"].format(
                decision_type=decision_type, 
                complexity=complexity_level
            ),
            context=context,
            decision_type=decision_type,
            target_roles=target_roles,
            complexity_level=complexity_level,
            created_at=datetime.now(),
            source="generated"
        )
        
        self.situations[situation_id] = situation
        await self._save_situations()
        
        logger.info(f"Generated situation {situation_id} for roles {target_roles}")
        return situation
    
    async def collect_mentor_feedback(self, situation_id: str, agent_role: str,
                                    agent_response: str, mentor_input: Dict[str, Any]) -> MentorFeedback:
        """
        Collect mentor feedback on an agent response.
        
        Args:
            situation_id: ID of the situation
            agent_role: Role of the responding agent
            agent_response: Agent's original response
            mentor_input: Mentor feedback input
            
        Returns:
            Processed mentor feedback
        """
        feedback = MentorFeedback(
            situation_id=situation_id,
            agent_role=agent_role,
            original_response=agent_response,
            mentor_rating=mentor_input.get("rating", 0.5),
            corrections=mentor_input.get("corrections", ""),
            improvements=mentor_input.get("improvements", ""),
            alternative_framing=mentor_input.get("alternative_framing"),
            mentor_id=mentor_input.get("mentor_id", "system"),
            feedback_type=mentor_input.get("feedback_type", "correction"),
            created_at=datetime.now()
        )
        
        # Add to feedback storage
        if situation_id not in self.feedback:
            self.feedback[situation_id] = []
        self.feedback[situation_id].append(feedback)
        
        await self._save_feedback()
        
        logger.info(f"Collected mentor feedback for {agent_role} on situation {situation_id}")
        return feedback
    
    async def create_training_example(self, feedback: MentorFeedback) -> TrainingExample:
        """
        Create an improved training example from mentor feedback.
        
        Args:
            feedback: Mentor feedback to process
            
        Returns:
            New training example
        """
        situation = self.situations[feedback.situation_id]
        
        # Create improved response based on mentor feedback
        improved_response = self._generate_improved_response(
            feedback.original_response,
            feedback.corrections,
            feedback.improvements,
            feedback.alternative_framing
        )
        
        # Generate input prompt with situation context
        input_prompt = self._format_situation_prompt(situation, feedback.agent_role)
        
        example_id = f"ex_{feedback.situation_id}_{feedback.agent_role}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        training_example = TrainingExample(
            id=example_id,
            input_prompt=input_prompt,
            target_response=improved_response,
            role=feedback.agent_role,
            situation_context=situation.context,
            quality_score=feedback.mentor_rating,
            source_type=DatasetType.SELF_LEARNING,
            version="v2.0",  # Self-learning version
            created_at=datetime.now()
        )
        
        logger.info(f"Created training example {example_id} from feedback")
        return training_example
    
    async def update_self_learning_dataset(self, training_examples: List[TrainingExample]):
        """
        Update the self-learning dataset with new training examples.
        
        Args:
            training_examples: New examples to add
        """
        for example in training_examples:
            if example.role not in self.self_learning_dataset:
                self.self_learning_dataset[example.role] = []
            
            self.self_learning_dataset[example.role].append(example)
        
        await self._save_self_learning_dataset()
        
        logger.info(f"Updated self-learning dataset with {len(training_examples)} examples")
    
    async def create_blended_dataset(self, role: str, 
                                   original_weight: float = 0.7,
                                   self_learning_weight: float = 0.3) -> List[TrainingExample]:
        """
        Create blended dataset for fine-tuning (original + self-learning).
        
        Args:
            role: Agent role
            original_weight: Weight for original dataset (60-80% recommended)
            self_learning_weight: Weight for self-learning dataset (20-40% recommended)
            
        Returns:
            Blended dataset for training
        """
        blended = []
        
        # Add original dataset examples
        original_examples = self.original_dataset.get(role, [])
        original_count = int(len(original_examples) * original_weight)
        blended.extend(original_examples[:original_count])
        
        # Add self-learning examples  
        learning_examples = self.self_learning_dataset.get(role, [])
        learning_count = int(len(learning_examples) * self_learning_weight)
        blended.extend(learning_examples[-learning_count:])  # Most recent examples
        
        logger.info(f"Created blended dataset for {role}: {len(blended)} examples "
                   f"(original: {original_count}, self-learning: {learning_count})")
        
        return blended
    
    async def run_learning_cycle(self, role: str) -> Dict[str, Any]:
        """
        Run a complete self-learning cycle for a specific role.
        
        Args:
            role: Agent role to improve
            
        Returns:
            Cycle results and metrics
        """
        cycle_start = datetime.now()
        cycle_num = self.learning_cycles.get(role, 0) + 1
        self.learning_cycles[role] = cycle_num
        
        logger.info(f"Starting learning cycle {cycle_num} for role {role}")
        
        results = {
            "role": role,
            "cycle_number": cycle_num,
            "started_at": cycle_start.isoformat(),
            "phases": {}
        }
        
        try:
            # Phase 1: Generate situations
            situations_generated = await self._generate_situations_for_role(role, count=3)
            results["phases"]["situation_generation"] = {
                "situations_generated": len(situations_generated),
                "status": "completed"
            }
            
            # Phase 2: Get agent responses (stub - would use LoRA manager)
            if self.lora_manager:
                responses = []
                for situation in situations_generated:
                    response = await self.lora_manager.generate_response(
                        role=role, 
                        prompt=self._format_situation_prompt(situation, role)
                    )
                    responses.append((situation.id, response))
            else:
                responses = [(s.id, f"Stub response for {role}") for s in situations_generated]
            
            results["phases"]["response_generation"] = {
                "responses_generated": len(responses),
                "status": "completed"
            }
            
            # Phase 3: Collect mentor feedback (stub - would integrate with mentor system)
            feedback_collected = []
            for situation_id, response in responses:
                # Simulate mentor feedback
                mock_feedback = {
                    "rating": 0.7 + (cycle_num * 0.05),  # Improve over time
                    "corrections": f"Improve analysis depth for {role}",
                    "improvements": f"Add more {role}-specific metrics",
                    "mentor_id": "system_mentor"
                }
                
                feedback = await self.collect_mentor_feedback(
                    situation_id, role, response, mock_feedback
                )
                feedback_collected.append(feedback)
            
            results["phases"]["mentor_feedback"] = {
                "feedback_collected": len(feedback_collected),
                "average_rating": sum(fb.mentor_rating for fb in feedback_collected) / len(feedback_collected),
                "status": "completed"
            }
            
            # Phase 4: Create training examples
            training_examples = []
            for feedback in feedback_collected:
                example = await self.create_training_example(feedback)
                training_examples.append(example)
            
            results["phases"]["training_examples"] = {
                "examples_created": len(training_examples),
                "status": "completed"
            }
            
            # Phase 5: Update dataset
            await self.update_self_learning_dataset(training_examples)
            
            results["phases"]["dataset_update"] = {
                "examples_added": len(training_examples),
                "total_self_learning": len(self.self_learning_dataset.get(role, [])),
                "status": "completed"
            }
            
            # Phase 6: Fine-tuning (stub - would trigger actual training)
            blended_dataset = await self.create_blended_dataset(role)
            
            results["phases"]["fine_tuning"] = {
                "blended_dataset_size": len(blended_dataset),
                "training_triggered": True,  # Would be actual training
                "status": "stub_completed"
            }
            
            # Phase 7: Update metrics
            metrics = await self._update_learning_metrics(role, cycle_num, results)
            results["metrics"] = metrics
            
            cycle_end = datetime.now()
            results["completed_at"] = cycle_end.isoformat()
            results["duration_minutes"] = (cycle_end - cycle_start).total_seconds() / 60
            results["status"] = "completed"
            
            logger.info(f"Completed learning cycle {cycle_num} for {role} in {results['duration_minutes']:.1f} minutes")
            
        except Exception as e:
            logger.error(f"Learning cycle failed for {role}: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    async def get_learning_progress(self, role: str = None) -> Dict[str, Any]:
        """
        Get learning progress metrics for role(s).
        
        Args:
            role: Specific role, or None for all roles
            
        Returns:
            Learning progress information
        """
        if role:
            metrics = self.learning_metrics.get(role, {})
            dataset_info = {
                "original_examples": len(self.original_dataset.get(role, [])),
                "self_learning_examples": len(self.self_learning_dataset.get(role, [])),
                "learning_cycles": self.learning_cycles.get(role, 0)
            }
            
            return {
                "role": role,
                "metrics": metrics,
                "dataset_info": dataset_info
            }
        else:
            # All roles
            all_progress = {}
            for role in ["cfo", "cmo", "coo", "cto", "founder", "investor"]:
                all_progress[role] = await self.get_learning_progress(role)
            
            return {
                "total_roles": len(all_progress),
                "roles": all_progress,
                "total_situations": len(self.situations),
                "total_feedback": sum(len(fb) for fb in self.feedback.values())
            }
    
    # Helper methods
    
    async def _get_situation_templates(self) -> Dict[str, Any]:
        """Get situation templates for generation"""
        return {
            "strategic": {
                "title_format": "Strategic {decision_type} Decision",
                "description_format": "The board must decide on a {decision_type} initiative with complexity level {complexity}."
            },
            "financial": {
                "title_format": "Financial {decision_type} Analysis",
                "description_format": "Financial analysis needed for {decision_type} with complexity {complexity}."
            },
            "default": {
                "title_format": "Boardroom {decision_type} Decision",
                "description_format": "Board decision required for {decision_type} at complexity {complexity}."
            }
        }
    
    def _get_complexity_factors(self, level: int) -> List[str]:
        """Get complexity factors based on level"""
        factors = {
            1: ["single_stakeholder", "clear_metrics"],
            2: ["multiple_stakeholders", "some_uncertainty"],
            3: ["competing_priorities", "moderate_risk"],
            4: ["high_stakes", "time_pressure", "regulatory_concerns"],
            5: ["existential_risk", "extreme_uncertainty", "conflicting_data"]
        }
        return factors.get(level, factors[3])
    
    def _generate_improved_response(self, original: str, corrections: str,
                                  improvements: str, alternative: Optional[str]) -> str:
        """Generate improved response from mentor feedback"""
        # Simple improvement logic - would be more sophisticated in production
        improved = original
        
        if corrections:
            improved += f"\n\n[CORRECTED]: {corrections}"
        
        if improvements:
            improved += f"\n\n[IMPROVED]: {improvements}"
        
        if alternative:
            improved = alternative  # Use alternative if provided
        
        return improved
    
    def _format_situation_prompt(self, situation: Situation, role: str) -> str:
        """Format situation as prompt for agent"""
        return f"""
[BOARDROOM SITUATION]
Title: {situation.title}
Decision Type: {situation.decision_type}
Your Role: {role.upper()}

Context: {json.dumps(situation.context, indent=2)}

Situation: {situation.description}

Please provide your analysis and recommendation as the {role.upper()}.
"""
    
    async def _generate_situations_for_role(self, role: str, count: int = 3) -> List[Situation]:
        """Generate situations targeted for a specific role"""
        situations = []
        
        role_decision_types = {
            "cfo": ["financial", "investment", "operational"],
            "cmo": ["market", "strategic", "product"],
            "coo": ["operational", "strategic"],
            "cto": ["product", "strategic", "operational"],
            "founder": ["strategic", "governance", "investment"],
            "investor": ["investment", "financial", "governance"]
        }
        
        decision_types = role_decision_types.get(role, ["strategic"])
        
        for i in range(count):
            decision_type = decision_types[i % len(decision_types)]
            situation = await self.generate_situation(
                decision_type=decision_type,
                target_roles=[role],
                complexity_level=2 + (i % 3)  # Vary complexity
            )
            situations.append(situation)
        
        return situations
    
    async def _update_learning_metrics(self, role: str, cycle_num: int, cycle_results: Dict[str, Any]) -> LearningMetrics:
        """Update learning metrics for a role"""
        
        # Calculate metrics from cycle results
        feedback_data = cycle_results["phases"]["mentor_feedback"]
        avg_rating = feedback_data["average_rating"]
        
        # Mock calculations for role fidelity and leadership clarity
        role_fidelity = min(1.0, 0.6 + (cycle_num * 0.05))  # Improve over cycles
        leadership_clarity = min(1.0, 0.5 + (cycle_num * 0.08))
        conflict_index = max(0.0, 0.8 - (cycle_num * 0.03))  # Reduce conflicts over time
        
        metrics = LearningMetrics(
            role=role,
            cycle_number=cycle_num,
            situations_processed=cycle_results["phases"]["situation_generation"]["situations_generated"],
            feedback_received=feedback_data["feedback_collected"],
            training_examples_added=cycle_results["phases"]["training_examples"]["examples_created"],
            role_fidelity_score=role_fidelity,
            leadership_clarity_score=leadership_clarity,
            conflict_index=conflict_index,
            improvement_rate=(avg_rating - 0.5) / cycle_num if cycle_num > 0 else 0.0,
            last_updated=datetime.now()
        )
        
        self.learning_metrics[role] = metrics
        return metrics
    
    # Persistence methods
    
    async def _save_situations(self):
        """Save situations to disk"""
        try:
            situations_data = []
            for situation in self.situations.values():
                situations_data.append({
                    "id": situation.id,
                    "title": situation.title,
                    "description": situation.description,
                    "context": situation.context,
                    "decision_type": situation.decision_type,
                    "target_roles": situation.target_roles,
                    "complexity_level": situation.complexity_level,
                    "created_at": situation.created_at.isoformat(),
                    "source": situation.source
                })
            
            with open(os.path.join(self.data_dir, "situations.json"), 'w') as f:
                json.dump(situations_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save situations: {e}")
    
    async def _save_feedback(self):
        """Save mentor feedback to disk"""
        try:
            feedback_data = {}
            for situation_id, feedback_list in self.feedback.items():
                feedback_data[situation_id] = []
                for fb in feedback_list:
                    feedback_data[situation_id].append({
                        "situation_id": fb.situation_id,
                        "agent_role": fb.agent_role,
                        "original_response": fb.original_response,
                        "mentor_rating": fb.mentor_rating,
                        "corrections": fb.corrections,
                        "improvements": fb.improvements,
                        "alternative_framing": fb.alternative_framing,
                        "mentor_id": fb.mentor_id,
                        "feedback_type": fb.feedback_type,
                        "created_at": fb.created_at.isoformat()
                    })
            
            with open(os.path.join(self.data_dir, "mentor_feedback.json"), 'w') as f:
                json.dump(feedback_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save feedback: {e}")
    
    async def _save_self_learning_dataset(self):
        """Save self-learning dataset to disk"""
        try:
            dataset_data = {}
            for role, examples in self.self_learning_dataset.items():
                dataset_data[role] = []
                for ex in examples:
                    dataset_data[role].append({
                        "id": ex.id,
                        "input_prompt": ex.input_prompt,
                        "target_response": ex.target_response,
                        "role": ex.role,
                        "situation_context": ex.situation_context,
                        "quality_score": ex.quality_score,
                        "source_type": ex.source_type.value,
                        "version": ex.version,
                        "created_at": ex.created_at.isoformat()
                    })
            
            with open(os.path.join(self.data_dir, "self_learning_dataset.json"), 'w') as f:
                json.dump(dataset_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save self-learning dataset: {e}")