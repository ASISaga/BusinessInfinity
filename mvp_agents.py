"""
Minimal Agent Base Classes for BusinessInfinity MVP
Replaces the missing RealmOfAgents dependency with simplified local implementations
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base agent class with essential functionality"""
    
    def __init__(self, agent_id: str, name: str, role: str):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.created_at = datetime.now()
        self.conversation_history = []
        
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process a message and return a response"""
        pass
    
    def get_profile(self) -> Dict[str, Any]:
        """Get agent profile information"""
        return {
            "id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "conversation_count": len(self.conversation_history)
        }
    
    def add_conversation_entry(self, message: str, response: str):
        """Add conversation to history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response
        }
        self.conversation_history.append(entry)
        
        # Keep only last 100 entries for MVP
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]


class LeadershipAgent(BaseAgent):
    """Leadership agent with business decision-making capabilities"""
    
    def __init__(self, agent_id: str, name: str, role: str, domain: str):
        super().__init__(agent_id, name, role)
        self.domain = domain
        self.expertise_areas = []
        self.decision_framework = {}
        
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process leadership-related messages"""
        try:
            # Simulate processing time
            await asyncio.sleep(0.1)
            
            # Simple response generation based on role and domain
            response = self._generate_leadership_response(message, context or {})
            
            # Add to conversation history
            self.add_conversation_entry(message, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message for {self.agent_id}: {e}")
            return f"I apologize, but I encountered an error while processing your request. As your {self.role}, I'll need more information to provide a proper response."
    
    def _generate_leadership_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate appropriate leadership response based on role"""
        message_lower = message.lower()
        
        # Domain-specific response patterns
        if self.role == "CEO":
            if any(word in message_lower for word in ["strategy", "vision", "direction"]):
                return f"As CEO, I believe we need to focus on strategic alignment with our core vision. Let me outline our key strategic priorities: 1) Market leadership, 2) Operational excellence, 3) Innovation leadership. What specific aspect would you like to discuss?"
            elif any(word in message_lower for word in ["team", "culture", "organization"]):
                return f"Our organizational culture is fundamental to our success. As CEO, I prioritize building a high-performance culture based on accountability, innovation, and customer focus. How can we strengthen this in your area?"
                
        elif self.role == "CFO":
            if any(word in message_lower for word in ["budget", "finance", "cost", "revenue"]):
                return f"From a financial perspective, I recommend we analyze the cost-benefit implications carefully. Let me review our current financial position and provide recommendations for optimal resource allocation."
            elif any(word in message_lower for word in ["investment", "funding", "capital"]):
                return f"For any capital allocation decisions, I evaluate based on ROI, risk profile, and strategic alignment. Let me provide a financial analysis framework for this opportunity."
                
        elif self.role == "CTO":
            if any(word in message_lower for word in ["technology", "architecture", "system"]):
                return f"From a technology leadership standpoint, I recommend focusing on scalable, secure, and maintainable solutions. Let me outline our technical strategy and implementation approach."
            elif any(word in message_lower for word in ["security", "risk", "compliance"]):
                return f"Security and compliance are paramount in our technical decisions. I'll ensure we implement robust security frameworks and maintain regulatory compliance across all systems."
                
        elif self.role == "CMO":
            if any(word in message_lower for word in ["marketing", "brand", "customer"]):
                return f"Our marketing strategy should focus on customer-centric brand positioning and data-driven campaign optimization. Let me share our customer acquisition and retention strategies."
            elif any(word in message_lower for word in ["market", "competition", "positioning"]):
                return f"Market positioning requires deep customer insights and competitive intelligence. I'll provide market analysis and recommend positioning strategies to maximize our competitive advantage."
                
        elif self.role == "COO":
            if any(word in message_lower for word in ["operations", "process", "efficiency"]):
                return f"Operational excellence is achieved through systematic process optimization and performance management. Let me outline our operational efficiency framework and improvement opportunities."
            elif any(word in message_lower for word in ["quality", "performance", "delivery"]):
                return f"Quality and delivery performance are key operational metrics. I'll provide analysis of our current performance and recommendations for continuous improvement."
                
        elif self.role == "CHRO":
            if any(word in message_lower for word in ["talent", "hiring", "people"]):
                return f"Our talent strategy focuses on attracting, developing, and retaining top performers. Let me share our talent acquisition and development framework."
            elif any(word in message_lower for word in ["culture", "engagement", "performance"]):
                return f"Employee engagement and performance management are critical to organizational success. I'll outline our people development and culture enhancement strategies."
                
        elif self.role == "Founder":
            if any(word in message_lower for word in ["vision", "mission", "purpose"]):
                return f"Our foundational vision drives everything we do. As Founder, I believe in building a company that creates meaningful impact while achieving sustainable growth. Let me share our core purpose and strategic vision."
            elif any(word in message_lower for word in ["innovation", "product", "market"]):
                return f"Innovation and market opportunity identification are central to our entrepreneurial approach. I'll provide insights on market trends and product development strategies."
        
        # Generic leadership response
        return f"As your {self.role}, I appreciate you bringing this to my attention. Based on my experience in {self.domain}, I recommend we take a strategic approach that considers both short-term execution and long-term vision. Could you provide more specific context so I can offer more targeted guidance?"


class AgentManager:
    """Simple agent manager for MVP"""
    
    def __init__(self):
        self.agents = {}
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """Initialize default C-Suite and Founder agents"""
        default_agents = [
            ("ceo", "Chief Executive Officer", "CEO", "Executive Leadership"),
            ("cfo", "Chief Financial Officer", "CFO", "Finance"),
            ("cto", "Chief Technology Officer", "CTO", "Technology"),
            ("cmo", "Chief Marketing Officer", "CMO", "Marketing"),
            ("coo", "Chief Operating Officer", "COO", "Operations"),
            ("chro", "Chief Human Resources Officer", "CHRO", "Human Resources"),
            ("founder", "Founder", "Founder", "Entrepreneurship"),
        ]
        
        for agent_id, name, role, domain in default_agents:
            agent = LeadershipAgent(agent_id, name, role, domain)
            self.agents[agent_id] = agent
            
    def get_agent(self, agent_id: str) -> Optional[LeadershipAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id.lower())
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents"""
        return [agent.get_profile() for agent in self.agents.values()]
    
    async def ask_agent(self, agent_id: str, message: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Ask an agent a question"""
        agent = self.get_agent(agent_id)
        if not agent:
            return None
            
        try:
            response = await agent.process_message(message, context)
            return response
        except Exception as e:
            logger.error(f"Error asking agent {agent_id}: {e}")
            return None
    
    def get_agent_profile(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent profile"""
        agent = self.get_agent(agent_id)
        return agent.get_profile() if agent else None


# Global agent manager instance
agent_manager = AgentManager()