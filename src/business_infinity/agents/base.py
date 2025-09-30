"""
Base Business Agent

Base business agent with business-specific capabilities that extends
AOS Agent with:
- Business intelligence and context awareness
- KPI tracking and performance metrics
- Integration with Business Infinity analytics
- Business-specific decision frameworks
- Domain expertise and specialization
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import from existing AOS structure for now
try:
    from aos.agents import Agent
    from aos.messaging import Message, MessageType, MessagePriority
except ImportError:
    # Fall back to existing structure
    from RealmOfAgents.AgentOperatingSystem.Agent import Agent
    
    # Create placeholder classes for messaging
    from enum import Enum
    
    class MessageType(Enum):
        ANALYSIS = "analysis"
        DECISION = "decision"
        REQUEST = "request"
        RESPONSE = "response"
    
    class MessagePriority(Enum):
        LOW = "low"
        NORMAL = "normal"
        HIGH = "high"
        URGENT = "urgent"
    
    class Message:
        def __init__(self, sender_id, recipient_id, message_type, content, priority=MessagePriority.NORMAL):
            self.sender_id = sender_id
            self.recipient_id = recipient_id
            self.message_type = message_type
            self.content = content
            self.priority = priority


class BusinessAgent(Agent):
    """
    Base Business Agent extending AOS Agent with business capabilities.
    
    Provides business-specific functionality including:
    - Domain expertise and specialization
    - Business KPI tracking
    - Performance metrics collection
    - Business decision frameworks
    - Integration with business analytics
    """
    
    def __init__(self, 
                 agent_id: str,
                 name: str,
                 role: str, 
                 domain: str,
                 config: Dict[str, Any] = None):
        """
        Initialize Business Agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name
            role: Business role (CEO, CTO, etc.)
            domain: Domain of expertise
            config: Configuration dictionary
        """
        super().__init__(
            agent_id=agent_id,
            name=name,
            config=config
        )
        
        self.role = role
        self.domain = domain
        self.company_context = config.get("company_context", {}) if config else {}
        self.analytics_engine = config.get("analytics_engine") if config else None
        self.workflow_engine = config.get("workflow_engine") if config else None
        
        # Business-specific attributes
        self.domain_expertise = self._define_domain_expertise()
        self.business_kpis = self._define_business_kpis()
        self.decision_framework = self._define_business_decision_framework()
        
        # Collaboration and performance tracking
        self.collaboration_network = []
        self.decisions_made = []
        self.performance_metrics = {}
        self.contribution_history = []
        
        self.logger = logging.getLogger(f"BusinessAgent.{role}")

    def _define_domain_expertise(self) -> List[str]:
        """Define domain expertise areas. Override in subclasses."""
        return ["business_operations", "strategic_thinking", "decision_making"]

    def _define_business_kpis(self) -> Dict[str, Any]:
        """Define business KPIs to track. Override in subclasses."""
        return {
            "decision_quality": {"target": 85.0, "unit": "score", "current": 0.0},
            "response_time": {"target": 300.0, "unit": "seconds", "current": 0.0},
            "collaboration_effectiveness": {"target": 80.0, "unit": "score", "current": 0.0},
            "business_impact": {"target": 75.0, "unit": "score", "current": 0.0}
        }

    def _define_business_decision_framework(self) -> Dict[str, Any]:
        """Define business decision framework. Override in subclasses."""
        return {
            "decision_criteria": [
                "business_impact", 
                "risk_level", 
                "resource_requirements",
                "strategic_alignment",
                "market_opportunity"
            ],
            "evaluation_method": "multi_criteria_analysis",
            "consensus_requirement": True,
            "escalation_threshold": 0.3,
            "decision_matrix_weights": {
                "business_impact": 0.3,
                "risk_level": 0.2,
                "resource_requirements": 0.2,
                "strategic_alignment": 0.2,
                "market_opportunity": 0.1
            }
        }

    async def analyze_business_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze business context using domain expertise.
        
        Args:
            context: Business context to analyze
            
        Returns:
            Analysis result with recommendations and risk assessment
        """
        try:
            # Perform domain-specific analysis
            domain_analysis = await self._perform_domain_analysis(context)
            
            # Generate recommendations
            recommendations = await self._generate_domain_recommendations(domain_analysis)
            
            # Assess risks and opportunities
            risk_assessment = await self._assess_risks_and_opportunities(context)
            
            # Calculate confidence score
            confidence = await self._calculate_analysis_confidence(domain_analysis)
            
            # Create analysis result
            analysis_result = {
                "agent_id": self.agent_id,
                "agent_role": self.role,
                "domain": self.domain,
                "analysis": domain_analysis,
                "recommendations": recommendations,
                "risk_assessment": risk_assessment,
                "confidence": confidence,
                "reasoning": f"Based on {self.domain} expertise and current business context",
                "timestamp": datetime.utcnow().isoformat(),
                "expertise_areas": self.domain_expertise
            }
            
            # Store contribution
            self.contribution_history.append(analysis_result)
            await self._update_performance_metrics("analysis_completed", 1)
            
            # Send analysis to business system
            await self._send_business_message(
                MessageType.ANALYSIS,
                analysis_result,
                priority=MessagePriority.HIGH
            )
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Business context analysis failed: {e}")
            error_result = {
                "agent_id": self.agent_id,
                "agent_role": self.role,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            await self._update_performance_metrics("analysis_failed", 1)
            return error_result

    async def _perform_domain_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform domain-specific analysis. Override in subclasses.
        
        Args:
            context: Business context
            
        Returns:
            Domain analysis results
        """
        return {
            "domain_perspective": f"General {self.domain} analysis",
            "key_insights": ["Standard business insight"],
            "data_quality": "sufficient",
            "analysis_depth": "basic",
            "market_conditions": "stable",
            "competitive_landscape": "moderate"
        }

    async def _generate_domain_recommendations(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate domain-specific recommendations. Override in subclasses.
        
        Args:
            analysis: Domain analysis results
            
        Returns:
            Recommendations with implementation details
        """
        return {
            "primary_recommendation": "Standard business recommendation",
            "alternative_options": ["Option A", "Option B", "Option C"],
            "implementation_priority": "medium",
            "resource_requirements": {
                "budget": "moderate",
                "timeline": "3-6 months",
                "personnel": "existing team"
            },
            "success_metrics": [
                "increased_efficiency",
                "cost_reduction",
                "customer_satisfaction"
            ],
            "implementation_steps": [
                "Phase 1: Planning",
                "Phase 2: Execution", 
                "Phase 3: Monitoring"
            ]
        }

    async def _assess_risks_and_opportunities(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess risks and opportunities. Override in subclasses.
        
        Args:
            context: Business context
            
        Returns:
            Risk and opportunity assessment
        """
        return {
            "risks": [
                {
                    "risk": "Market volatility",
                    "probability": 0.3,
                    "impact": "medium",
                    "mitigation": "Diversification strategy"
                },
                {
                    "risk": "Resource constraints",
                    "probability": 0.4,
                    "impact": "high",
                    "mitigation": "Resource optimization"
                }
            ],
            "opportunities": [
                {
                    "opportunity": "Market expansion",
                    "potential": "high",
                    "timeline": "6-12 months",
                    "investment_required": "moderate"
                },
                {
                    "opportunity": "Technology adoption",
                    "potential": "medium",
                    "timeline": "3-6 months",
                    "investment_required": "low"
                }
            ],
            "mitigation_strategies": [
                "Risk monitoring dashboard",
                "Contingency planning",
                "Regular strategy reviews"
            ],
            "opportunity_capture_plan": [
                "Market research",
                "Pilot programs",
                "Gradual rollout"
            ]
        }

    async def _calculate_analysis_confidence(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate confidence score for analysis.
        
        Args:
            analysis: Analysis results
            
        Returns:
            Confidence score between 0 and 1
        """
        # Factors affecting confidence
        data_quality = analysis.get("data_quality", "sufficient")
        analysis_depth = analysis.get("analysis_depth", "basic")
        
        confidence = 0.7  # Base confidence
        
        # Adjust based on data quality
        if data_quality == "excellent":
            confidence += 0.2
        elif data_quality == "good":
            confidence += 0.1
        elif data_quality == "poor":
            confidence -= 0.2
        
        # Adjust based on analysis depth
        if analysis_depth == "comprehensive":
            confidence += 0.15
        elif analysis_depth == "detailed":
            confidence += 0.1
        elif analysis_depth == "basic":
            confidence -= 0.1
        
        # Ensure confidence is within bounds
        return max(0.0, min(1.0, confidence))

    async def make_business_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a business decision using the decision framework.
        
        Args:
            decision_context: Context for the decision
            
        Returns:
            Decision result with rationale
        """
        try:
            # Analyze the decision context
            analysis = await self.analyze_business_context(decision_context)
            
            # Apply decision framework
            decision_result = await self._apply_decision_framework(
                decision_context, 
                analysis
            )
            
            # Store decision
            self.decisions_made.append(decision_result)
            await self._update_performance_metrics("decisions_made", 1)
            
            # Send decision to business system
            await self._send_business_message(
                MessageType.DECISION,
                decision_result,
                priority=MessagePriority.HIGH
            )
            
            return decision_result
            
        except Exception as e:
            self.logger.error(f"Business decision failed: {e}")
            return {
                "agent_id": self.agent_id,
                "decision": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _apply_decision_framework(self, 
                                      context: Dict[str, Any], 
                                      analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply the business decision framework.
        
        Args:
            context: Decision context
            analysis: Business analysis
            
        Returns:
            Decision result
        """
        framework = self.decision_framework
        criteria = framework["decision_criteria"]
        weights = framework["decision_matrix_weights"]
        
        # Score each criterion
        scores = {}
        for criterion in criteria:
            scores[criterion] = await self._score_criterion(criterion, context, analysis)
        
        # Calculate weighted score
        weighted_score = sum(
            scores[criterion] * weights.get(criterion, 0.1)
            for criterion in criteria
        )
        
        # Make decision based on score
        decision = "approve" if weighted_score >= 0.6 else "reject"
        if 0.4 <= weighted_score < 0.6:
            decision = "conditional"
        
        return {
            "agent_id": self.agent_id,
            "agent_role": self.role,
            "decision": decision,
            "weighted_score": weighted_score,
            "criterion_scores": scores,
            "rationale": f"Decision based on {framework['evaluation_method']} with score {weighted_score:.2f}",
            "framework_used": framework,
            "confidence": analysis.get("confidence", 0.7),
            "timestamp": datetime.utcnow().isoformat(),
            "requires_consensus": framework["consensus_requirement"]
        }

    async def _score_criterion(self, criterion: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> float:
        """Score a specific decision criterion."""
        # Default scoring logic - override in subclasses
        base_score = 0.5
        
        if criterion == "business_impact":
            impact = context.get("expected_impact", "medium")
            if impact == "high":
                base_score = 0.8
            elif impact == "medium":
                base_score = 0.6
            elif impact == "low":
                base_score = 0.4
        
        elif criterion == "risk_level":
            risk = context.get("risk_level", "medium")
            if risk == "low":
                base_score = 0.8
            elif risk == "medium":
                base_score = 0.6
            elif risk == "high":
                base_score = 0.3
        
        elif criterion == "resource_requirements":
            resources = context.get("resources_required", "medium")
            if resources == "low":
                base_score = 0.8
            elif resources == "medium":
                base_score = 0.6
            elif resources == "high":
                base_score = 0.4
        
        return min(1.0, max(0.0, base_score))

    async def _send_business_message(self, 
                                   message_type: MessageType,
                                   content: Dict[str, Any],
                                   priority: MessagePriority = MessagePriority.NORMAL):
        """Send a message to the business system."""
        message = Message(
            sender_id=self.agent_id,
            recipient_id="business_system",
            message_type=message_type,
            content=content,
            priority=priority
        )
        await self.send_message(message)

    async def _update_performance_metrics(self, metric_name: str, value: float):
        """Update performance metrics."""
        if metric_name not in self.performance_metrics:
            self.performance_metrics[metric_name] = {
                "value": 0.0,
                "count": 0,
                "last_updated": datetime.utcnow()
            }
        
        metric = self.performance_metrics[metric_name]
        metric["value"] += value
        metric["count"] += 1
        metric["last_updated"] = datetime.utcnow()

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for this agent."""
        return {
            "agent_id": self.agent_id,
            "agent_role": self.role,
            "domain": self.domain,
            "kpis": self.business_kpis,
            "performance_metrics": self.performance_metrics,
            "decisions_count": len(self.decisions_made),
            "contributions_count": len(self.contribution_history),
            "collaboration_network_size": len(self.collaboration_network),
            "domain_expertise": self.domain_expertise,
            "last_activity": datetime.utcnow().isoformat()
        }

    async def get_business_context(self) -> Dict[str, Any]:
        """Get business context for this agent."""
        return {
            "company_context": self.company_context,
            "role": self.role,
            "domain": self.domain,
            "expertise": self.domain_expertise,
            "decision_framework": self.decision_framework,
            "status": self.status,
            "performance": await self.get_performance_summary()
        }