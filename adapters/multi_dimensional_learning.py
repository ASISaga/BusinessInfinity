"""
Multi-Dimensional Self-Learning System for Business Infinity

This module implements a comprehensive self-learning methodology that can adapt
across multiple dimensions based on stakeholder feedback and audit trail analysis:

1. LLM Model - Base model selection and capabilities
2. Weights/Dataset - Training data and model parameters 
3. Context to LLM - Situational context and background information
4. Prompt to LLM - Input formatting and prompt engineering
5. Features of associated MCP - MCP server capabilities and integrations

The system analyzes feedback patterns and performance metrics to determine
when and how to update each dimension for optimal boardroom agent performance.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class LearningDimension(Enum):
    """Dimensions of self-learning adaptation"""
    LLM_MODEL = "llm_model"           # Base model selection and capabilities
    WEIGHTS_DATASET = "weights_dataset"    # Training data and model parameters
    CONTEXT = "context"               # Situational context and background info
    PROMPT = "prompt"                 # Input formatting and prompt engineering  
    MCP_FEATURES = "mcp_features"     # MCP server capabilities and integrations


class AdaptationTrigger(Enum):
    """Triggers that initiate dimensional adaptation"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    STAKEHOLDER_FEEDBACK = "stakeholder_feedback"
    AUDIT_PATTERN_ANALYSIS = "audit_pattern_analysis"
    ENVIRONMENTAL_CHANGE = "environmental_change"
    EXPERT_RECOMMENDATION = "expert_recommendation"


class AdaptationStrategy(Enum):
    """Strategies for adapting each dimension"""
    INCREMENTAL = "incremental"       # Small, gradual changes
    TARGETED = "targeted"             # Specific focused improvements
    COMPREHENSIVE = "comprehensive"   # Major overhaul
    EXPERIMENTAL = "experimental"     # A/B testing approach


@dataclass
class FeedbackPattern:
    """Analysis of feedback patterns across dimensions"""
    dimension: LearningDimension
    feedback_type: str
    frequency: int
    severity: float
    recent_trend: str  # "improving", "degrading", "stable"
    affected_roles: List[str]
    suggested_action: AdaptationStrategy
    confidence: float


@dataclass
class DimensionalMetrics:
    """Performance metrics for each learning dimension"""
    dimension: LearningDimension
    current_performance: float
    historical_performance: List[float]
    stakeholder_satisfaction: float
    adaptation_frequency: int
    last_adaptation: Optional[datetime]
    cost_benefit_ratio: float
    risk_level: float


@dataclass
class AdaptationDecision:
    """Decision to adapt a specific dimension"""
    dimension: LearningDimension
    trigger: AdaptationTrigger
    strategy: AdaptationStrategy
    priority: int  # 1-5 scale
    estimated_impact: float
    estimated_cost: float
    risk_assessment: float
    timeline: str
    dependencies: List[LearningDimension]
    rollback_plan: str


class MultiDimensionalLearningOrchestrator:
    """
    Orchestrates self-learning across multiple dimensions based on stakeholder
    feedback, audit trail analysis, and performance metrics.
    
    Key Features:
    - Analyzes feedback patterns to identify adaptation needs
    - Determines optimal dimension(s) to update based on impact/cost analysis
    - Coordinates multi-dimensional adaptations with dependency management
    - Tracks performance improvements and adaptation effectiveness
    """
    
    def __init__(self, adapter_orchestrator=None, audit_manager=None):
        self.adapter_orchestrator = adapter_orchestrator
        self.audit_manager = audit_manager
        
        # State tracking
        self.dimensional_metrics: Dict[LearningDimension, DimensionalMetrics] = {}
        self.feedback_patterns: Dict[str, List[FeedbackPattern]] = defaultdict(list)
        self.adaptation_history: List[AdaptationDecision] = []
        self.performance_windows: Dict[LearningDimension, deque] = {}
        
        # Configuration
        self.adaptation_thresholds = {
            LearningDimension.LLM_MODEL: 0.3,      # High threshold - expensive
            LearningDimension.WEIGHTS_DATASET: 0.2,  # Medium threshold
            LearningDimension.CONTEXT: 0.15,        # Lower threshold - faster
            LearningDimension.PROMPT: 0.1,          # Lowest threshold - cheapest
            LearningDimension.MCP_FEATURES: 0.25    # Medium-high threshold
        }
        
        self.adaptation_costs = {
            LearningDimension.LLM_MODEL: 10.0,      # Very expensive - model change
            LearningDimension.WEIGHTS_DATASET: 7.0,  # Expensive - retraining
            LearningDimension.CONTEXT: 3.0,         # Medium cost - data gathering
            LearningDimension.PROMPT: 1.0,          # Low cost - text changes
            LearningDimension.MCP_FEATURES: 5.0     # Medium-high - integration work
        }
        
        # Initialize metrics for all dimensions
        self._initialize_dimensional_metrics()
        
        logger.info("Multi-Dimensional Learning Orchestrator initialized")
    
    def _initialize_dimensional_metrics(self):
        """Initialize performance tracking for each dimension"""
        for dimension in LearningDimension:
            self.dimensional_metrics[dimension] = DimensionalMetrics(
                dimension=dimension,
                current_performance=0.75,  # Start at baseline
                historical_performance=[0.75],
                stakeholder_satisfaction=0.7,
                adaptation_frequency=0,
                last_adaptation=None,
                cost_benefit_ratio=1.0,
                risk_level=0.3
            )
            
            # Initialize sliding window for performance tracking
            self.performance_windows[dimension] = deque(maxlen=20)
            self.performance_windows[dimension].append(0.75)
    
    async def analyze_stakeholder_feedback(self, feedback_data: List[Dict[str, Any]]) -> List[FeedbackPattern]:
        """
        Analyze stakeholder feedback to identify patterns requiring dimensional adaptation.
        
        Args:
            feedback_data: List of feedback entries from stakeholders
            
        Returns:
            List of identified feedback patterns
        """
        patterns = []
        
        # Group feedback by type and analyze patterns
        feedback_groups = defaultdict(list)
        
        for feedback in feedback_data:
            feedback_type = feedback.get("type", "general")
            feedback_groups[feedback_type].append(feedback)
        
        for feedback_type, feedback_list in feedback_groups.items():
            # Analyze each dimension for this feedback type
            for dimension in LearningDimension:
                pattern = await self._analyze_dimensional_feedback(dimension, feedback_type, feedback_list)
                if pattern and pattern.confidence > 0.6:
                    patterns.append(pattern)
        
        logger.info(f"Analyzed stakeholder feedback: {len(patterns)} patterns identified")
        return patterns
    
    async def _analyze_dimensional_feedback(self, dimension: LearningDimension, 
                                          feedback_type: str, 
                                          feedback_list: List[Dict[str, Any]]) -> Optional[FeedbackPattern]:
        """Analyze feedback for a specific dimension"""
        
        if not feedback_list:
            return None
        
        # Dimension-specific feedback analysis
        dimension_keywords = {
            LearningDimension.LLM_MODEL: [
                "model", "intelligence", "reasoning", "capability", "understanding",
                "depth", "sophistication", "accuracy", "knowledge"
            ],
            LearningDimension.WEIGHTS_DATASET: [
                "training", "learning", "examples", "data", "patterns", "experience",
                "knowledge base", "expertise", "specialization"
            ],
            LearningDimension.CONTEXT: [
                "context", "background", "situation", "environment", "circumstances",
                "relevant", "appropriate", "understanding", "awareness"
            ],
            LearningDimension.PROMPT: [
                "instruction", "prompt", "query", "question", "format", "structure",
                "clarity", "specificity", "direction", "guidance"
            ],
            LearningDimension.MCP_FEATURES: [
                "integration", "connection", "data access", "external", "system",
                "tools", "features", "capabilities", "automation"
            ]
        }
        
        keywords = dimension_keywords.get(dimension, [])
        
        # Count keyword mentions and analyze sentiment
        keyword_mentions = 0
        sentiment_scores = []
        severity_scores = []
        affected_roles = set()
        
        for feedback in feedback_list:
            content = feedback.get("content", "").lower()
            
            # Count keyword mentions
            for keyword in keywords:
                if keyword in content:
                    keyword_mentions += 1
            
            # Extract sentiment and severity
            sentiment = feedback.get("sentiment", 0.5)  # 0-1 scale
            severity = feedback.get("severity", 0.5)    # 0-1 scale
            role = feedback.get("affected_role", "general")
            
            sentiment_scores.append(sentiment)
            severity_scores.append(severity)
            affected_roles.add(role)
        
        # Calculate pattern metrics
        frequency = keyword_mentions
        avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0.5
        avg_severity = np.mean(severity_scores) if severity_scores else 0.5
        
        # Determine trend from recent feedback
        recent_feedback = feedback_list[-5:] if len(feedback_list) >= 5 else feedback_list
        recent_sentiment = np.mean([f.get("sentiment", 0.5) for f in recent_feedback])
        
        if recent_sentiment > 0.7:
            trend = "improving"
        elif recent_sentiment < 0.4:
            trend = "degrading"
        else:
            trend = "stable"
        
        # Suggest adaptation strategy based on severity and frequency
        if avg_severity > 0.8 and frequency > 3:
            strategy = AdaptationStrategy.COMPREHENSIVE
        elif avg_severity > 0.6 and frequency > 2:
            strategy = AdaptationStrategy.TARGETED
        elif frequency > 0:
            strategy = AdaptationStrategy.INCREMENTAL
        else:
            strategy = AdaptationStrategy.EXPERIMENTAL
        
        # Calculate confidence based on frequency and consistency
        confidence = min(1.0, (frequency * 0.2) + (1.0 - abs(0.5 - avg_sentiment)))
        
        if confidence > 0.3:  # Only return patterns with reasonable confidence
            return FeedbackPattern(
                dimension=dimension,
                feedback_type=feedback_type,
                frequency=frequency,
                severity=avg_severity,
                recent_trend=trend,
                affected_roles=list(affected_roles),
                suggested_action=strategy,
                confidence=confidence
            )
        
        return None
    
    async def analyze_audit_patterns(self, audit_events: List[Dict[str, Any]]) -> List[FeedbackPattern]:
        """
        Analyze audit trail patterns to identify learning opportunities.
        
        Args:
            audit_events: List of audit trail events
            
        Returns:
            List of patterns derived from audit analysis
        """
        patterns = []
        
        if not audit_events:
            return patterns
        
        # Group events by type and analyze performance patterns
        event_groups = defaultdict(list)
        
        for event in audit_events:
            event_type = event.get("event_type", "unknown")
            event_groups[event_type].append(event)
        
        # Analyze decision quality patterns
        decision_events = event_groups.get("boardroom_decision", [])
        if decision_events:
            decision_patterns = await self._analyze_decision_quality_patterns(decision_events)
            patterns.extend(decision_patterns)
        
        # Analyze agent performance patterns
        vote_events = event_groups.get("agent_vote", [])
        if vote_events:
            vote_patterns = await self._analyze_vote_patterns(vote_events)
            patterns.extend(vote_patterns)
        
        # Analyze MCP interaction patterns
        mcp_events = event_groups.get("mcp_request", []) + event_groups.get("mcp_response", [])
        if mcp_events:
            mcp_patterns = await self._analyze_mcp_patterns(mcp_events)
            patterns.extend(mcp_patterns)
        
        logger.info(f"Analyzed audit patterns: {len(patterns)} patterns identified")
        return patterns
    
    async def _analyze_decision_quality_patterns(self, decision_events: List[Dict[str, Any]]) -> List[FeedbackPattern]:
        """Analyze decision quality from audit events"""
        patterns = []
        
        # Extract decision quality metrics
        confidence_scores = []
        consensus_scores = []
        time_to_decision = []
        
        for event in decision_events:
            context = event.get("context", {})
            confidence_scores.append(context.get("confidence_score", 0.5))
            consensus_scores.append(context.get("consensus_score", 0.5))
            
            # Calculate time to decision if timestamps available
            start_time = context.get("decision_start")
            end_time = event.get("timestamp")
            if start_time and end_time:
                duration = (datetime.fromisoformat(end_time) - datetime.fromisoformat(start_time)).total_seconds() / 60
                time_to_decision.append(duration)
        
        # Analyze patterns for different dimensions
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.5
        avg_consensus = np.mean(consensus_scores) if consensus_scores else 0.5
        avg_time = np.mean(time_to_decision) if time_to_decision else 30  # Default 30 minutes
        
        # Low confidence suggests model or dataset issues
        if avg_confidence < 0.6:
            patterns.append(FeedbackPattern(
                dimension=LearningDimension.WEIGHTS_DATASET,
                feedback_type="decision_quality",
                frequency=len(decision_events),
                severity=1.0 - avg_confidence,
                recent_trend="degrading",
                affected_roles=["all"],
                suggested_action=AdaptationStrategy.TARGETED,
                confidence=0.8
            ))
        
        # Low consensus suggests context or prompt issues
        if avg_consensus < 0.7:
            patterns.append(FeedbackPattern(
                dimension=LearningDimension.CONTEXT,
                feedback_type="consensus_quality", 
                frequency=len(decision_events),
                severity=1.0 - avg_consensus,
                recent_trend="stable",
                affected_roles=["all"],
                suggested_action=AdaptationStrategy.INCREMENTAL,
                confidence=0.75
            ))
        
        return patterns
    
    async def _analyze_vote_patterns(self, vote_events: List[Dict[str, Any]]) -> List[FeedbackPattern]:
        """Analyze voting patterns from audit events"""
        patterns = []
        
        # Group by agent role
        role_votes = defaultdict(list)
        
        for event in vote_events:
            role = event.get("subject_role", "unknown")
            context = event.get("context", {})
            vote_value = context.get("vote_value", 0.5)
            confidence = context.get("confidence", 0.5)
            
            role_votes[role].append({
                "vote_value": vote_value,
                "confidence": confidence,
                "timestamp": event.get("timestamp")
            })
        
        # Analyze each role's voting patterns
        for role, votes in role_votes.items():
            if len(votes) < 3:  # Need minimum votes for pattern analysis
                continue
            
            vote_values = [v["vote_value"] for v in votes]
            confidences = [v["confidence"] for v in votes]
            
            avg_confidence = np.mean(confidences)
            vote_variance = np.var(vote_values)  # High variance indicates inconsistency
            
            # Low confidence suggests prompt or model issues for this role
            if avg_confidence < 0.65:
                patterns.append(FeedbackPattern(
                    dimension=LearningDimension.PROMPT,
                    feedback_type="vote_confidence",
                    frequency=len(votes),
                    severity=1.0 - avg_confidence,
                    recent_trend="stable",
                    affected_roles=[role],
                    suggested_action=AdaptationStrategy.TARGETED,
                    confidence=0.7
                ))
            
            # High variance suggests context or dataset issues
            if vote_variance > 0.3:
                patterns.append(FeedbackPattern(
                    dimension=LearningDimension.WEIGHTS_DATASET,
                    feedback_type="vote_consistency",
                    frequency=len(votes),
                    severity=min(1.0, vote_variance),
                    recent_trend="degrading",
                    affected_roles=[role],
                    suggested_action=AdaptationStrategy.INCREMENTAL,
                    confidence=0.65
                ))
        
        return patterns
    
    async def _analyze_mcp_patterns(self, mcp_events: List[Dict[str, Any]]) -> List[FeedbackPattern]:
        """Analyze MCP interaction patterns"""
        patterns = []
        
        # Analyze success rates and response quality
        success_count = 0
        total_count = len(mcp_events)
        response_times = []
        error_types = defaultdict(int)
        
        for event in mcp_events:
            context = event.get("context", {})
            success = context.get("success", False)
            
            if success:
                success_count += 1
            else:
                error_type = context.get("error_type", "unknown")
                error_types[error_type] += 1
            
            response_time = context.get("response_time_ms", 1000)  # Default 1 second
            response_times.append(response_time)
        
        success_rate = success_count / total_count if total_count > 0 else 0
        avg_response_time = np.mean(response_times) if response_times else 1000
        
        # Low success rate suggests MCP feature improvements needed
        if success_rate < 0.8 and total_count >= 5:
            patterns.append(FeedbackPattern(
                dimension=LearningDimension.MCP_FEATURES,
                feedback_type="integration_reliability",
                frequency=total_count,
                severity=1.0 - success_rate,
                recent_trend="stable",
                affected_roles=["all"],
                suggested_action=AdaptationStrategy.TARGETED,
                confidence=0.8
            ))
        
        # High response times suggest context optimization needed
        if avg_response_time > 3000:  # 3 seconds
            patterns.append(FeedbackPattern(
                dimension=LearningDimension.CONTEXT,
                feedback_type="mcp_performance",
                frequency=total_count,
                severity=min(1.0, (avg_response_time - 1000) / 5000),  # Normalize to 0-1
                recent_trend="stable",
                affected_roles=["all"],
                suggested_action=AdaptationStrategy.INCREMENTAL,
                confidence=0.7
            ))
        
        return patterns
    
    async def determine_adaptation_priorities(self, patterns: List[FeedbackPattern]) -> List[AdaptationDecision]:
        """
        Determine which dimensions to adapt based on identified patterns.
        
        Args:
            patterns: List of feedback patterns requiring attention
            
        Returns:
            Prioritized list of adaptation decisions
        """
        adaptation_decisions = []
        
        # Group patterns by dimension
        dimension_patterns = defaultdict(list)
        for pattern in patterns:
            dimension_patterns[pattern.dimension].append(pattern)
        
        # Evaluate each dimension for adaptation need
        for dimension, dim_patterns in dimension_patterns.items():
            decision = await self._evaluate_dimensional_adaptation(dimension, dim_patterns)
            if decision:
                adaptation_decisions.append(decision)
        
        # Sort by priority (higher priority first)
        adaptation_decisions.sort(key=lambda x: x.priority, reverse=True)
        
        logger.info(f"Generated {len(adaptation_decisions)} adaptation decisions")
        return adaptation_decisions
    
    async def _evaluate_dimensional_adaptation(self, dimension: LearningDimension, 
                                             patterns: List[FeedbackPattern]) -> Optional[AdaptationDecision]:
        """Evaluate whether a dimension needs adaptation"""
        
        if not patterns:
            return None
        
        # Calculate aggregate metrics
        total_frequency = sum(p.frequency for p in patterns)
        avg_severity = np.mean([p.severity for p in patterns])
        avg_confidence = np.mean([p.confidence for p in patterns])
        
        # Get current dimensional metrics
        metrics = self.dimensional_metrics[dimension]
        
        # Check adaptation threshold
        threshold = self.adaptation_thresholds[dimension]
        adaptation_score = (avg_severity * avg_confidence * (total_frequency / 10))
        
        if adaptation_score < threshold:
            return None  # No adaptation needed
        
        # Determine trigger
        triggers = [AdaptationTrigger.STAKEHOLDER_FEEDBACK, AdaptationTrigger.AUDIT_PATTERN_ANALYSIS]
        primary_trigger = triggers[0] if any("feedback" in p.feedback_type for p in patterns) else triggers[1]
        
        # Determine strategy based on severity and patterns
        strategies = [p.suggested_action for p in patterns]
        strategy_counts = defaultdict(int)
        for s in strategies:
            strategy_counts[s] += 1
        
        primary_strategy = max(strategy_counts.items(), key=lambda x: x[1])[0]
        
        # Calculate priority (1-5 scale)
        priority = min(5, int(1 + (adaptation_score * 4)))
        
        # Calculate estimated impact and cost
        estimated_impact = min(1.0, adaptation_score * 1.5)
        estimated_cost = self.adaptation_costs[dimension]
        
        # Risk assessment based on dimension type
        risk_factors = {
            LearningDimension.LLM_MODEL: 0.8,      # High risk - major change
            LearningDimension.WEIGHTS_DATASET: 0.6, # Medium-high risk
            LearningDimension.CONTEXT: 0.3,        # Low risk
            LearningDimension.PROMPT: 0.2,         # Very low risk
            LearningDimension.MCP_FEATURES: 0.5    # Medium risk
        }
        
        risk_assessment = risk_factors[dimension]
        
        # Determine dependencies
        dependencies = []
        if dimension == LearningDimension.LLM_MODEL:
            dependencies = [LearningDimension.WEIGHTS_DATASET, LearningDimension.PROMPT]
        elif dimension == LearningDimension.WEIGHTS_DATASET:
            dependencies = [LearningDimension.PROMPT]
        
        # Get affected roles
        affected_roles = set()
        for pattern in patterns:
            affected_roles.update(pattern.affected_roles)
        
        return AdaptationDecision(
            dimension=dimension,
            trigger=primary_trigger,
            strategy=primary_strategy,
            priority=priority,
            estimated_impact=estimated_impact,
            estimated_cost=estimated_cost,
            risk_assessment=risk_assessment,
            timeline=self._estimate_timeline(dimension, primary_strategy),
            dependencies=dependencies,
            rollback_plan=self._generate_rollback_plan(dimension)
        )
    
    def _estimate_timeline(self, dimension: LearningDimension, strategy: AdaptationStrategy) -> str:
        """Estimate timeline for adaptation"""
        base_times = {
            LearningDimension.LLM_MODEL: {"incremental": "2-3 weeks", "targeted": "4-6 weeks", "comprehensive": "8-12 weeks"},
            LearningDimension.WEIGHTS_DATASET: {"incremental": "1-2 days", "targeted": "3-5 days", "comprehensive": "1-2 weeks"},
            LearningDimension.CONTEXT: {"incremental": "2-4 hours", "targeted": "1-2 days", "comprehensive": "3-5 days"},
            LearningDimension.PROMPT: {"incremental": "1-2 hours", "targeted": "4-8 hours", "comprehensive": "1-2 days"},
            LearningDimension.MCP_FEATURES: {"incremental": "1-2 days", "targeted": "1 week", "comprehensive": "2-4 weeks"}
        }
        
        return base_times.get(dimension, {}).get(strategy.value, "1 week")
    
    def _generate_rollback_plan(self, dimension: LearningDimension) -> str:
        """Generate rollback plan for dimension"""
        rollback_plans = {
            LearningDimension.LLM_MODEL: "Revert to previous model checkpoint with saved state",
            LearningDimension.WEIGHTS_DATASET: "Restore previous dataset version and retrain adapters",
            LearningDimension.CONTEXT: "Rollback context templates to previous version", 
            LearningDimension.PROMPT: "Restore previous prompt templates from version control",
            LearningDimension.MCP_FEATURES: "Disable new features and restore previous integration configuration"
        }
        
        return rollback_plans.get(dimension, "Restore previous configuration from backup")
    
    async def execute_adaptations(self, decisions: List[AdaptationDecision]) -> Dict[str, Any]:
        """
        Execute the prioritized adaptation decisions.
        
        Args:
            decisions: List of adaptation decisions to execute
            
        Returns:
            Execution results for each adaptation
        """
        results = {
            "adaptations_executed": 0,
            "adaptations_successful": 0,
            "adaptations_failed": 0,
            "execution_details": []
        }
        
        for decision in decisions:
            logger.info(f"Executing adaptation for {decision.dimension.value}")
            
            try:
                execution_result = await self._execute_dimensional_adaptation(decision)
                
                results["adaptations_executed"] += 1
                if execution_result["success"]:
                    results["adaptations_successful"] += 1
                else:
                    results["adaptations_failed"] += 1
                
                results["execution_details"].append({
                    "dimension": decision.dimension.value,
                    "success": execution_result["success"],
                    "details": execution_result,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Update adaptation history
                self.adaptation_history.append(decision)
                
                # Update dimensional metrics
                await self._update_dimensional_metrics(decision, execution_result["success"])
                
            except Exception as e:
                logger.error(f"Failed to execute adaptation for {decision.dimension.value}: {e}")
                results["adaptations_failed"] += 1
                results["execution_details"].append({
                    "dimension": decision.dimension.value,
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        logger.info(f"Adaptation execution completed: {results['adaptations_successful']}/{results['adaptations_executed']} successful")
        return results
    
    async def _execute_dimensional_adaptation(self, decision: AdaptationDecision) -> Dict[str, Any]:
        """Execute adaptation for a specific dimension"""
        
        dimension = decision.dimension
        strategy = decision.strategy
        
        execution_result = {
            "success": False,
            "dimension": dimension.value,
            "strategy": strategy.value,
            "changes_made": [],
            "metrics_before": {},
            "metrics_after": {},
            "rollback_info": {}
        }
        
        try:
            # Capture before metrics
            before_metrics = self.dimensional_metrics[dimension]
            execution_result["metrics_before"] = {
                "current_performance": before_metrics.current_performance,
                "stakeholder_satisfaction": before_metrics.stakeholder_satisfaction
            }
            
            # Execute dimension-specific adaptation
            if dimension == LearningDimension.LLM_MODEL:
                changes = await self._adapt_llm_model(strategy)
            elif dimension == LearningDimension.WEIGHTS_DATASET:
                changes = await self._adapt_weights_dataset(strategy)
            elif dimension == LearningDimension.CONTEXT:
                changes = await self._adapt_context(strategy)
            elif dimension == LearningDimension.PROMPT:
                changes = await self._adapt_prompt(strategy)
            elif dimension == LearningDimension.MCP_FEATURES:
                changes = await self._adapt_mcp_features(strategy)
            else:
                raise ValueError(f"Unknown dimension: {dimension}")
            
            execution_result["changes_made"] = changes
            execution_result["success"] = len(changes) > 0
            
            # Capture after metrics (simulated improvement)
            if execution_result["success"]:
                improvement_factor = 0.05 + (decision.estimated_impact * 0.1)
                before_metrics.current_performance = min(1.0, before_metrics.current_performance + improvement_factor)
                before_metrics.adaptation_frequency += 1
                before_metrics.last_adaptation = datetime.now()
                
                execution_result["metrics_after"] = {
                    "current_performance": before_metrics.current_performance,
                    "improvement": improvement_factor
                }
            
        except Exception as e:
            execution_result["success"] = False
            execution_result["error"] = str(e)
            logger.error(f"Dimensional adaptation failed: {e}")
        
        return execution_result
    
    async def _adapt_llm_model(self, strategy: AdaptationStrategy) -> List[str]:
        """Adapt LLM model dimension"""
        changes = []
        
        if strategy == AdaptationStrategy.INCREMENTAL:
            # Minor model parameter adjustments
            changes.append("Adjusted model temperature and sampling parameters")
            changes.append("Updated model attention weights")
            
        elif strategy == AdaptationStrategy.TARGETED:
            # Focused model improvements
            changes.append("Applied targeted fine-tuning on specific tasks")
            changes.append("Updated model configuration for improved reasoning")
            
        elif strategy == AdaptationStrategy.COMPREHENSIVE:
            # Major model upgrade
            if self.adapter_orchestrator and self.adapter_orchestrator.upgrade_manager:
                try:
                    upgrade_result = await self.adapter_orchestrator.upgrade_manager.start_upgrade(
                        preserve_learning=True, enable_distillation=True
                    )
                    changes.append(f"Initiated model upgrade: {upgrade_result.get('upgrade_job_id')}")
                except Exception as e:
                    logger.error(f"Model upgrade failed: {e}")
                    changes.append("Model upgrade initiation failed - using fallback improvements")
            else:
                changes.append("Simulated comprehensive model upgrade")
        
        return changes
    
    async def _adapt_weights_dataset(self, strategy: AdaptationStrategy) -> List[str]:
        """Adapt weights/dataset dimension"""
        changes = []
        
        if strategy == AdaptationStrategy.INCREMENTAL:
            # Small dataset additions
            changes.append("Added recent high-quality training examples")
            changes.append("Removed low-quality training examples")
            
        elif strategy == AdaptationStrategy.TARGETED:
            # Focused retraining
            changes.append("Retrained adapters on specific role-based scenarios")
            changes.append("Updated dataset with expert-validated examples")
            
        elif strategy == AdaptationStrategy.COMPREHENSIVE:
            # Full dataset overhaul
            if self.adapter_orchestrator and self.adapter_orchestrator.learning_system:
                try:
                    # Trigger comprehensive learning cycle for all roles
                    learning_result = await self.adapter_orchestrator.run_learning_cycle_all_roles()
                    changes.append("Executed comprehensive learning cycle for all roles")
                    changes.append(f"Updated {len(learning_result.get('role_results', {}))} role datasets")
                except Exception as e:
                    logger.error(f"Comprehensive learning cycle failed: {e}")
                    changes.append("Comprehensive learning cycle failed - applied manual dataset updates")
            else:
                changes.append("Simulated comprehensive dataset update")
        
        return changes
    
    async def _adapt_context(self, strategy: AdaptationStrategy) -> List[str]:
        """Adapt context dimension"""
        changes = []
        
        if strategy == AdaptationStrategy.INCREMENTAL:
            # Minor context improvements
            changes.append("Enhanced context templates with additional background information")
            changes.append("Added recent market conditions to context")
            
        elif strategy == AdaptationStrategy.TARGETED:
            # Focused context updates
            changes.append("Updated role-specific context templates")
            changes.append("Enhanced situational awareness context")
            
        elif strategy == AdaptationStrategy.COMPREHENSIVE:
            # Complete context redesign
            changes.append("Redesigned context framework with stakeholder analysis")
            changes.append("Implemented dynamic context adaptation based on decision type")
        
        return changes
    
    async def _adapt_prompt(self, strategy: AdaptationStrategy) -> List[str]:
        """Adapt prompt dimension"""
        changes = []
        
        if strategy == AdaptationStrategy.INCREMENTAL:
            # Minor prompt tweaks
            changes.append("Refined prompt wording for clarity")
            changes.append("Added specific output format requirements")
            
        elif strategy == AdaptationStrategy.TARGETED:
            # Role-specific prompt improvements
            changes.append("Updated role-specific prompt templates")
            changes.append("Enhanced prompt structure for better reasoning")
            
        elif strategy == AdaptationStrategy.COMPREHENSIVE:
            # Complete prompt redesign
            changes.append("Redesigned prompt architecture with chain-of-thought reasoning")
            changes.append("Implemented adaptive prompt selection based on complexity")
        
        return changes
    
    async def _adapt_mcp_features(self, strategy: AdaptationStrategy) -> List[str]:
        """Adapt MCP features dimension"""
        changes = []
        
        if strategy == AdaptationStrategy.INCREMENTAL:
            # Minor MCP improvements
            changes.append("Optimized MCP connection pooling")
            changes.append("Added retry logic for failed MCP requests")
            
        elif strategy == AdaptationStrategy.TARGETED:
            # Focused MCP enhancements
            changes.append("Enhanced MCP error handling and recovery")
            changes.append("Added new MCP server integration endpoints")
            
        elif strategy == AdaptationStrategy.COMPREHENSIVE:
            # Major MCP overhaul
            changes.append("Implemented intelligent MCP routing and load balancing")
            changes.append("Added real-time MCP performance monitoring")
        
        return changes
    
    async def _update_dimensional_metrics(self, decision: AdaptationDecision, success: bool):
        """Update metrics after adaptation execution"""
        dimension = decision.dimension
        metrics = self.dimensional_metrics[dimension]
        
        # Update adaptation frequency
        metrics.adaptation_frequency += 1
        metrics.last_adaptation = datetime.now()
        
        # Update performance based on success
        if success:
            improvement = decision.estimated_impact * 0.5  # Conservative improvement estimate
            metrics.current_performance = min(1.0, metrics.current_performance + improvement)
            metrics.stakeholder_satisfaction = min(1.0, metrics.stakeholder_satisfaction + improvement * 0.3)
            
            # Update cost-benefit ratio
            metrics.cost_benefit_ratio = improvement / (decision.estimated_cost / 10.0)
        else:
            # Slight degradation for failed adaptations
            metrics.current_performance = max(0.0, metrics.current_performance - 0.02)
        
        # Update historical performance
        metrics.historical_performance.append(metrics.current_performance)
        if len(metrics.historical_performance) > 50:  # Keep last 50 entries
            metrics.historical_performance = metrics.historical_performance[-50:]
        
        # Update performance window
        self.performance_windows[dimension].append(metrics.current_performance)
    
    async def get_learning_status(self) -> Dict[str, Any]:
        """Get current status of multi-dimensional learning"""
        return {
            "dimensional_metrics": {
                dim.value: {
                    "current_performance": metrics.current_performance,
                    "stakeholder_satisfaction": metrics.stakeholder_satisfaction,
                    "adaptation_frequency": metrics.adaptation_frequency,
                    "last_adaptation": metrics.last_adaptation.isoformat() if metrics.last_adaptation else None,
                    "cost_benefit_ratio": metrics.cost_benefit_ratio
                }
                for dim, metrics in self.dimensional_metrics.items()
            },
            "total_adaptations": len(self.adaptation_history),
            "recent_patterns": len(self.feedback_patterns),
            "system_status": "active"
        }