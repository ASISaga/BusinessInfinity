"""
CEO Agent - Refactored for Clean AOS Separation

This module demonstrates proper extension of BusinessAgent for
domain-specific business logic. It shows the clean separation:
- AOS provides infrastructure (lifecycle, messaging, decisions)
- BusinessAgent provides business capabilities (KPIs, analytics)
- CEO provides domain expertise (strategic leadership)
"""

from typing import Dict, Any, List
from .business_agent_refactored import BusinessAgent


class ChiefExecutiveOfficerRefactored(BusinessAgent):
    """
    Chief Executive Officer - Strategic Leadership and Executive Decision-Making
    
    Responsibilities (Business-Specific):
    - Overall strategic direction and vision
    - Executive decision-making and leadership
    - Stakeholder management and communications
    - Performance oversight and accountability
    - Corporate governance and compliance
    - Crisis management and strategic pivots
    
    Infrastructure (Provided by AOS):
    - Agent lifecycle management
    - Message routing and handling
    - Decision collaboration patterns
    - State persistence
    - Health monitoring
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            agent_id="bi_ceo",
            name="Business Infinity CEO",
            role="CEO",
            domain="executive_leadership",
            config=config
        )
    
    def _define_domain_expertise(self) -> List[str]:
        """Define CEO's areas of expertise."""
        return [
            "strategic_leadership",
            "executive_decision_making",
            "stakeholder_management",
            "corporate_governance",
            "crisis_management",
            "strategic_planning",
            "performance_management",
            "organizational_development",
            "investor_relations",
            "board_management",
            "change_management",
            "vision_setting",
            "market_positioning",
            "competitive_strategy"
        ]
    
    def _define_business_kpis(self) -> Dict[str, Any]:
        """Define CEO-specific KPIs."""
        return {
            "strategic_decision_quality": {
                "target": 90.0,
                "unit": "score",
                "current": 0.0,
                "description": "Quality of strategic decisions made"
            },
            "stakeholder_satisfaction": {
                "target": 85.0,
                "unit": "score",
                "current": 0.0,
                "description": "Overall stakeholder satisfaction rating"
            },
            "company_performance": {
                "target": 80.0,
                "unit": "score",
                "current": 0.0,
                "description": "Overall company performance index"
            },
            "leadership_effectiveness": {
                "target": 88.0,
                "unit": "score",
                "current": 0.0,
                "description": "Leadership effectiveness rating"
            },
            "crisis_response_time": {
                "target": 120.0,
                "unit": "minutes",
                "current": 0.0,
                "description": "Average time to respond to crises"
            },
            "board_engagement": {
                "target": 90.0,
                "unit": "score",
                "current": 0.0,
                "description": "Board of directors engagement score"
            },
            "strategic_alignment": {
                "target": 85.0,
                "unit": "score",
                "current": 0.0,
                "description": "Alignment of initiatives with strategy"
            },
            "employee_engagement": {
                "target": 80.0,
                "unit": "score",
                "current": 0.0,
                "description": "Overall employee engagement"
            }
        }
    
    def _define_business_decision_framework(self) -> Dict[str, Any]:
        """Define CEO's decision-making framework."""
        return {
            "decision_criteria": [
                "strategic_alignment",
                "stakeholder_impact",
                "financial_performance",
                "competitive_advantage",
                "risk_management",
                "organizational_capability",
                "market_positioning",
                "long_term_value_creation"
            ],
            "evaluation_method": "executive_scorecard",
            "consensus_requirement": False,  # CEO has final authority
            "escalation_threshold": 0.2,  # Lower threshold - CEO is escalation point
            "decision_matrix_weights": {
                "strategic_alignment": 0.25,
                "stakeholder_impact": 0.20,
                "financial_performance": 0.20,
                "competitive_advantage": 0.15,
                "risk_management": 0.10,
                "organizational_capability": 0.05,
                "market_positioning": 0.05
            },
            "consultation_required": [
                "major_strategic_shifts",
                "large_investments",
                "organizational_restructuring",
                "market_entry_exit",
                "crisis_response"
            ]
        }
    
    def _summarize_context(self, context: Dict[str, Any]) -> str:
        """Provide executive summary of context."""
        context_type = context.get("type", "general")
        priority = context.get("priority", "medium")
        
        return f"Executive analysis: {context_type} decision (priority: {priority})"
    
    async def _generate_insights(self, context: Dict[str, Any]) -> List[str]:
        """Generate strategic insights from CEO perspective."""
        insights = []
        
        # Strategic alignment insight
        if "strategy" in context:
            insights.append(
                f"Strategic alignment: Evaluating impact on {context.get('strategy', 'overall strategy')}"
            )
        
        # Stakeholder impact insight
        if "stakeholders" in context:
            insights.append(
                f"Stakeholder consideration: Affects {len(context.get('stakeholders', []))} stakeholder groups"
            )
        
        # Market positioning insight
        if "market" in context or "competitive" in context:
            insights.append(
                "Market impact: Analyzing competitive positioning and market dynamics"
            )
        
        # Add general leadership insight
        insights.append(
            "Leadership perspective: Assessing long-term value creation and organizational impact"
        )
        
        return insights
    
    async def _identify_risks(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify strategic and executive risks."""
        risks = []
        
        # Strategic misalignment risk
        risks.append({
            "type": "strategic",
            "description": "Potential strategic misalignment with long-term goals",
            "severity": "medium",
            "mitigation": "Align with strategic planning framework"
        })
        
        # Stakeholder risk
        if context.get("stakeholders"):
            risks.append({
                "type": "stakeholder",
                "description": "Impact on stakeholder relationships and trust",
                "severity": "high",
                "mitigation": "Engage stakeholders early and transparently"
            })
        
        # Execution risk
        risks.append({
            "type": "execution",
            "description": "Organizational capability to execute decision",
            "severity": "medium",
            "mitigation": "Assess resource availability and capability gaps"
        })
        
        return risks
    
    async def _identify_opportunities(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify strategic opportunities."""
        opportunities = []
        
        # Value creation opportunity
        opportunities.append({
            "type": "value_creation",
            "description": "Potential for long-term value creation and growth",
            "impact": "high"
        })
        
        # Competitive advantage
        if "market" in context or "competitive" in context:
            opportunities.append({
                "type": "competitive",
                "description": "Opportunity to strengthen competitive position",
                "impact": "medium"
            })
        
        # Organizational development
        opportunities.append({
            "type": "organizational",
            "description": "Opportunity to enhance organizational capability",
            "impact": "medium"
        })
        
        return opportunities
    
    async def _generate_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate executive recommendations."""
        recommendations = []
        
        # Strategic alignment recommendation
        recommendations.append({
            "priority": "high",
            "category": "strategic",
            "recommendation": "Ensure alignment with long-term strategic objectives",
            "rationale": "Strategic coherence is critical for sustained success"
        })
        
        # Stakeholder engagement recommendation
        recommendations.append({
            "priority": "high",
            "category": "stakeholder",
            "recommendation": "Proactive stakeholder communication and engagement",
            "rationale": "Maintaining stakeholder trust and support"
        })
        
        # Risk mitigation recommendation
        recommendations.append({
            "priority": "medium",
            "category": "risk",
            "recommendation": "Implement comprehensive risk mitigation plan",
            "rationale": "Prudent risk management is essential"
        })
        
        # Execution planning recommendation
        recommendations.append({
            "priority": "medium",
            "category": "execution",
            "recommendation": "Develop detailed execution plan with milestones",
            "rationale": "Effective execution determines success"
        })
        
        return recommendations
    
    async def provide_strategic_guidance(
        self,
        topic: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Provide strategic guidance on a topic.
        
        Args:
            topic: Strategic topic or question
            context: Relevant context
            
        Returns:
            Strategic guidance with analysis and recommendations
        """
        # Analyze the context
        analysis = await self.analyze_business_context({
            **context,
            "topic": topic,
            "type": "strategic_guidance"
        })
        
        # Provide guidance
        guidance = {
            "topic": topic,
            "analysis": analysis,
            "strategic_direction": self._determine_strategic_direction(topic, context),
            "key_considerations": analysis.get("insights", []),
            "risks_to_address": analysis.get("risks", []),
            "opportunities_to_pursue": analysis.get("opportunities", []),
            "recommended_actions": analysis.get("recommendations", []),
            "timeline": "To be determined based on urgency and resources",
            "success_metrics": self._define_success_metrics(topic)
        }
        
        return guidance
    
    def _determine_strategic_direction(self, topic: str, context: Dict[str, Any]) -> str:
        """Determine strategic direction for a topic."""
        # Business-specific logic for strategic direction
        return f"Strategic direction for {topic}: Focus on long-term value creation and sustainable growth"
    
    def _define_success_metrics(self, topic: str) -> List[str]:
        """Define success metrics for strategic initiative."""
        return [
            "Strategic alignment score",
            "Stakeholder satisfaction",
            "ROI and value creation",
            "Market position improvement",
            "Organizational capability enhancement"
        ]


# Convenience function for creating CEO agent
def create_ceo(config: Dict[str, Any] = None) -> ChiefExecutiveOfficerRefactored:
    """
    Create and configure a CEO agent.
    
    Args:
        config: Optional configuration
        
    Returns:
        Configured CEO agent
    """
    return ChiefExecutiveOfficerRefactored(config=config)
