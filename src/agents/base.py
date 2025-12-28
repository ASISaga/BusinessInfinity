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

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import logging

# Try importing external BusinessAgent package
try:
    from BusinessAgent import BusinessAgent
    from BusinessAgent.message import Message, MessageType, MessagePriority
    BUSINESS_AGENT_AVAILABLE = True
except ImportError:
    BUSINESS_AGENT_AVAILABLE = False
    # Provide stub implementations
    Message = None
    MessageType = None
    MessagePriority = None
    
    class BusinessAgent(ABC):
        """Stub BusinessAgent base class when package not available."""
        
        def __init__(self, agent_id: str, name: str, role: str, domain: str, config: Dict[str, Any] = None):
            self.agent_id = agent_id
            self.name = name
            self.role = role
            self.domain = domain
            self.config = config or {}
            self.logger = logging.getLogger(f"BusinessAgent.{agent_id}")
        
        @abstractmethod
        def _define_domain_expertise(self) -> List[str]:
            """Define domain expertise areas."""
            pass
        
        @abstractmethod
        def _define_business_kpis(self) -> Dict[str, Any]:
            """Define business KPIs."""
            pass
        
        @abstractmethod
        def _define_business_decision_framework(self) -> Dict[str, Any]:
            """Define business decision framework."""
            pass
        
        async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
            """Process a business query."""
            return {"response": f"Query processed by {self.role}", "query": query}


# Re-export for use by agent implementations
__all__ = [
    "BusinessAgent",
    "Message", 
    "MessageType",
    "MessagePriority",
    "BUSINESS_AGENT_AVAILABLE",
]