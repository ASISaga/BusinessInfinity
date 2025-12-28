"""
Business Agent Base - Refactored for Clean AOS Separation

This module defines the BusinessAgent class that extends AOS LeadershipAgent
with business-specific capabilities. This is the proper pattern for building
business logic on top of generic AOS infrastructure.

Architecture:
    AOS LeadershipAgent (generic infrastructure)
        ↓ extends
    BusinessAgent (business-specific capabilities)
        ↓ extends
    CEO, CFO, CTO, etc. (domain-specific implementations)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Import from AgentOperatingSystem (infrastructure layer)
# NOTE: These imports will work once AOS is refactored with the new structure
try:
    from AgentOperatingSystem.agents import LeadershipAgent
    AOS_AVAILABLE = True
except ImportError:
    # Temporary fallback during refactoring
    AOS_AVAILABLE = False
    
    class LeadershipAgent:
        """Temporary placeholder for AOS LeadershipAgent during refactoring"""
        def __init__(self, agent_id: str, name: str, role: str, config: Dict[str, Any] = None):
            self.agent_id = agent_id
            self.name = name
            self.role = role
            self.config = config or {}


class BusinessAgent:
    """
    Base class for all BusinessInfinity agents.
    
    Extends AOS LeadershipAgent with business-specific capabilities:
    - Business intelligence and domain expertise
    - KPI tracking and performance metrics
    - Business analytics integration
    - Domain-specific decision frameworks
    - Stakeholder management
    
    This class focuses ONLY on business logic and uses AOS for:
    - Agent lifecycle (from BaseAgent)
    - Decision-making patterns (from LeadershipAgent)
    - Message routing and handling (from BaseAgent)
    - State persistence (via AOS storage)
    - Health monitoring (from BaseAgent)
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        domain: str,
        config: Dict[str, Any] = None
    ):
        """
        Initialize business agent.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable agent name
            role: Business role (CEO, CFO, CTO, etc.)
            domain: Domain expertise area
            config: Optional configuration
        """
        # Call AOS LeadershipAgent init
        super().__init__(agent_id, name, role, config)
        
        # Business-specific attributes
        self.domain = domain
        self.expertise_areas = self._define_domain_expertise()
        self.business_kpis = self._define_business_kpis()
        self.decision_framework = self._define_business_decision_framework()
        self.performance_history = []
        self.logger = logging.getLogger(f"bi.agent.{agent_id}")
    
    def _define_domain_expertise(self) -> List[str]:
        """
        Define areas of domain expertise.
        Override in subclasses to specify agent's expertise.
        
        Returns:
            List of expertise area identifiers
        """
        return []
    
    def _define_business_kpis(self) -> Dict[str, Any]:
        """
        Define business KPIs this agent tracks.
        Override in subclasses to specify relevant KPIs.
        
        Returns:
            Dictionary of KPI definitions with targets and units
        """
        return {}
    
    def _define_business_decision_framework(self) -> Dict[str, Any]:
        """
        Define the decision-making framework for this agent.
        Override in subclasses to specify decision criteria.
        
        Returns:
            Decision framework configuration
        """
        return {
            "decision_criteria": [],
            "evaluation_method": "scorecard",
            "consensus_requirement": True,
            "escalation_threshold": 0.3
        }
    
    async def analyze_business_context(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze business context using domain expertise.
        
        Args:
            context: Business context to analyze
            
        Returns:
            Analysis with insights, risks, opportunities, recommendations
        """
        analysis = {
            "agent_id": getattr(self, 'agent_id', 'unknown'),
            "role": getattr(self, 'role', 'unknown'),
            "domain": self.domain,
            "timestamp": datetime.utcnow().isoformat(),
            "context_summary": self._summarize_context(context),
            "insights": await self._generate_insights(context),
            "risks": await self._identify_risks(context),
            "opportunities": await self._identify_opportunities(context),
            "recommendations": await self._generate_recommendations(context),
            "confidence": 0.0
        }
        
        return analysis
    
    def _summarize_context(self, context: Dict[str, Any]) -> str:
        """Summarize business context. Override in subclasses."""
        return f"Business context analysis for {self.domain}"
    
    async def _generate_insights(self, context: Dict[str, Any]) -> List[str]:
        """Generate business insights. Override in subclasses."""
        return []
    
    async def _identify_risks(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify business risks. Override in subclasses."""
        return []
    
    async def _identify_opportunities(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify business opportunities. Override in subclasses."""
        return []
    
    async def _generate_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate business recommendations. Override in subclasses."""
        return []
    
    async def make_business_decision(
        self,
        decision_context: Dict[str, Any],
        stakeholders: List[str] = None
    ) -> Dict[str, Any]:
        """
        Make a business decision using the agent's decision framework.
        Uses AOS LeadershipAgent's make_decision with business logic.
        
        Args:
            decision_context: Context for the decision
            stakeholders: Optional stakeholder agents to consult
            
        Returns:
            Business decision with rationale and confidence
        """
        # Analyze business context first
        analysis = await self.analyze_business_context(decision_context)
        
        # Enhance context with business analysis
        enhanced_context = {
            **decision_context,
            "business_analysis": analysis,
            "framework": self.decision_framework,
            "domain_expertise": self.expertise_areas
        }
        
        # Use AOS decision-making (when available)
        if AOS_AVAILABLE and hasattr(super(), 'make_decision'):
            decision = await super().make_decision(
                context=enhanced_context,
                stakeholders=stakeholders,
                mode=self.decision_framework.get("consensus_requirement") and "consensus" or "autonomous"
            )
        else:
            # Temporary fallback
            decision = {
                "decision": "pending",
                "rationale": "AOS decision-making not available",
                "confidence": 0.0
            }
        
        # Add business-specific metadata
        decision["business_metadata"] = {
            "domain": self.domain,
            "expertise_applied": self.expertise_areas,
            "kpis_considered": list(self.business_kpis.keys()),
            "analysis": analysis
        }
        
        return decision
    
    def update_kpi(self, kpi_name: str, value: float) -> bool:
        """
        Update a KPI value.
        
        Args:
            kpi_name: Name of the KPI to update
            value: New value
            
        Returns:
            True if successful
        """
        if kpi_name in self.business_kpis:
            self.business_kpis[kpi_name]["current"] = value
            self.business_kpis[kpi_name]["last_updated"] = datetime.utcnow().isoformat()
            
            # Record in performance history
            self.performance_history.append({
                "kpi": kpi_name,
                "value": value,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return True
        return False
    
    def get_kpi_status(self) -> Dict[str, Any]:
        """
        Get status of all KPIs.
        
        Returns:
            KPI status with current vs target
        """
        status = {}
        for kpi_name, kpi_data in self.business_kpis.items():
            current = kpi_data.get("current", 0.0)
            target = kpi_data.get("target", 0.0)
            
            status[kpi_name] = {
                "current": current,
                "target": target,
                "unit": kpi_data.get("unit", ""),
                "achievement_rate": (current / target * 100) if target > 0 else 0.0,
                "status": "on_track" if current >= target * 0.9 else "needs_attention"
            }
        
        return status
    
    def get_business_metadata(self) -> Dict[str, Any]:
        """
        Get comprehensive business metadata for this agent.
        
        Returns:
            Business metadata including expertise, KPIs, framework
        """
        # Get base metadata from AOS (when available)
        if AOS_AVAILABLE and hasattr(super(), 'get_metadata'):
            base_metadata = super().get_metadata()
        else:
            base_metadata = {
                "agent_id": getattr(self, 'agent_id', 'unknown'),
                "name": getattr(self, 'name', 'unknown'),
                "role": getattr(self, 'role', 'unknown')
            }
        
        # Add business-specific metadata
        business_metadata = {
            **base_metadata,
            "domain": self.domain,
            "expertise_areas": self.expertise_areas,
            "kpis": self.get_kpi_status(),
            "decision_framework": self.decision_framework,
            "performance_summary": {
                "total_decisions": len(self.performance_history),
                "recent_kpis": self.performance_history[-10:] if self.performance_history else []
            }
        }
        
        return business_metadata


# Convenience function for creating business agents
def create_business_agent(
    role: str,
    domain: str,
    config: Dict[str, Any] = None
) -> BusinessAgent:
    """
    Factory function for creating business agents.
    
    Args:
        role: Business role (CEO, CFO, etc.)
        domain: Domain expertise
        config: Optional configuration
        
    Returns:
        Configured BusinessAgent instance
    """
    agent_id = f"bi_{role.lower()}"
    name = f"Business Infinity {role}"
    
    return BusinessAgent(
        agent_id=agent_id,
        name=name,
        role=role,
        domain=domain,
        config=config
    )
