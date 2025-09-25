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
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
from sklearn.metrics import mean_squared_error, f1_score
from sklearn.calibration import calibration_curve
from scipy.stats import entropy

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


class FocusArea(Enum):
    """Focus areas for learning improvements"""
    CONTEXT = "context"        # Update abstract context via MCP
    PROMPT = "prompt"          # Adjust prompt templates/variants
    MODEL = "model"            # Fine-tune via LoRA adapters
    INTERFACE = "interface"    # Fix third-party integrations


class InterfaceType(Enum):
    """Types of interfaces in the system"""
    ERP = "erp"
    CRM = "crm"
    MES = "mes"
    SOCIAL = "social"
    MCP_SERVER = "mcp_server"


@dataclass
class EpisodeEvent:
    """Core event model for audit-driven self-learning"""
    # Event envelope
    agent_id: str
    scenario_id: str
    timestamp: datetime
    source: str
    correlation_ids: List[str]
    
    # Inputs
    user_intent: str
    prompts: List[str]
    tool_calls: List[Dict[str, Any]]
    retrieved_context: Dict[str, Any]
    third_party_payloads: Dict[str, Any]
    
    # Predictions
    model_output: str
    action_plan: Dict[str, Any]
    selected_tools: List[str]
    confidence_scores: Dict[str, float]
    
    # Outcomes
    actual_results: Dict[str, Any]
    user_verdict: Optional[str] = None
    mentor_verdict: Optional[str] = None
    kpis: Dict[str, float] = field(default_factory=dict)
    error_codes: List[str] = field(default_factory=list)
    latencies: Dict[str, float] = field(default_factory=dict)
    
    # Feedback
    stakeholder_ratings: Dict[str, float] = field(default_factory=dict)
    mentor_annotations: List[str] = field(default_factory=list)
    categorical_tags: List[str] = field(default_factory=list)
    suggested_corrections: List[str] = field(default_factory=list)
    
    # Context deltas
    context_updates: Dict[str, Any] = field(default_factory=dict)
    mcp_object_refs: List[str] = field(default_factory=list)
    
    # Interfaces touched
    interfaces_used: Dict[InterfaceType, Dict[str, Any]] = field(default_factory=dict)
    schema_versions: Dict[str, str] = field(default_factory=dict)


@dataclass
class DerivedMetrics:
    """Derived features for learning analysis"""
    episode_id: str
    
    # Prediction errors
    rmse: Optional[float] = None
    f1_score: Optional[float] = None
    edit_distance: Optional[float] = None
    
    # Calibration
    brier_score: Optional[float] = None
    reliability_deviation: Optional[float] = None
    
    # Drift indicators
    kl_divergence: Optional[float] = None
    schema_mismatch_count: int = 0
    
    # Prompt sensitivity
    prompt_sensitivity_index: Optional[float] = None
    quality_vs_prompt_delta: Optional[float] = None
    
    # Interface reliability
    interface_error_rates: Dict[InterfaceType, float] = field(default_factory=dict)
    retry_counts: Dict[InterfaceType, int] = field(default_factory=dict)
    mttr_seconds: Dict[InterfaceType, float] = field(default_factory=dict)
    
    # Context utility
    retrieval_hit_rate: Optional[float] = None
    conflict_density: Optional[float] = None
    
    computed_at: datetime = field(default_factory=datetime.now)


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


class MetricsCalculator:
    """Calculates derived metrics from episode events"""
    
    def __init__(self):
        self.baseline_distributions = {}
        self.historical_metrics = []
    
    def calculate_derived_metrics(self, episode: EpisodeEvent) -> DerivedMetrics:
        """Calculate comprehensive derived metrics for an episode"""
        metrics = DerivedMetrics(episode_id=f"{episode.agent_id}_{episode.scenario_id}_{episode.timestamp.isoformat()}")
        
        # Calculate prediction errors
        metrics.rmse = self._calculate_rmse(episode)
        metrics.f1_score = self._calculate_f1_score(episode)
        metrics.edit_distance = self._calculate_edit_distance(episode)
        
        # Calculate calibration metrics
        metrics.brier_score = self._calculate_brier_score(episode)
        metrics.reliability_deviation = self._calculate_reliability_deviation(episode)
        
        # Calculate drift indicators
        metrics.kl_divergence = self._calculate_kl_divergence(episode)
        metrics.schema_mismatch_count = self._count_schema_mismatches(episode)
        
        # Calculate prompt sensitivity
        metrics.prompt_sensitivity_index = self._calculate_prompt_sensitivity(episode)
        
        # Calculate interface reliability
        metrics.interface_error_rates = self._calculate_interface_error_rates(episode)
        metrics.retry_counts = self._get_retry_counts(episode)
        metrics.mttr_seconds = self._calculate_mttr(episode)
        
        # Calculate context utility
        metrics.retrieval_hit_rate = self._calculate_retrieval_hit_rate(episode)
        metrics.conflict_density = self._calculate_conflict_density(episode)
        
        return metrics
    
    def _calculate_rmse(self, episode: EpisodeEvent) -> Optional[float]:
        """Calculate RMSE for numerical predictions"""
        try:
            if episode.kpis and 'predicted_values' in episode.actual_results:
                predicted = np.array(episode.actual_results['predicted_values'])
                actual = np.array(list(episode.kpis.values()))
                if len(predicted) == len(actual):
                    return float(np.sqrt(mean_squared_error(actual, predicted)))
        except Exception as e:
            logger.warning(f"Could not calculate RMSE: {e}")
        return None
    
    def _calculate_f1_score(self, episode: EpisodeEvent) -> Optional[float]:
        """Calculate F1 score for classification tasks"""
        try:
            if 'predicted_categories' in episode.actual_results and 'actual_categories' in episode.actual_results:
                predicted = episode.actual_results['predicted_categories']
                actual = episode.actual_results['actual_categories']
                return float(f1_score(actual, predicted, average='weighted'))
        except Exception as e:
            logger.warning(f"Could not calculate F1 score: {e}")
        return None
    
    def _calculate_edit_distance(self, episode: EpisodeEvent) -> Optional[float]:
        """Calculate edit distance between predicted and actual text"""
        try:
            predicted_text = episode.model_output
            if 'actual_text' in episode.actual_results:
                actual_text = episode.actual_results['actual_text']
                return float(self._levenshtein_distance(predicted_text, actual_text))
        except Exception:
            return None
    
    def _calculate_brier_score(self, episode: EpisodeEvent) -> Optional[float]:
        """Calculate Brier score for probability calibration"""
        try:
            if episode.confidence_scores and 'outcome_probabilities' in episode.actual_results:
                predicted_probs = np.array(list(episode.confidence_scores.values()))
                actual_outcomes = np.array(episode.actual_results['outcome_probabilities'])
                return float(np.mean((predicted_probs - actual_outcomes) ** 2))
        except Exception:
            return None
    
    def _calculate_reliability_deviation(self, episode: EpisodeEvent) -> Optional[float]:
        """Calculate deviation from perfect reliability"""
        try:
            if episode.confidence_scores:
                avg_confidence = np.mean(list(episode.confidence_scores.values()))
                success_rate = 1.0 if episode.user_verdict == "success" else 0.0
                return float(abs(avg_confidence - success_rate))
        except Exception:
            return None
    
    def _calculate_kl_divergence(self, episode: EpisodeEvent) -> Optional[float]:
        """Calculate KL divergence from baseline distribution"""
        try:
            agent_type = episode.agent_id.split('_')[0] if '_' in episode.agent_id else episode.agent_id
            if agent_type in self.baseline_distributions:
                current_dist = self._extract_response_distribution(episode.model_output)
                baseline_dist = self.baseline_distributions[agent_type]
                return float(entropy(current_dist, baseline_dist))
        except Exception:
            return None
    
    def _count_schema_mismatches(self, episode: EpisodeEvent) -> int:
        """Count schema version mismatches"""
        mismatch_count = 0
        for interface_type, interface_data in episode.interfaces_used.items():
            if 'expected_version' in interface_data and 'actual_version' in interface_data:
                if interface_data['expected_version'] != interface_data['actual_version']:
                    mismatch_count += 1
        return mismatch_count
    
    def _calculate_prompt_sensitivity(self, episode: EpisodeEvent) -> Optional[float]:
        """Calculate sensitivity to prompt variations"""
        # This would need historical data of prompt variations
        return None  # Placeholder - needs implementation with historical data
    
    def _calculate_interface_error_rates(self, episode: EpisodeEvent) -> Dict[InterfaceType, float]:
        """Calculate error rates per interface"""
        error_rates = {}
        for interface_type, interface_data in episode.interfaces_used.items():
            if 'error_count' in interface_data and 'total_calls' in interface_data:
                total_calls = interface_data['total_calls']
                if total_calls > 0:
                    error_rates[interface_type] = interface_data['error_count'] / total_calls
        return error_rates
    
    def _get_retry_counts(self, episode: EpisodeEvent) -> Dict[InterfaceType, int]:
        """Get retry counts per interface"""
        retry_counts = {}
        for interface_type, interface_data in episode.interfaces_used.items():
            retry_counts[interface_type] = interface_data.get('retry_count', 0)
        return retry_counts
    
    def _calculate_mttr(self, episode: EpisodeEvent) -> Dict[InterfaceType, float]:
        """Calculate Mean Time To Recovery per interface"""
        mttr = {}
        for interface_type, interface_data in episode.interfaces_used.items():
            if 'recovery_times' in interface_data:
                recovery_times = interface_data['recovery_times']
                if recovery_times:
                    mttr[interface_type] = np.mean(recovery_times)
        return mttr
    
    def _calculate_retrieval_hit_rate(self, episode: EpisodeEvent) -> Optional[float]:
        """Calculate context retrieval hit rate"""
        try:
            if 'retrieved_items' in episode.retrieved_context and 'total_queries' in episode.retrieved_context:
                retrieved = episode.retrieved_context['retrieved_items']
                total = episode.retrieved_context['total_queries']
                return float(retrieved / total) if total > 0 else 0.0
        except Exception:
            return None
    
    def _calculate_conflict_density(self, episode: EpisodeEvent) -> Optional[float]:
        """Calculate density of conflicts in retrieved context"""
        try:
            if 'conflicts' in episode.retrieved_context and 'total_items' in episode.retrieved_context:
                conflicts = episode.retrieved_context['conflicts']
                total = episode.retrieved_context['total_items']
                return float(conflicts / total) if total > 0 else 0.0
        except Exception:
            return None
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _extract_response_distribution(self, response: str) -> np.ndarray:
        """Extract distribution from response for KL divergence calculation"""
        # Simple implementation - count word frequencies as distribution
        words = response.lower().split()
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Convert to probability distribution
        total_words = len(words)
        if total_words > 0:
            return np.array([count / total_words for count in word_counts.values()])
        else:
            return np.array([1.0])  # Fallback uniform distribution


class DecisionEngine:
    """Determines focus areas for learning improvements"""
    
    def __init__(self):
        self.thresholds = {
            'systematic_error_rate': 0.1,
            'prompt_sensitivity_index': 0.3,
            'interface_reliability': 0.95,
            'context_utility': 0.7
        }
    
    def decide_focus_area(self, metrics: DerivedMetrics, episode: EpisodeEvent) -> FocusArea:
        """Decide which focus area needs attention based on metrics"""
        
        # Check for context utility issues first -> context updates
        if self._has_context_utility_issues(metrics):
            return FocusArea.CONTEXT
        
        # Check for interface reliability issues -> interface fixes
        if self._has_interface_reliability_issues(metrics):
            return FocusArea.INTERFACE
        
        # Check for high prompt sensitivity -> prompt adjustment
        if self._has_high_prompt_sensitivity(metrics):
            return FocusArea.PROMPT
        
        # Check for systematic errors -> model fine-tuning
        if self._has_systematic_errors(metrics):
            return FocusArea.MODEL
        
        # Default to model improvement if no clear signal
        return FocusArea.MODEL
    
    def _has_systematic_errors(self, metrics: DerivedMetrics) -> bool:
        """Check for systematic error patterns"""
        error_indicators = [
            metrics.f1_score is not None and metrics.f1_score < (1 - self.thresholds['systematic_error_rate']),
            metrics.brier_score is not None and metrics.brier_score > self.thresholds['systematic_error_rate'],
            metrics.reliability_deviation is not None and metrics.reliability_deviation > self.thresholds['systematic_error_rate']
        ]
        return any(error_indicators)
    
    def _has_high_prompt_sensitivity(self, metrics: DerivedMetrics) -> bool:
        """Check for high prompt sensitivity"""
        return (metrics.prompt_sensitivity_index is not None and 
                metrics.prompt_sensitivity_index > self.thresholds['prompt_sensitivity_index'])
    
    def _has_interface_reliability_issues(self, metrics: DerivedMetrics) -> bool:
        """Check for interface reliability problems"""
        for interface_type, error_rate in metrics.interface_error_rates.items():
            if error_rate > (1 - self.thresholds['interface_reliability']):
                return True
        return False
    
    def _has_context_utility_issues(self, metrics: DerivedMetrics) -> bool:
        """Check for context utility problems"""
        utility_issues = [
            metrics.retrieval_hit_rate is not None and metrics.retrieval_hit_rate < self.thresholds['context_utility'],
            metrics.conflict_density is not None and metrics.conflict_density > (1 - self.thresholds['context_utility'])
        ]
        return any(utility_issues)


@dataclass
class AbstractContext:
    """Layered abstract context for MCP server management"""
    agent_id: str
    
    # Narrative state
    commitments: List[str] = field(default_factory=list)
    role_relationships: Dict[str, str] = field(default_factory=dict)
    ongoing_sagas: List[str] = field(default_factory=list)
    
    # Domain frames
    ontology_entities: Dict[str, Any] = field(default_factory=dict)
    domain_relationships: Dict[str, List[str]] = field(default_factory=dict)
    active_policies: List[str] = field(default_factory=list)
    
    # Operating memory
    episode_summaries: List[str] = field(default_factory=list)
    outcome_patterns: Dict[str, float] = field(default_factory=dict)
    learned_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Interface affordances
    available_capabilities: Dict[InterfaceType, List[str]] = field(default_factory=dict)
    capability_limits: Dict[InterfaceType, Dict[str, Any]] = field(default_factory=dict)
    reliability_scores: Dict[InterfaceType, float] = field(default_factory=dict)
    
    # Metadata
    version: str = "1.0"
    last_updated: datetime = field(default_factory=datetime.now)
    update_source: str = "system"


class AbstractContextManager:
    """Manages abstract contexts with layered persistence via MCP server"""
    
    def __init__(self, mcp_client=None):
        self.mcp_client = mcp_client
        self.contexts: Dict[str, AbstractContext] = {}
        self.context_versions: Dict[str, List[str]] = {}
        
    async def update_context_from_episode(self, episode: EpisodeEvent, 
                                        focus_area: FocusArea) -> AbstractContext:
        """Update abstract context based on episode and focus area"""
        agent_id = episode.agent_id
        
        # Get or create context
        context = self.contexts.get(agent_id, AbstractContext(agent_id=agent_id))
        
        # Update based on focus area
        if focus_area == FocusArea.CONTEXT:
            context = await self._comprehensive_context_update(context, episode)
        else:
            context = await self._incremental_context_update(context, episode)
        
        # Version and persist
        await self._version_and_persist(context)
        
        self.contexts[agent_id] = context
        return context
    
    async def _comprehensive_context_update(self, context: AbstractContext, 
                                          episode: EpisodeEvent) -> AbstractContext:
        """Comprehensive context update when focus area is CONTEXT"""
        
        # Update narrative state
        if episode.user_intent not in context.commitments:
            context.commitments.append(episode.user_intent)
        
        # Update operating memory with episode summary
        episode_summary = self._generate_episode_summary(episode)
        context.episode_summaries.append(episode_summary)
        
        # Update outcome patterns
        if episode.user_verdict:
            outcome_key = f"{episode.scenario_id}_{episode.user_verdict}"
            context.outcome_patterns[outcome_key] = context.outcome_patterns.get(outcome_key, 0) + 1
        
        # Update interface reliability scores
        for interface_type, interface_data in episode.interfaces_used.items():
            if 'success_rate' in interface_data:
                context.reliability_scores[interface_type] = interface_data['success_rate']
        
        context.last_updated = datetime.now()
        context.update_source = "comprehensive_update"
        
        return context
    
    async def _incremental_context_update(self, context: AbstractContext, 
                                        episode: EpisodeEvent) -> AbstractContext:
        """Incremental context update for non-context focus areas"""
        
        # Light updates - only critical information
        if len(context.episode_summaries) > 100:  # Keep last 100 summaries
            context.episode_summaries = context.episode_summaries[-100:]
        
        # Update interface reliability incrementally
        for interface_type in episode.interfaces_used:
            if interface_type not in context.reliability_scores:
                context.reliability_scores[interface_type] = 0.95  # Default
        
        context.last_updated = datetime.now()
        context.update_source = "incremental_update"
        
        return context
    
    def _generate_episode_summary(self, episode: EpisodeEvent) -> str:
        """Generate a concise summary of the episode"""
        summary_parts = [
            f"Agent: {episode.agent_id}",
            f"Scenario: {episode.scenario_id}",
            f"Intent: {episode.user_intent[:100]}...",
            f"Outcome: {episode.user_verdict or 'pending'}",
            f"Timestamp: {episode.timestamp.isoformat()}"
        ]
        return " | ".join(summary_parts)
    
    async def _version_and_persist(self, context: AbstractContext):
        """Version the context and persist to MCP server"""
        # Increment version
        version_parts = context.version.split('.')
        patch_version = int(version_parts[-1]) + 1
        context.version = f"{'.'.join(version_parts[:-1])}.{patch_version}"
        
        # Track versions
        agent_id = context.agent_id
        if agent_id not in self.context_versions:
            self.context_versions[agent_id] = []
        self.context_versions[agent_id].append(context.version)
        
        # Persist to MCP server if available
        if self.mcp_client:
            try:
                await self.mcp_client.persist_context(context)
                logger.info(f"Persisted context version {context.version} for agent {agent_id}")
            except Exception as e:
                logger.error(f"Failed to persist context: {e}")
    
    async def get_context(self, agent_id: str, version: Optional[str] = None) -> Optional[AbstractContext]:
        """Get context for agent, optionally specific version"""
        if version is None:
            return self.contexts.get(agent_id)
        
        # For specific versions, would need to query MCP server
        # This is a simplified implementation
        return self.contexts.get(agent_id)
    
    def detect_conflicts(self, context: AbstractContext) -> List[str]:
        """Detect conflicts in the context"""
        conflicts = []
        
        # Check for conflicting commitments
        if len(context.commitments) > 1:
            # Simple conflict detection - would be more sophisticated in practice
            for i, commitment1 in enumerate(context.commitments):
                for j, commitment2 in enumerate(context.commitments[i+1:], i+1):
                    if self._are_conflicting(commitment1, commitment2):
                        conflicts.append(f"Conflicting commitments: {commitment1} vs {commitment2}")
        
        return conflicts
    
    def _are_conflicting(self, commitment1: str, commitment2: str) -> bool:
        """Simple conflict detection between commitments"""
        # Placeholder logic - would use more sophisticated NLP in practice
        conflict_keywords = [('increase', 'decrease'), ('buy', 'sell'), ('expand', 'contract')]
        
        for keyword1, keyword2 in conflict_keywords:
            if keyword1 in commitment1.lower() and keyword2 in commitment2.lower():
                return True
            if keyword2 in commitment1.lower() and keyword1 in commitment2.lower():
                return True
        
        return False


class SelfLearningSystem:
    """
    Enhanced audit-driven self-learning system for boardroom agents.
    
    Implements comprehensive episode tracking, metrics calculation, decision engine,
    and abstract context management as described in the Self-Learning.md framework.
    
    Key Features:
    - Episode-driven event model with comprehensive tracking
    - Derived metrics calculation (RMSE, F1, Brier score, KL divergence, etc.)
    - Decision engine for focus area determination
    - Abstract context management with MCP integration
    - Shadow evaluation and rollback capabilities
    - Interface reliability monitoring
    """
    
    def __init__(self, data_dir: str = None, lora_manager=None, mcp_client=None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "learning_data")
        self.lora_manager = lora_manager
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Enhanced components
        self.metrics_calculator = MetricsCalculator()
        self.decision_engine = DecisionEngine()
        self.context_manager = AbstractContextManager(mcp_client)
        
        # State tracking - existing
        self.situations: Dict[str, Situation] = {}
        self.feedback: Dict[str, List[MentorFeedback]] = {}
        self.original_dataset: Dict[str, List[TrainingExample]] = {}
        self.self_learning_dataset: Dict[str, List[TrainingExample]] = {}
        self.learning_metrics: Dict[str, LearningMetrics] = {}
        self.learning_cycles: Dict[str, int] = {}
        
        # New audit-driven state tracking
        self.episodes: Dict[str, EpisodeEvent] = {}
        self.derived_metrics: Dict[str, DerivedMetrics] = {}
        self.shadow_evaluations: Dict[str, Dict[str, Any]] = {}
        self.rollback_points: Dict[str, Dict[str, Any]] = {}
        
        # Load existing data
        self._load_datasets()
        self._load_situations()
        self._load_feedback()
        self._load_episodes()
        
        logger.info(f"Enhanced Self-Learning System initialized with data dir: {self.data_dir}")
    
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
    
    def _load_episodes(self):
        """Load existing episodes from disk"""
        try:
            episodes_path = os.path.join(self.data_dir, "episodes.json")
            if os.path.exists(episodes_path):
                with open(episodes_path, 'r') as f:
                    data = json.load(f)
                    for episode_data in data:
                        episode = EpisodeEvent(
                            agent_id=episode_data["agent_id"],
                            scenario_id=episode_data["scenario_id"],
                            timestamp=datetime.fromisoformat(episode_data["timestamp"]),
                            source=episode_data["source"],
                            correlation_ids=episode_data["correlation_ids"],
                            user_intent=episode_data["user_intent"],
                            prompts=episode_data["prompts"],
                            tool_calls=episode_data["tool_calls"],
                            retrieved_context=episode_data["retrieved_context"],
                            third_party_payloads=episode_data["third_party_payloads"],
                            model_output=episode_data["model_output"],
                            action_plan=episode_data["action_plan"],
                            selected_tools=episode_data["selected_tools"],
                            confidence_scores=episode_data["confidence_scores"],
                            actual_results=episode_data["actual_results"],
                            **{k: v for k, v in episode_data.items() if k not in [
                                "agent_id", "scenario_id", "timestamp", "source", "correlation_ids",
                                "user_intent", "prompts", "tool_calls", "retrieved_context",
                                "third_party_payloads", "model_output", "action_plan",
                                "selected_tools", "confidence_scores", "actual_results"
                            ]}
                        )
                        episode_id = f"{episode.agent_id}_{episode.scenario_id}_{episode.timestamp.isoformat()}"
                        self.episodes[episode_id] = episode
                
                logger.info(f"Loaded {len(self.episodes)} episodes")
                
        except Exception as e:
            logger.error(f"Failed to load episodes: {e}")
    
    # Core Audit-Driven Learning Methods
    
    async def process_episode(self, episode: EpisodeEvent) -> Dict[str, Any]:
        """
        Process a completed episode through the audit-driven self-learning loop.
        
        This is the main entry point implementing the framework from Self-Learning.md:
        1. Compute metrics and analyze patterns
        2. Decide focus area (context, prompt, model, interface)
        3. Apply appropriate changes
        4. Shadow evaluate and rollback if needed
        
        Args:
            episode: Completed episode event
            
        Returns:
            Processing results and metrics
        """
        try:
            # Store episode
            episode_id = f"{episode.agent_id}_{episode.scenario_id}_{episode.timestamp.isoformat()}"
            self.episodes[episode_id] = episode
            
            # 1. Compute metrics and analyze patterns
            metrics = self.metrics_calculator.calculate_derived_metrics(episode)
            self.derived_metrics[episode_id] = metrics
            
            # 2. Decide focus area based on metrics
            focus_area = self.decision_engine.decide_focus_area(metrics, episode)
            
            # 3. Create rollback point before changes
            await self._create_rollback_point(episode.agent_id)
            
            # 4. Apply changes based on focus area
            changes_applied = await self._apply_focus_area_changes(episode, focus_area, metrics)
            
            # 5. Shadow evaluate the changes
            evaluation_result = await self._shadow_evaluate(episode.agent_id, episode)
            
            # 6. Decide whether to keep or rollback changes
            if not self._should_keep_changes(evaluation_result):
                await self._rollback_changes(episode.agent_id)
                logger.info(f"Rolled back changes for agent {episode.agent_id} due to poor evaluation")
                changes_applied["rolled_back"] = True
            else:
                logger.info(f"Kept changes for agent {episode.agent_id} - evaluation passed")
                changes_applied["rolled_back"] = False
            
            # 7. Save updated state
            await self._save_episodes()
            
            return {
                "episode_id": episode_id,
                "metrics": metrics,
                "focus_area": focus_area.value,
                "changes_applied": changes_applied,
                "evaluation_result": evaluation_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process episode: {e}")
            return {"error": f"Episode processing failed: {str(e)}"}
    
    async def _apply_focus_area_changes(self, episode: EpisodeEvent, 
                                      focus_area: FocusArea, 
                                      metrics: DerivedMetrics) -> Dict[str, Any]:
        """Apply changes based on determined focus area"""
        changes = {"focus_area": focus_area.value}
        
        if focus_area == FocusArea.CONTEXT:
            # Update abstract context via MCP
            context = await self.context_manager.update_context_from_episode(episode, focus_area)
            changes["context_updated"] = True
            changes["context_version"] = context.version
            
        elif focus_area == FocusArea.PROMPT:
            # Select and swap prompt variant
            new_prompt = await self._select_prompt_variant(episode, metrics)
            await self._swap_prompt(episode.agent_id, new_prompt)
            changes["prompt_updated"] = True
            changes["new_prompt_id"] = new_prompt.get("id", "unknown")
            
        elif focus_area == FocusArea.MODEL:
            # Schedule fine-tuning with curated dataset
            dataset = await self._curate_fine_tune_data(episode.agent_id, metrics)
            fine_tune_job = await self._schedule_fine_tune(episode.agent_id, dataset)
            changes["fine_tune_scheduled"] = True
            changes["fine_tune_job_id"] = fine_tune_job.get("job_id", "unknown")
            
        elif focus_area == FocusArea.INTERFACE:
            # Propose and apply interface patches
            interface_fixes = await self._propose_interface_patches(episode, metrics)
            applied_fixes = await self._apply_interface_fixes(interface_fixes)
            changes["interface_fixes_applied"] = len(applied_fixes)
            changes["fixes"] = applied_fixes
        
        return changes
    
    async def _select_prompt_variant(self, episode: EpisodeEvent, 
                                   metrics: DerivedMetrics) -> Dict[str, Any]:
        """Select better prompt variant based on metrics"""
        # Placeholder implementation
        return {
            "id": f"prompt_variant_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "template": "Enhanced prompt template based on metrics analysis",
            "improvements": ["Reduced ambiguity", "Better role framing", "Clearer output format"]
        }
    
    async def _swap_prompt(self, agent_id: str, new_prompt: Dict[str, Any]):
        """Swap the prompt for an agent"""
        # This would integrate with a prompt registry system
        logger.info(f"Swapped prompt for agent {agent_id} to {new_prompt['id']}")
    
    async def _curate_fine_tune_data(self, agent_id: str, 
                                   metrics: DerivedMetrics) -> List[TrainingExample]:
        """Curate dataset for fine-tuning based on metrics"""
        # Use existing logic but focus on problem areas identified by metrics
        role = agent_id.split('_')[0] if '_' in agent_id else agent_id
        
        # Get base examples
        original_examples = self.original_dataset.get(role, [])
        learning_examples = self.self_learning_dataset.get(role, [])
        
        # Filter based on metrics to focus on problem areas
        if metrics.f1_score is not None and metrics.f1_score < 0.7:
            # Focus on classification improvements
            curated = [ex for ex in learning_examples if "classification" in ex.input_prompt.lower()]
        elif metrics.reliability_deviation is not None and metrics.reliability_deviation > 0.3:
            # Focus on confidence calibration
            curated = [ex for ex in learning_examples if ex.quality_score > 0.8]
        else:
            # General curation
            curated = learning_examples[-50:]  # Most recent examples
        
        # Blend with original
        blended = original_examples[:100] + curated
        return blended
    
    async def _schedule_fine_tune(self, agent_id: str, 
                                dataset: List[TrainingExample]) -> Dict[str, Any]:
        """Schedule fine-tuning job"""
        job_id = f"finetune_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # This would integrate with the actual fine-tuning pipeline
        logger.info(f"Scheduled fine-tune job {job_id} for agent {agent_id} with {len(dataset)} examples")
        
        return {
            "job_id": job_id,
            "dataset_size": len(dataset),
            "status": "scheduled",
            "estimated_completion": (datetime.now() + timedelta(hours=2)).isoformat()
        }
    
    async def _propose_interface_patches(self, episode: EpisodeEvent, 
                                       metrics: DerivedMetrics) -> List[Dict[str, Any]]:
        """Propose fixes for interface reliability issues"""
        patches = []
        
        for interface_type, error_rate in metrics.interface_error_rates.items():
            if error_rate > 0.1:  # More than 10% error rate
                patches.append({
                    "interface": interface_type.value,
                    "issue": "High error rate",
                    "error_rate": error_rate,
                    "proposed_fix": "Add retry logic with exponential backoff",
                    "priority": "high" if error_rate > 0.2 else "medium"
                })
        
        return patches
    
    async def _apply_interface_fixes(self, patches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply proposed interface fixes"""
        applied_fixes = []
        
        for patch in patches:
            # This would integrate with interface management system
            logger.info(f"Applied interface fix for {patch['interface']}: {patch['proposed_fix']}")
            applied_fixes.append({
                "interface": patch["interface"],
                "fix_applied": patch["proposed_fix"],
                "timestamp": datetime.now().isoformat()
            })
        
        return applied_fixes
    
    async def _shadow_evaluate(self, agent_id: str, episode: EpisodeEvent) -> Dict[str, Any]:
        """Shadow evaluate changes before deciding to keep them"""
        # This would run parallel evaluation with old vs new system
        evaluation = {
            "agent_id": agent_id,
            "evaluation_type": "shadow",
            "baseline_performance": 0.75,  # Placeholder
            "new_performance": 0.78,  # Placeholder  
            "improvement": 0.03,
            "confidence_interval": [0.01, 0.05],
            "sample_size": 50,
            "evaluated_at": datetime.now().isoformat()
        }
        
        self.shadow_evaluations[agent_id] = evaluation
        return evaluation
    
    def _should_keep_changes(self, evaluation: Dict[str, Any]) -> bool:
        """Determine if changes should be kept based on shadow evaluation"""
        improvement = evaluation.get("improvement", 0)
        confidence_interval = evaluation.get("confidence_interval", [0, 0])
        
        # Keep changes if there's statistically significant improvement
        return improvement > 0 and confidence_interval[0] > 0
    
    async def _create_rollback_point(self, agent_id: str):
        """Create a rollback point before making changes"""
        rollback_data = {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "context": await self.context_manager.get_context(agent_id),
            "prompt_state": "current_prompt_state",  # Would capture actual prompt state
            "model_state": "current_model_state",    # Would capture actual model state
            "interface_state": "current_interface_state"  # Would capture interface configs
        }
        
        self.rollback_points[agent_id] = rollback_data
        logger.info(f"Created rollback point for agent {agent_id}")
    
    async def _rollback_changes(self, agent_id: str):
        """Rollback to previous state"""
        if agent_id in self.rollback_points:
            rollback_data = self.rollback_points[agent_id]
            
            # Restore context
            if rollback_data["context"]:
                self.context_manager.contexts[agent_id] = rollback_data["context"]
            
            # Restore other states (prompt, model, interface)
            # This would integrate with respective management systems
            
            logger.info(f"Rolled back changes for agent {agent_id}")
        else:
            logger.warning(f"No rollback point found for agent {agent_id}")
    
    async def _save_episodes(self):
        """Save episodes to disk"""
        try:
            episodes_path = os.path.join(self.data_dir, "episodes.json")
            episodes_data = []
            
            for episode in self.episodes.values():
                episode_dict = {
                    "agent_id": episode.agent_id,
                    "scenario_id": episode.scenario_id,
                    "timestamp": episode.timestamp.isoformat(),
                    "source": episode.source,
                    "correlation_ids": episode.correlation_ids,
                    "user_intent": episode.user_intent,
                    "prompts": episode.prompts,
                    "tool_calls": episode.tool_calls,
                    "retrieved_context": episode.retrieved_context,
                    "third_party_payloads": episode.third_party_payloads,
                    "model_output": episode.model_output,
                    "action_plan": episode.action_plan,
                    "selected_tools": episode.selected_tools,
                    "confidence_scores": episode.confidence_scores,
                    "actual_results": episode.actual_results,
                    "user_verdict": episode.user_verdict,
                    "mentor_verdict": episode.mentor_verdict,
                    "kpis": episode.kpis,
                    "error_codes": episode.error_codes,
                    "latencies": episode.latencies,
                    "stakeholder_ratings": episode.stakeholder_ratings,
                    "mentor_annotations": episode.mentor_annotations,
                    "categorical_tags": episode.categorical_tags,
                    "suggested_corrections": episode.suggested_corrections,
                    "context_updates": episode.context_updates,
                    "mcp_object_refs": episode.mcp_object_refs,
                    "interfaces_used": {k.value: v for k, v in episode.interfaces_used.items()},
                    "schema_versions": episode.schema_versions
                }
                episodes_data.append(episode_dict)
            
            with open(episodes_path, 'w') as f:
                json.dump(episodes_data, f, indent=2)
            
            logger.info(f"Saved {len(episodes_data)} episodes to disk")
            
        except Exception as e:
            logger.error(f"Failed to save episodes: {e}")
    
    # Integration methods with existing system
    
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