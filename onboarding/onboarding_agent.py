"""
Onboarding Agent for Business Infinity
Handles the step-by-step onboarding journey for new founders
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class OnboardingStage(Enum):
    """Onboarding stages following the journey specification"""
    WELCOME_GATEWAY = "welcome_gateway"
    IDENTITY_CAPTURE = "identity_capture"
    WEBSITE_DISCOVERY = "website_discovery"
    PITCH_DECK_UPLOAD = "pitch_deck_upload"
    FINANCIAL_DOCS = "financial_docs"
    SYSTEM_CONNECTORS = "system_connectors"
    VOICE_PROFILE = "voice_profile"
    INSTANT_BASELINE = "instant_baseline"
    GOVERNANCE_SETTINGS = "governance_settings"
    QUICK_ACTIONS = "quick_actions"
    COMPLETED = "completed"

@dataclass
class OnboardingSession:
    """Represents an onboarding session for a founder"""
    session_id: str
    founder_name: Optional[str] = None
    company_name: Optional[str] = None
    email: Optional[str] = None
    current_stage: OnboardingStage = OnboardingStage.WELCOME_GATEWAY
    auth_method: Optional[str] = None
    linkedin_profile: Optional[Dict[str, Any]] = None
    website_data: Optional[Dict[str, Any]] = None
    pitch_deck_data: Optional[Dict[str, Any]] = None
    financial_data: Optional[Dict[str, Any]] = None
    connected_systems: List[str] = None
    voice_profile: Optional[Dict[str, Any]] = None
    governance_settings: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.connected_systems is None:
            self.connected_systems = []
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "session_id": self.session_id,
            "founder_name": self.founder_name,
            "company_name": self.company_name,
            "email": self.email,
            "current_stage": self.current_stage.value,
            "auth_method": self.auth_method,
            "linkedin_profile": self.linkedin_profile,
            "website_data": self.website_data,
            "pitch_deck_data": self.pitch_deck_data,
            "financial_data": self.financial_data,
            "connected_systems": self.connected_systems,
            "voice_profile": self.voice_profile,
            "governance_settings": self.governance_settings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

class OnboardingAgent:
    """
    AI agent responsible for guiding founders through the onboarding process
    Follows the reassurance-first approach specified in the journey document
    """
    
    def __init__(self):
        self.sessions: Dict[str, OnboardingSession] = {}
        self.stage_messages = self._initialize_stage_messages()
        
    def _initialize_stage_messages(self) -> Dict[OnboardingStage, Dict[str, str]]:
        """Initialize reassurance messages for each stage"""
        return {
            OnboardingStage.WELCOME_GATEWAY: {
                "welcome": "Welcome — this is your private boardroom. We'll only read data you allow and never change anything without permission.",
                "privacy": "Read-only connections by default; you remain in control.",
                "security": "Secure sign-on via OAuth. We follow industry best practices."
            },
            OnboardingStage.IDENTITY_CAPTURE: {
                "linkedin_prompt": "We'll read your profile and recent public posts to tailor the boardroom voice. Nothing will be posted or changed.",
                "data_scope": "Only core profile + last 20 public posts are used. You can revoke access anytime.",
                "consent": "We will only read these fields; nothing is posted to LinkedIn."
            },
            OnboardingStage.WEBSITE_DISCOVERY: {
                "public_only": "We only fetch public content; we will ask before you upload any private documents.",
                "read_only": "This was read from your public site; no writes occurred.",
                "verification": "Does this represent your company correctly?"
            },
            OnboardingStage.PITCH_DECK_UPLOAD: {
                "encryption": "Files are stored encrypted and only accessible in read-only mode to boardroom agents.",
                "security": "Stored encrypted at rest (AES-256 equivalent). Only authorized boardroom agents can read this file.",
                "optional": "I'd rather not upload now (you can skip this step)"
            },
            OnboardingStage.FINANCIAL_DOCS: {
                "integrity": "We will never alter these documents — only read and summarize.",
                "retention": "Private files retained 30 days by default; export or delete anytime.",
                "verification": "Files are hashed to verify unchanged content."
            },
            OnboardingStage.SYSTEM_CONNECTORS: {
                "read_only": "We request read-only scope only. No writes or edits. You remain in control.",
                "security": "Connections use TLS; tokens are stored encrypted; we undergo third-party penetration tests.",
                "revoke": "You can revoke access anytime."
            },
            OnboardingStage.VOICE_PROFILE: {
                "analysis_only": "We only analyze public posts to learn voice and priorities — nothing is published anywhere.",
                "transparency": "Transparency log shows the posts parsed and you can remove any post from analysis.",
                "control": "Quick preview of extracted themes with an edit button."
            },
            OnboardingStage.INSTANT_BASELINE: {
                "completion": "Your boardroom is assembled. We've created your Founder Dossier and Company Brief.",
                "permission": "From here on, we observe and advise; nothing will be changed without your permission.",
                "audit": "Everything is logged and auditable. You can download artifacts or request deletion."
            },
            OnboardingStage.GOVERNANCE_SETTINGS: {
                "privacy": "By default your data is private to you. Invite team members selectively.",
                "control": "You can change these settings any time.",
                "rbac": "Conservative defaults: founder only, read-only for invited viewers."
            },
            OnboardingStage.QUICK_ACTIONS: {
                "welcome": "You're inside the boardroom. We'll surface weekly insights and urgent risks proactively.",
                "optional": "When you're ready for a full review, we'll convene. Until then, we watch, learn, and advise.",
                "security": "If security or privacy is ever a concern, click Revoke Access or contact security@businessinfinity — we'll respond within 4 hours."
            }
        }
    
    async def start_onboarding(self, session_id: str, initial_data: Dict[str, Any] = None) -> OnboardingSession:
        """Start a new onboarding session"""
        session = OnboardingSession(session_id=session_id)
        
        if initial_data:
            if 'company_name' in initial_data:
                session.company_name = initial_data['company_name']
            if 'founder_name' in initial_data:
                session.founder_name = initial_data['founder_name']
            if 'email' in initial_data:
                session.email = initial_data['email']
        
        self.sessions[session_id] = session
        logger.info(f"Started onboarding session {session_id}")
        
        return session
    
    async def progress_to_stage(self, session_id: str, stage: OnboardingStage, stage_data: Dict[str, Any] = None) -> OnboardingSession:
        """Progress the onboarding session to the next stage"""
        if session_id not in self.sessions:
            raise ValueError(f"Onboarding session {session_id} not found")
        
        session = self.sessions[session_id]
        previous_stage = session.current_stage
        session.current_stage = stage
        
        # Store stage-specific data
        if stage_data:
            if stage == OnboardingStage.IDENTITY_CAPTURE:
                session.linkedin_profile = stage_data.get('linkedin_profile')
                session.auth_method = stage_data.get('auth_method', 'linkedin')
            elif stage == OnboardingStage.WEBSITE_DISCOVERY:
                session.website_data = stage_data.get('website_data')
            elif stage == OnboardingStage.PITCH_DECK_UPLOAD:
                session.pitch_deck_data = stage_data.get('pitch_deck_data')
            elif stage == OnboardingStage.FINANCIAL_DOCS:
                session.financial_data = stage_data.get('financial_data')
            elif stage == OnboardingStage.SYSTEM_CONNECTORS:
                if 'connected_system' in stage_data:
                    session.connected_systems.append(stage_data['connected_system'])
            elif stage == OnboardingStage.VOICE_PROFILE:
                session.voice_profile = stage_data.get('voice_profile')
            elif stage == OnboardingStage.GOVERNANCE_SETTINGS:
                session.governance_settings = stage_data.get('governance_settings')
            elif stage == OnboardingStage.COMPLETED:
                session.completed_at = datetime.now()
        
        logger.info(f"Session {session_id} progressed from {previous_stage.value} to {stage.value}")
        return session
    
    def get_stage_message(self, stage: OnboardingStage, message_type: str) -> str:
        """Get reassurance message for a specific stage"""
        return self.stage_messages.get(stage, {}).get(message_type, "")
    
    async def generate_ceo_briefing(self, session: OnboardingSession) -> str:
        """Generate initial CEO briefing message for step 8"""
        briefing_parts = [
            f"Welcome to your perpetual boardroom, {session.founder_name or 'Founder'}!",
            "",
            "I've just completed your onboarding analysis. Here's what we've assembled:"
        ]
        
        if session.company_name:
            briefing_parts.append(f"• Company Profile: {session.company_name}")
        
        if session.linkedin_profile:
            briefing_parts.append("• LinkedIn Profile: Captured and analyzed")
        
        if session.website_data:
            briefing_parts.append("• Website Content: Parsed and categorized")
            
        if session.pitch_deck_data:
            briefing_parts.append(f"• Pitch Deck: {session.pitch_deck_data.get('slides_count', 'N/A')} slides processed")
            
        if session.financial_data:
            briefing_parts.append("• Financial Documents: Analyzed and secured")
            
        if session.connected_systems:
            briefing_parts.append(f"• System Integrations: {len(session.connected_systems)} systems connected")
            
        if session.voice_profile:
            briefing_parts.append("• Voice Profile: Generated from your communications")
        
        briefing_parts.extend([
            "",
            "Your Founder Dossier and Live Baseline are ready. No writes were made. Everything is logged and auditable.",
            "",
            "From now on, we'll monitor your business environment and provide strategic insights. Your data remains under your control.",
            "",
            "Would you like me to connect you with any of the C-Suite agents for immediate analysis?"
        ])
        
        return "\n".join(briefing_parts)
    
    async def handle_quick_action(self, session_id: str, action_message: str) -> str:
        """Handle final step quick actions"""
        if session_id not in self.sessions:
            return "Session not found. Please restart onboarding."
        
        session = self.sessions[session_id]
        action_lower = action_message.lower()
        
        if 'a' in action_lower or 'runway' in action_lower or 'cfo' in action_lower:
            response = f"Excellent choice, {session.founder_name or 'Founder'}! I'm connecting you with our CFO agent who will:"
            response += "\n• Analyze your financial data and burn rate"
            response += "\n• Create a comprehensive runway model"
            response += "\n• Identify funding requirements and milestones"
            if session.financial_data:
                response += "\n• Use your uploaded financial documents for accurate projections"
            response += "\n\nThe CFO agent will have access to all the data you've shared and will provide actionable insights."
            
        elif 'b' in action_lower or 'gtm' in action_lower or 'cmo' in action_lower:
            response = f"Great selection, {session.founder_name or 'Founder'}! Our CMO agent will create:"
            response += "\n• Go-to-Market strategy based on your company profile"
            response += "\n• Target market analysis and positioning"
            response += "\n• Brand voice guidelines aligned with your communication style"
            if session.voice_profile:
                response += f"\n• Messaging optimized for your identified themes: {', '.join(session.voice_profile.get('themes', []))}"
            response += "\n\nThis will help align your marketing across all channels."
            
        elif 'c' in action_lower or 'review' in action_lower or 'deep' in action_lower:
            response = f"Perfect, {session.founder_name or 'Founder'}! I'll convene the full C-Suite for a comprehensive review:"
            response += "\n• CEO: Strategic overview and growth opportunities"
            response += "\n• CFO: Financial analysis and runway planning"
            response += "\n• CMO: Marketing strategy and brand positioning"
            response += "\n• CTO: Technology roadmap and scalability"
            response += "\n• COO: Operations optimization and efficiency"
            response += "\n\nWe'll analyze all your data and provide detailed insights across all business functions."
            
        else:
            response = f"I'm here to help, {session.founder_name or 'Founder'}! You can:"
            response += "\n• Type 'A' for CFO runway analysis"
            response += "\n• Type 'B' for CMO go-to-market strategy"
            response += "\n• Type 'C' for comprehensive C-Suite review"
            response += "\n• Or ask me any specific question about your business"
            response += "\n\nRemember, you can always access these options later from your boardroom dashboard."
        
        return response
    
    def get_session(self, session_id: str) -> Optional[OnboardingSession]:
        """Get onboarding session by ID"""
        return self.sessions.get(session_id)
    
    def get_all_sessions(self) -> List[OnboardingSession]:
        """Get all onboarding sessions"""
        return list(self.sessions.values())
    
    async def generate_audit_entries(self, session: OnboardingSession) -> List[Dict[str, Any]]:
        """Generate audit trail entries for a session"""
        entries = []
        base_time = session.created_at
        
        entries.append({
            "timestamp": base_time.isoformat(),
            "action": "onboarding_session_started",
            "description": f"Onboarding session initiated for {session.company_name or 'company'}",
            "data_accessed": None,
            "permissions_granted": None
        })
        
        if session.linkedin_profile:
            entries.append({
                "timestamp": (base_time).isoformat(),
                "action": "linkedin_authorization",
                "description": "LinkedIn OAuth completed - read-only profile access granted",
                "data_accessed": "LinkedIn profile, recent posts (public)",
                "permissions_granted": "read-only"
            })
        
        if session.website_data:
            entries.append({
                "timestamp": (base_time).isoformat(),
                "action": "website_parsing",
                "description": f"Website content parsed from {session.website_data.get('source_url', 'provided URL')}",
                "data_accessed": "Public website content only",
                "permissions_granted": None
            })
        
        if session.pitch_deck_data:
            entries.append({
                "timestamp": (base_time).isoformat(),
                "action": "document_upload",
                "description": "Pitch deck uploaded and encrypted",
                "data_accessed": f"Pitch deck ({session.pitch_deck_data.get('slides_count', 'N/A')} slides)",
                "permissions_granted": "read-only, encrypted storage"
            })
        
        if session.financial_data:
            entries.append({
                "timestamp": (base_time).isoformat(),
                "action": "financial_documents_upload",
                "description": "Financial documents processed and secured",
                "data_accessed": "Financial reports and data",
                "permissions_granted": "read-only, 30-day retention"
            })
        
        for system in session.connected_systems:
            entries.append({
                "timestamp": (base_time).isoformat(),
                "action": "system_integration",
                "description": f"Connected to {system} with read-only permissions",
                "data_accessed": f"{system} data (scope: read-only)",
                "permissions_granted": "OAuth read-only access"
            })
        
        if session.voice_profile:
            entries.append({
                "timestamp": (base_time).isoformat(),
                "action": "voice_profile_generation",
                "description": "Voice profile created from public communications",
                "data_accessed": "Public posts and communications",
                "permissions_granted": None
            })
        
        entries.append({
            "timestamp": (base_time).isoformat(),
            "action": "founder_dossier_created",
            "description": "Founder Dossier and Company Baseline generated",
            "data_accessed": "All provided onboarding data",
            "permissions_granted": "read-only analysis"
        })
        
        return entries

# Create global instance
onboarding_agent = OnboardingAgent()