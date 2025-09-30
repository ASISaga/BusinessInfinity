"""
Evaluation Harness for Business Infinity LoRA Adapters

Implements comprehensive evaluation metrics for boardroom agents as defined
in the adapter specifications. Measures role fidelity, leadership clarity,
and conflict resolution capabilities.

Key Metrics:
- Role Fidelity: How well agents maintain their role-specific characteristics
- Leadership Clarity: Quality of executive decision framing and synthesis
- Conflict Index: How well agents handle inter-role tensions and trade-offs
- Response Quality: Overall response coherence and business relevance
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re
import hashlib

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of evaluation metrics"""
    ROLE_FIDELITY = "role_fidelity"
    LEADERSHIP_CLARITY = "leadership_clarity"
    CONFLICT_INDEX = "conflict_index"
    RESPONSE_QUALITY = "response_quality"
    GUARDRAIL_COMPLIANCE = "guardrail_compliance"


class EvaluationLevel(Enum):
    """Levels of evaluation complexity"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class RoleFidelityMetrics:
    """Metrics for role-specific behavior evaluation"""
    vocabulary_consistency: float  # Use of role-specific terms
    kpi_relevance: float  # Mention of appropriate KPIs
    reasoning_style: float  # Matches expected reasoning pattern
    expertise_depth: float  # Depth of domain knowledge
    perspective_alignment: float  # Maintains role perspective
    overall_score: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LeadershipClarityMetrics:
    """Metrics for leadership and decision framing"""
    executive_synthesis: float  # Ability to synthesize complex information
    options_presentation: float  # Clear presentation of alternatives
    risk_assessment: float  # Identification and evaluation of risks
    recommendation_quality: float  # Single, clear recommendation
    action_specificity: float  # Specific actions with owners/timelines
    trade_off_recognition: float  # Recognition of trade-offs
    overall_score: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConflictIndexMetrics:
    """Metrics for handling inter-role conflicts and tensions"""
    tension_recognition: float  # Recognition of role conflicts
    balanced_perspective: float  # Balanced consideration of other roles
    resolution_approach: float  # Constructive conflict resolution
    collaboration_tone: float  # Collaborative vs. competitive tone
    compromise_quality: float  # Quality of compromise solutions
    stakeholder_consideration: float  # Consideration of all stakeholders
    overall_score: float  # Lower = better conflict handling
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GuardrailComplianceMetrics:
    """Metrics for guardrail compliance"""
    role_specific_checks: float  # Role-specific guardrail adherence
    output_schema_compliance: float  # Adherence to output schema
    numeric_consistency: float  # Consistency of numbers and figures
    ethical_guidelines: float  # Adherence to ethical guidelines
    factual_accuracy: float  # Avoidance of fabricated information
    overall_score: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Complete evaluation result for a response"""
    response_id: str
    agent_role: str
    scenario_id: str
    evaluation_level: EvaluationLevel
    role_fidelity: RoleFidelityMetrics
    leadership_clarity: LeadershipClarityMetrics
    conflict_index: ConflictIndexMetrics
    guardrail_compliance: GuardrailComplianceMetrics
    overall_score: float
    evaluation_timestamp: datetime
    evaluator_version: str = "v1.0.0"
    notes: str = ""


@dataclass
class EvaluationScenario:
    """A scenario for evaluating agent responses"""
    id: str
    title: str
    description: str
    context: Dict[str, Any]
    expected_behaviors: Dict[str, List[str]]  # Per role
    difficulty_level: EvaluationLevel
    evaluation_criteria: Dict[str, Any]
    target_roles: List[str]
    created_at: datetime


class EvaluationHarness:
    """
    Comprehensive evaluation system for boardroom agent responses.
    
    Features:
    - Multi-dimensional scoring across role fidelity, leadership clarity, etc.
    - Configurable evaluation scenarios of varying complexity
    - Automated guardrail compliance checking
    - Historical performance tracking and trend analysis
    - Comparative evaluation between different model versions
    """
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "evaluation_data")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # State
        self.evaluation_scenarios: Dict[str, EvaluationScenario] = {}
        self.evaluation_results: List[EvaluationResult] = []
        self.role_vocabularies: Dict[str, List[str]] = {}
        self.role_kpis: Dict[str, List[str]] = {}
        self.guardrail_rules: Dict[str, List[str]] = {}
        
        # Initialize evaluation components
        self._load_evaluation_scenarios()
        self._load_role_definitions()
        self._load_guardrail_rules()
        
        logger.info(f"Evaluation Harness initialized with {len(self.evaluation_scenarios)} scenarios")
    
    def _load_evaluation_scenarios(self):
        """Load predefined evaluation scenarios"""
        try:
            scenarios_path = os.path.join(self.data_dir, "evaluation_scenarios.json")
            if os.path.exists(scenarios_path):
                with open(scenarios_path, 'r') as f:
                    data = json.load(f)
                    for scenario_data in data:
                        scenario = EvaluationScenario(
                            id=scenario_data["id"],
                            title=scenario_data["title"],
                            description=scenario_data["description"],
                            context=scenario_data["context"],
                            expected_behaviors=scenario_data["expected_behaviors"],
                            difficulty_level=EvaluationLevel(scenario_data["difficulty_level"]),
                            evaluation_criteria=scenario_data["evaluation_criteria"],
                            target_roles=scenario_data["target_roles"],
                            created_at=datetime.fromisoformat(scenario_data["created_at"])
                        )
                        self.evaluation_scenarios[scenario.id] = scenario
            else:
                self._generate_default_scenarios()
                
        except Exception as e:
            logger.error(f"Failed to load evaluation scenarios: {e}")
            self._generate_default_scenarios()
    
    def _generate_default_scenarios(self):
        """Generate default evaluation scenarios"""
        default_scenarios = [
            {
                "id": "strategic_expansion",
                "title": "Strategic Market Expansion Decision",
                "description": "The company is considering expanding into a new geographic market with significant investment requirements.",
                "context": {
                    "company_stage": "growth",
                    "current_markets": ["North America", "Europe"],
                    "target_market": "Asia Pacific",
                    "investment_required": "$50M",
                    "timeline": "18 months",
                    "risk_factors": ["regulatory", "competitive", "cultural"]
                },
                "expected_behaviors": {
                    "cfo": ["financial_analysis", "risk_assessment", "roi_calculation"],
                    "cmo": ["market_analysis", "brand_positioning", "customer_segmentation"],
                    "coo": ["operational_readiness", "supply_chain", "local_partnerships"],
                    "founder": ["vision_alignment", "strategic_rationale", "long_term_value"]
                },
                "difficulty_level": "intermediate",
                "evaluation_criteria": {
                    "requires_quantitative_analysis": True,
                    "involves_multiple_stakeholders": True,
                    "has_regulatory_considerations": True
                },
                "target_roles": ["cfo", "cmo", "coo", "founder"]
            },
            {
                "id": "product_pivot",
                "title": "Major Product Pivot Decision", 
                "description": "Customer feedback suggests the current product direction may not be optimal. The team is considering a significant pivot.",
                "context": {
                    "current_product": "B2B SaaS Platform",
                    "proposed_pivot": "B2C Mobile App",
                    "customer_feedback": "mixed",
                    "market_opportunity": "large but uncertain",
                    "development_resources": "limited",
                    "runway": "12 months"
                },
                "expected_behaviors": {
                    "cto": ["technical_feasibility", "resource_requirements", "timeline_assessment"],
                    "cmo": ["market_validation", "positioning_strategy", "customer_acquisition"],
                    "ceo": ["strategic_alignment", "stakeholder_communication", "decision_framework"],
                    "investor": ["risk_evaluation", "market_potential", "capital_requirements"]
                },
                "difficulty_level": "advanced",
                "evaluation_criteria": {
                    "high_uncertainty": True,
                    "time_pressure": True,
                    "conflicting_stakeholder_interests": True
                },
                "target_roles": ["cto", "cmo", "ceo", "investor"]
            }
        ]
        
        for scenario_data in default_scenarios:
            scenario = EvaluationScenario(
                id=scenario_data["id"],
                title=scenario_data["title"],
                description=scenario_data["description"],
                context=scenario_data["context"],
                expected_behaviors=scenario_data["expected_behaviors"],
                difficulty_level=EvaluationLevel(scenario_data["difficulty_level"]),
                evaluation_criteria=scenario_data["evaluation_criteria"],
                target_roles=scenario_data["target_roles"],
                created_at=datetime.now()
            )
            self.evaluation_scenarios[scenario.id] = scenario
        
        logger.info(f"Generated {len(default_scenarios)} default evaluation scenarios")
    
    def _load_role_definitions(self):
        """Load role-specific vocabularies and KPIs"""
        self.role_vocabularies = {
            "cfo": ["EBITDA", "cash flow", "ROI", "CAPEX", "OPEX", "runway", "burn rate", 
                   "valuation", "liquidity", "financial model", "sensitivity analysis"],
            "cmo": ["CAC", "LTV", "conversion rate", "brand awareness", "market share",
                   "customer acquisition", "retention", "segmentation", "positioning"],
            "coo": ["operational efficiency", "capacity", "SLA", "process optimization",
                   "resource allocation", "supply chain", "quality metrics"],
            "cto": ["technical architecture", "scalability", "security", "performance",
                   "technical debt", "infrastructure", "API design", "DevOps"],
            "founder": ["vision", "mission", "product-market fit", "strategic direction",
                       "company culture", "long-term value", "competitive advantage"],
            "investor": ["market opportunity", "competitive moat", "scalability potential",
                        "exit strategy", "portfolio fit", "due diligence", "term sheet"]
        }
        
        self.role_kpis = {
            "cfo": ["Revenue Growth", "Gross Margin", "Customer Acquisition Cost",
                   "Monthly Recurring Revenue", "Cash Burn Rate"],
            "cmo": ["Customer Acquisition Cost", "Customer Lifetime Value", "Conversion Rate",
                   "Brand Awareness", "Market Share"],
            "coo": ["Operational Efficiency", "Customer Satisfaction", "Employee Productivity",
                   "Process Cycle Time", "Quality Score"],
            "cto": ["System Uptime", "Response Time", "Security Incidents", "Developer Velocity",
                   "Technical Debt Ratio"],
            "founder": ["Product-Market Fit Score", "Employee Engagement", "Strategic Goal Progress",
                       "Innovation Index", "Company Culture Score"],
            "investor": ["Return on Investment", "Portfolio Performance", "Market Penetration",
                        "Competitive Position", "Exit Potential"]
        }
    
    def _load_guardrail_rules(self):
        """Load guardrail rules for compliance checking"""
        self.guardrail_rules = {
            "founder": [
                "must_link_vision_to_roadmap",
                "must_include_measurable_milestones",
                "no_pure_rhetoric_without_grounding",
                "must_address_cultural_continuity"
            ],
            "investor": [
                "must_include_valuation_impact",
                "must_assess_capital_efficiency",
                "must_consider_liquidity_exit_horizon",
                "no_fabricated_figures",
                "must_ensure_numeric_consistency"
            ],
            "leadership": [
                "must_present_options",
                "must_assess_risks", 
                "must_provide_single_recommendation",
                "must_specify_actions_with_owners",
                "must_highlight_tradeoffs_in_tension"
            ]
        }
    
    async def evaluate_response(self, response_text: str, agent_role: str, 
                              scenario_id: str, response_id: str = None) -> EvaluationResult:
        """
        Comprehensively evaluate an agent response.
        
        Args:
            response_text: The agent's response to evaluate
            agent_role: Role of the responding agent
            scenario_id: ID of the evaluation scenario
            response_id: Optional response identifier
            
        Returns:
            Complete evaluation result
        """
        if response_id is None:
            response_id = f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(response_text.encode()).hexdigest()[:6]}"
        
        scenario = self.evaluation_scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f"Evaluation scenario {scenario_id} not found")
        
        logger.info(f"Evaluating response {response_id} for role {agent_role} on scenario {scenario_id}")
        
        # Evaluate each dimension
        role_fidelity = await self._evaluate_role_fidelity(response_text, agent_role, scenario)
        leadership_clarity = await self._evaluate_leadership_clarity(response_text, agent_role, scenario)
        conflict_index = await self._evaluate_conflict_index(response_text, agent_role, scenario)
        guardrail_compliance = await self._evaluate_guardrail_compliance(response_text, agent_role, scenario)
        
        # Calculate overall score (weighted average)
        overall_score = (
            role_fidelity.overall_score * 0.3 +
            leadership_clarity.overall_score * 0.25 +
            (1.0 - conflict_index.overall_score) * 0.20 +  # Lower conflict index is better
            guardrail_compliance.overall_score * 0.25
        )
        
        result = EvaluationResult(
            response_id=response_id,
            agent_role=agent_role,
            scenario_id=scenario_id,
            evaluation_level=scenario.difficulty_level,
            role_fidelity=role_fidelity,
            leadership_clarity=leadership_clarity,
            conflict_index=conflict_index,
            guardrail_compliance=guardrail_compliance,
            overall_score=overall_score,
            evaluation_timestamp=datetime.now()
        )
        
        self.evaluation_results.append(result)
        
        logger.info(f"Evaluation completed - Overall Score: {overall_score:.3f}")
        return result
    
    async def _evaluate_role_fidelity(self, response_text: str, agent_role: str, 
                                    scenario: EvaluationScenario) -> RoleFidelityMetrics:
        """Evaluate how well the response maintains role-specific characteristics"""
        
        # Vocabulary consistency
        role_vocab = self.role_vocabularies.get(agent_role, [])
        vocab_matches = sum(1 for term in role_vocab if term.lower() in response_text.lower())
        vocabulary_consistency = min(1.0, vocab_matches / max(1, len(role_vocab) * 0.3))
        
        # KPI relevance
        role_kpi_list = self.role_kpis.get(agent_role, [])
        kpi_matches = sum(1 for kpi in role_kpi_list if kpi.lower() in response_text.lower())
        kpi_relevance = min(1.0, kpi_matches / max(1, len(role_kpi_list) * 0.2))
        
        # Reasoning style (pattern-based evaluation)
        reasoning_patterns = {
            "cfo": ["analysis", "financial", "risk", "return", "cost"],
            "cmo": ["market", "customer", "brand", "segment", "positioning"],
            "coo": ["operations", "process", "efficiency", "capacity", "execution"],
            "cto": ["technical", "architecture", "scalability", "security", "performance"],
            "founder": ["vision", "strategy", "long-term", "mission", "value"],
            "investor": ["opportunity", "return", "market", "competitive", "exit"]
        }
        
        patterns = reasoning_patterns.get(agent_role, [])
        pattern_matches = sum(1 for pattern in patterns if pattern in response_text.lower())
        reasoning_style = min(1.0, pattern_matches / max(1, len(patterns) * 0.4))
        
        # Expertise depth (estimated by response length and detail)
        response_length = len(response_text.split())
        expertise_depth = min(1.0, response_length / 200)  # Normalize to 200 words
        
        # Perspective alignment (check for role-specific framing)
        perspective_indicators = {
            "cfo": ["from a financial perspective", "financial impact", "cost-benefit"],
            "cmo": ["from a market perspective", "customer impact", "brand implications"],
            "founder": ["strategic perspective", "company mission", "long-term vision"]
        }
        
        indicators = perspective_indicators.get(agent_role, [])
        perspective_matches = sum(1 for indicator in indicators if indicator in response_text.lower())
        perspective_alignment = min(1.0, perspective_matches / max(1, len(indicators)))
        
        # Overall role fidelity score
        overall_score = (
            vocabulary_consistency * 0.25 +
            kpi_relevance * 0.20 +
            reasoning_style * 0.25 +
            expertise_depth * 0.15 +
            perspective_alignment * 0.15
        )
        
        return RoleFidelityMetrics(
            vocabulary_consistency=vocabulary_consistency,
            kpi_relevance=kpi_relevance,
            reasoning_style=reasoning_style,
            expertise_depth=expertise_depth,
            perspective_alignment=perspective_alignment,
            overall_score=overall_score,
            details={
                "vocab_matches": vocab_matches,
                "kpi_matches": kpi_matches,
                "pattern_matches": pattern_matches,
                "response_length": response_length
            }
        )
    
    async def _evaluate_leadership_clarity(self, response_text: str, agent_role: str,
                                         scenario: EvaluationScenario) -> LeadershipClarityMetrics:
        """Evaluate leadership and decision framing quality"""
        
        response_lower = response_text.lower()
        
        # Executive synthesis (ability to synthesize complex information)
        synthesis_indicators = ["in summary", "overall", "considering all factors", "taking into account"]
        synthesis_score = min(1.0, sum(1 for indicator in synthesis_indicators 
                                     if indicator in response_lower) / 2)
        
        # Options presentation (clear alternatives)
        option_indicators = ["option", "alternative", "approach", "choice", "scenario"]
        options_count = sum(response_lower.count(indicator) for indicator in option_indicators)
        options_presentation = min(1.0, options_count / 3)  # Expect 2-3 options
        
        # Risk assessment (identification of risks)
        risk_indicators = ["risk", "uncertainty", "challenge", "concern", "potential issue"]
        risk_mentions = sum(1 for indicator in risk_indicators if indicator in response_lower)
        risk_assessment = min(1.0, risk_mentions / 3)
        
        # Recommendation quality (single, clear recommendation)
        recommendation_indicators = ["recommend", "suggest", "propose", "advise", "should"]
        has_recommendation = any(indicator in response_lower for indicator in recommendation_indicators)
        recommendation_quality = 0.8 if has_recommendation else 0.2
        
        # Action specificity (specific actions with owners/timelines)
        action_indicators = ["action", "step", "implement", "execute", "timeline"]
        action_score = min(1.0, sum(1 for indicator in action_indicators 
                                  if indicator in response_lower) / 2)
        
        # Trade-off recognition
        tradeoff_indicators = ["trade-off", "balance", "compromise", "versus", "however"]
        tradeoff_score = min(1.0, sum(1 for indicator in tradeoff_indicators 
                                    if indicator in response_lower) / 2)
        
        # Overall leadership clarity
        overall_score = (
            synthesis_score * 0.20 +
            options_presentation * 0.20 +
            risk_assessment * 0.15 +
            recommendation_quality * 0.20 +
            action_score * 0.15 +
            tradeoff_score * 0.10
        )
        
        return LeadershipClarityMetrics(
            executive_synthesis=synthesis_score,
            options_presentation=options_presentation,
            risk_assessment=risk_assessment,
            recommendation_quality=recommendation_quality,
            action_specificity=action_score,
            trade_off_recognition=tradeoff_score,
            overall_score=overall_score,
            details={
                "synthesis_indicators": synthesis_indicators,
                "options_count": options_count,
                "risk_mentions": risk_mentions,
                "has_recommendation": has_recommendation
            }
        )
    
    async def _evaluate_conflict_index(self, response_text: str, agent_role: str,
                                     scenario: EvaluationScenario) -> ConflictIndexMetrics:
        """Evaluate how well the response handles inter-role conflicts"""
        
        response_lower = response_text.lower()
        
        # Tension recognition (acknowledges conflicts between roles)
        tension_indicators = ["tension", "conflict", "disagreement", "competing", "different perspectives"]
        tension_recognition = min(1.0, sum(1 for indicator in tension_indicators 
                                         if indicator in response_lower) / 2)
        
        # Balanced perspective (considers other roles' viewpoints)
        other_roles = [r for r in ["cfo", "cmo", "coo", "cto", "founder", "investor"] if r != agent_role]
        role_mentions = sum(1 for role in other_roles if role in response_lower)
        balanced_perspective = min(1.0, role_mentions / max(1, len(other_roles) * 0.3))
        
        # Resolution approach (constructive conflict resolution)
        resolution_indicators = ["collaborate", "align", "consensus", "compromise", "win-win"]
        resolution_score = min(1.0, sum(1 for indicator in resolution_indicators 
                                      if indicator in response_lower) / 2)
        
        # Collaboration tone vs. competitive tone
        collaborative_terms = ["together", "jointly", "shared", "collective", "team"]
        competitive_terms = ["beat", "outperform", "against", "compete", "dominate"]
        collab_count = sum(1 for term in collaborative_terms if term in response_lower)
        competitive_count = sum(1 for term in competitive_terms if term in response_lower)
        collaboration_tone = collab_count / max(1, collab_count + competitive_count)
        
        # Compromise quality (quality of compromise solutions)
        compromise_indicators = ["middle ground", "balance", "hybrid", "combined approach"]
        compromise_quality = min(1.0, sum(1 for indicator in compromise_indicators 
                                        if indicator in response_lower))
        
        # Stakeholder consideration (considers all stakeholders)
        stakeholder_terms = ["stakeholder", "customer", "employee", "investor", "board"]
        stakeholder_mentions = sum(1 for term in stakeholder_terms if term in response_lower)
        stakeholder_consideration = min(1.0, stakeholder_mentions / 3)
        
        # Overall conflict index (lower is better - indicates better conflict handling)
        conflict_score = 1.0 - (
            tension_recognition * 0.15 +
            balanced_perspective * 0.20 +
            resolution_score * 0.20 +
            collaboration_tone * 0.15 +
            compromise_quality * 0.15 +
            stakeholder_consideration * 0.15
        )
        
        return ConflictIndexMetrics(
            tension_recognition=tension_recognition,
            balanced_perspective=balanced_perspective,
            resolution_approach=resolution_score,
            collaboration_tone=collaboration_tone,
            compromise_quality=compromise_quality,
            stakeholder_consideration=stakeholder_consideration,
            overall_score=conflict_score,
            details={
                "role_mentions": role_mentions,
                "collab_count": collab_count,
                "competitive_count": competitive_count,
                "stakeholder_mentions": stakeholder_mentions
            }
        )
    
    async def _evaluate_guardrail_compliance(self, response_text: str, agent_role: str,
                                           scenario: EvaluationScenario) -> GuardrailComplianceMetrics:
        """Evaluate compliance with role-specific and general guardrails"""
        
        response_lower = response_text.lower()
        
        # Role-specific guardrail checks
        role_guardrails = self.guardrail_rules.get(agent_role, [])
        role_compliance_checks = []
        
        if agent_role == "founder":
            role_compliance_checks = [
                "roadmap" in response_lower or "milestone" in response_lower,  # vision to roadmap
                any(term in response_lower for term in ["measurable", "metric", "kpi"]),  # measurable milestones
                len(response_text) > 100,  # not pure rhetoric (substantial content)
                "culture" in response_lower or "value" in response_lower  # cultural continuity
            ]
        elif agent_role == "investor":
            role_compliance_checks = [
                "valuation" in response_lower or "value" in response_lower,  # valuation impact
                "capital" in response_lower or "efficiency" in response_lower,  # capital efficiency
                "exit" in response_lower or "liquidity" in response_lower,  # exit considerations
                not any(term in response_lower for term in ["$999", "exact", "precise"])  # no fabricated figures
            ]
        
        role_specific_score = sum(role_compliance_checks) / max(1, len(role_compliance_checks))
        
        # Output schema compliance (check for expected sections)
        schema_elements = ["analysis", "recommendation", "action", "risk"]
        schema_compliance = sum(1 for element in schema_elements if element in response_lower) / len(schema_elements)
        
        # Numeric consistency (basic check for reasonable numbers)
        import re
        numbers = re.findall(r'\$?\d+(?:,\d{3})*(?:\.\d+)?[MBK]?', response_text)
        numeric_consistency = 1.0 if len(numbers) == 0 else 0.8  # Basic check - more sophisticated logic needed
        
        # Ethical guidelines (check for problematic content)
        ethical_red_flags = ["discriminat", "bias", "unfair", "illegal", "unethical"]
        ethical_score = 1.0 - min(0.5, sum(1 for flag in ethical_red_flags if flag in response_lower) / 5)
        
        # Factual accuracy (check for hedging language vs. absolute claims)
        hedging_terms = ["likely", "probably", "estimate", "approximately", "suggest"]
        absolute_terms = ["definitely", "certainly", "guaranteed", "always", "never"]
        hedging_count = sum(1 for term in hedging_terms if term in response_lower)
        absolute_count = sum(1 for term in absolute_terms if term in response_lower)
        factual_accuracy = 0.8 if hedging_count > absolute_count else 0.6
        
        # Overall compliance score
        overall_score = (
            role_specific_score * 0.30 +
            schema_compliance * 0.20 +
            numeric_consistency * 0.15 +
            ethical_score * 0.20 +
            factual_accuracy * 0.15
        )
        
        return GuardrailComplianceMetrics(
            role_specific_checks=role_specific_score,
            output_schema_compliance=schema_compliance,
            numeric_consistency=numeric_consistency,
            ethical_guidelines=ethical_score,
            factual_accuracy=factual_accuracy,
            overall_score=overall_score,
            details={
                "role_checks_passed": sum(role_compliance_checks),
                "schema_elements_found": sum(1 for element in schema_elements if element in response_lower),
                "numbers_found": len(numbers),
                "hedging_vs_absolute": f"{hedging_count} vs {absolute_count}"
            }
        )
    
    async def run_evaluation_suite(self, agent_responses: Dict[str, str], 
                                 scenario_id: str) -> Dict[str, EvaluationResult]:
        """
        Run complete evaluation suite on multiple agent responses.
        
        Args:
            agent_responses: Dict mapping agent_role -> response_text
            scenario_id: ID of evaluation scenario
            
        Returns:
            Dict mapping agent_role -> evaluation_result
        """
        results = {}
        
        logger.info(f"Running evaluation suite on scenario {scenario_id} with {len(agent_responses)} responses")
        
        for agent_role, response_text in agent_responses.items():
            try:
                result = await self.evaluate_response(response_text, agent_role, scenario_id)
                results[agent_role] = result
                
                logger.info(f"Evaluated {agent_role}: Overall Score = {result.overall_score:.3f}")
                
            except Exception as e:
                logger.error(f"Failed to evaluate response from {agent_role}: {e}")
        
        return results
    
    async def get_performance_trends(self, agent_role: str = None, 
                                   days: int = 30) -> Dict[str, Any]:
        """
        Get performance trends over time for agent(s).
        
        Args:
            agent_role: Specific role or None for all roles
            days: Number of days to analyze
            
        Returns:
            Performance trend analysis
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter results by date and role
        filtered_results = [
            result for result in self.evaluation_results
            if result.evaluation_timestamp >= cutoff_date and
               (agent_role is None or result.agent_role == agent_role)
        ]
        
        if not filtered_results:
            return {"error": "No evaluation results found for the specified criteria"}
        
        # Calculate trends
        roles_analyzed = list(set(result.agent_role for result in filtered_results))
        
        trends = {}
        for role in roles_analyzed:
            role_results = [r for r in filtered_results if r.agent_role == role]
            
            # Calculate averages
            avg_overall = sum(r.overall_score for r in role_results) / len(role_results)
            avg_role_fidelity = sum(r.role_fidelity.overall_score for r in role_results) / len(role_results)
            avg_leadership = sum(r.leadership_clarity.overall_score for r in role_results) / len(role_results)
            avg_conflict = sum(r.conflict_index.overall_score for r in role_results) / len(role_results)
            
            # Calculate trend (simple linear approximation)
            if len(role_results) > 1:
                first_half = role_results[:len(role_results)//2]
                second_half = role_results[len(role_results)//2:]
                
                first_avg = sum(r.overall_score for r in first_half) / len(first_half)
                second_avg = sum(r.overall_score for r in second_half) / len(second_half)
                
                trend_direction = "improving" if second_avg > first_avg else "declining"
                trend_magnitude = abs(second_avg - first_avg)
            else:
                trend_direction = "insufficient_data"
                trend_magnitude = 0
            
            trends[role] = {
                "evaluations_count": len(role_results),
                "average_overall_score": avg_overall,
                "average_role_fidelity": avg_role_fidelity,
                "average_leadership_clarity": avg_leadership,
                "average_conflict_index": avg_conflict,
                "trend_direction": trend_direction,
                "trend_magnitude": trend_magnitude,
                "latest_score": role_results[-1].overall_score if role_results else 0
            }
        
        return {
            "analysis_period_days": days,
            "total_evaluations": len(filtered_results),
            "roles_analyzed": roles_analyzed,
            "trends": trends
        }
    
    async def generate_evaluation_report(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """Generate comprehensive evaluation report"""
        
        if not results:
            return {"error": "No results provided"}
        
        # Summary statistics
        avg_overall = sum(r.overall_score for r in results) / len(results)
        avg_role_fidelity = sum(r.role_fidelity.overall_score for r in results) / len(results)
        avg_leadership = sum(r.leadership_clarity.overall_score for r in results) / len(results)
        avg_conflict = sum(r.conflict_index.overall_score for r in results) / len(results)
        avg_compliance = sum(r.guardrail_compliance.overall_score for r in results) / len(results)
        
        # Role breakdown
        roles = list(set(r.agent_role for r in results))
        role_breakdown = {}
        
        for role in roles:
            role_results = [r for r in results if r.agent_role == role]
            role_breakdown[role] = {
                "count": len(role_results),
                "average_score": sum(r.overall_score for r in role_results) / len(role_results),
                "best_score": max(r.overall_score for r in role_results),
                "worst_score": min(r.overall_score for r in role_results)
            }
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if avg_role_fidelity > 0.8:
            strengths.append("Strong role fidelity - agents maintain role characteristics well")
        elif avg_role_fidelity < 0.6:
            weaknesses.append("Role fidelity issues - agents not maintaining role consistency")
        
        if avg_leadership > 0.75:
            strengths.append("Good leadership clarity - clear decision framing")
        elif avg_leadership < 0.6:
            weaknesses.append("Leadership clarity needs improvement")
        
        if avg_conflict < 0.4:  # Lower is better for conflict index
            strengths.append("Excellent conflict resolution - handles tensions well")
        elif avg_conflict > 0.7:
            weaknesses.append("High conflict index - difficulty handling role tensions")
        
        return {
            "report_generated": datetime.now().isoformat(),
            "summary": {
                "total_evaluations": len(results),
                "average_overall_score": avg_overall,
                "score_distribution": {
                    "role_fidelity": avg_role_fidelity,
                    "leadership_clarity": avg_leadership,
                    "conflict_index": avg_conflict,
                    "guardrail_compliance": avg_compliance
                }
            },
            "role_breakdown": role_breakdown,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": self._generate_recommendations(avg_role_fidelity, avg_leadership, avg_conflict, avg_compliance)
        }
    
    def _generate_recommendations(self, role_fidelity: float, leadership: float, 
                                conflict: float, compliance: float) -> List[str]:
        """Generate improvement recommendations based on scores"""
        recommendations = []
        
        if role_fidelity < 0.7:
            recommendations.append("Enhance role-specific training data with more domain vocabulary and KPIs")
        
        if leadership < 0.7:
            recommendations.append("Improve leadership adapter training with more executive decision-making examples")
        
        if conflict > 0.6:
            recommendations.append("Add more multi-role scenario training to improve conflict resolution")
        
        if compliance < 0.8:
            recommendations.append("Strengthen guardrail enforcement and schema compliance training")
        
        if not recommendations:
            recommendations.append("Performance is strong across all dimensions - consider increasing scenario complexity")
        
        return recommendations