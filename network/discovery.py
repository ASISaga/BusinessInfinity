"""
Network Discovery and Directory Service

Implements discovery mechanisms for the Global Network of Autonomous Boardrooms,
enabling boardrooms to find each other based on industry, capabilities, location,
and other criteria.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

from .network_protocol import BoardroomNode, EnterpriseIdentity, BoardroomStatus

class DiscoveryType(Enum):
    """Types of discovery operations"""
    BROADCAST = "broadcast"
    TARGETED = "targeted"
    INDUSTRY = "industry"
    CAPABILITY = "capability"
    LOCATION = "location"

@dataclass
class DiscoveryCriteria:
    """Criteria for discovering boardrooms"""
    industry: Optional[str] = None
    location: Optional[str] = None
    company_size: Optional[str] = None
    capabilities: Set[str] = field(default_factory=set)
    agent_types: Set[str] = field(default_factory=set)
    verification_required: bool = True
    max_results: int = 50
    
class BoardroomDirectory:
    """
    Directory service for registered boardrooms in the network
    
    Maintains a registry of all verified boardrooms with their
    capabilities, status, and metadata for discovery purposes.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.registered_boardrooms: Dict[str, BoardroomNode] = {}
        self.industry_index: Dict[str, Set[str]] = {}
        self.capability_index: Dict[str, Set[str]] = {}
        self.location_index: Dict[str, Set[str]] = {}
        
        # Directory metadata
        self.directory_updated: datetime = datetime.now()
        self.total_registered: int = 0
        
    def register_boardroom(self, boardroom: BoardroomNode) -> bool:
        """Register a boardroom in the directory"""
        if not boardroom.is_verified():
            self.logger.warning(f"Cannot register unverified boardroom: {boardroom.node_id}")
            return False
        
        self.registered_boardrooms[boardroom.node_id] = boardroom
        self._update_indices(boardroom)
        self.total_registered += 1
        self.directory_updated = datetime.now()
        
        self.logger.info(f"Registered boardroom: {boardroom.enterprise_identity.company_name}")
        return True
    
    def unregister_boardroom(self, node_id: str) -> bool:
        """Unregister a boardroom from the directory"""
        if node_id not in self.registered_boardrooms:
            return False
        
        boardroom = self.registered_boardrooms[node_id]
        self._remove_from_indices(boardroom)
        del self.registered_boardrooms[node_id]
        self.total_registered -= 1
        self.directory_updated = datetime.now()
        
        self.logger.info(f"Unregistered boardroom: {boardroom.enterprise_identity.company_name}")
        return True
    
    def find_boardrooms(self, criteria: DiscoveryCriteria) -> List[BoardroomNode]:
        """Find boardrooms matching the given criteria"""
        candidates = set(self.registered_boardrooms.keys())
        
        # Filter by verification status
        if criteria.verification_required:
            candidates = {node_id for node_id in candidates 
                         if self.registered_boardrooms[node_id].is_verified()}
        
        # Filter by industry
        if criteria.industry:
            industry_nodes = self.industry_index.get(criteria.industry.lower(), set())
            candidates = candidates.intersection(industry_nodes)
        
        # Filter by capabilities
        if criteria.capabilities:
            for capability in criteria.capabilities:
                capability_nodes = self.capability_index.get(capability.lower(), set())
                candidates = candidates.intersection(capability_nodes)
        
        # Filter by location
        if criteria.location:
            location_nodes = self.location_index.get(criteria.location.lower(), set())
            candidates = candidates.intersection(location_nodes)
        
        # Filter by agent types
        if criteria.agent_types:
            candidates = {node_id for node_id in candidates
                         if any(agent in self.registered_boardrooms[node_id].active_agents
                               for agent in criteria.agent_types)}
        
        # Filter by company size
        if criteria.company_size:
            candidates = {node_id for node_id in candidates
                         if self.registered_boardrooms[node_id].enterprise_identity.size == criteria.company_size}
        
        # Convert to BoardroomNode objects and limit results
        results = [self.registered_boardrooms[node_id] for node_id in candidates]
        results = results[:criteria.max_results]
        
        self.logger.info(f"Discovery query returned {len(results)} boardrooms")
        return results
    
    def get_directory_stats(self) -> Dict[str, Any]:
        """Get directory statistics"""
        active_count = sum(1 for br in self.registered_boardrooms.values() 
                          if br.status == BoardroomStatus.ACTIVE)
        verified_count = sum(1 for br in self.registered_boardrooms.values() 
                           if br.is_verified())
        
        return {
            "total_registered": self.total_registered,
            "active_boardrooms": active_count,
            "verified_boardrooms": verified_count,
            "industries": len(self.industry_index),
            "capabilities": len(self.capability_index),
            "locations": len(self.location_index),
            "last_updated": self.directory_updated.isoformat()
        }
    
    def _update_indices(self, boardroom: BoardroomNode):
        """Update search indices for a boardroom"""
        node_id = boardroom.node_id
        
        # Industry index
        industry = boardroom.enterprise_identity.industry.lower()
        if industry not in self.industry_index:
            self.industry_index[industry] = set()
        self.industry_index[industry].add(node_id)
        
        # Capability index
        for capability in boardroom.capabilities:
            cap_key = capability.lower()
            if cap_key not in self.capability_index:
                self.capability_index[cap_key] = set()
            self.capability_index[cap_key].add(node_id)
        
        # Location index
        location = boardroom.enterprise_identity.location.lower()
        if location not in self.location_index:
            self.location_index[location] = set()
        self.location_index[location].add(node_id)
    
    def _remove_from_indices(self, boardroom: BoardroomNode):
        """Remove boardroom from search indices"""
        node_id = boardroom.node_id
        
        # Remove from industry index
        industry = boardroom.enterprise_identity.industry.lower()
        if industry in self.industry_index:
            self.industry_index[industry].discard(node_id)
            if not self.industry_index[industry]:
                del self.industry_index[industry]
        
        # Remove from capability index
        for capability in boardroom.capabilities:
            cap_key = capability.lower()
            if cap_key in self.capability_index:
                self.capability_index[cap_key].discard(node_id)
                if not self.capability_index[cap_key]:
                    del self.capability_index[cap_key]
        
        # Remove from location index
        location = boardroom.enterprise_identity.location.lower()
        if location in self.location_index:
            self.location_index[location].discard(node_id)
            if not self.location_index[location]:
                del self.location_index[location]

class NetworkDiscovery:
    """
    Network Discovery Service
    
    Handles discovery operations across the global network of boardrooms,
    including broadcast discovery, targeted searches, and network mapping.
    """
    
    def __init__(self, directory: BoardroomDirectory = None):
        self.logger = logging.getLogger(__name__)
        self.directory = directory or BoardroomDirectory()
        self.discovery_history: List[Dict[str, Any]] = []
        self.network_map: Dict[str, Set[str]] = {}  # Node connections
        
    async def discover_boardrooms(self, criteria: DiscoveryCriteria, 
                                discovery_type: DiscoveryType = DiscoveryType.BROADCAST) -> List[BoardroomNode]:
        """
        Discover boardrooms in the network based on criteria
        
        Args:
            criteria: Discovery criteria
            discovery_type: Type of discovery operation
            
        Returns:
            List of matching BoardroomNode objects
        """
        self.logger.info(f"Starting {discovery_type.value} discovery")
        
        # Record discovery attempt
        discovery_record = {
            "timestamp": datetime.now(),
            "type": discovery_type.value,
            "criteria": {
                "industry": criteria.industry,
                "location": criteria.location,
                "capabilities": list(criteria.capabilities),
                "agent_types": list(criteria.agent_types),
                "verification_required": criteria.verification_required
            }
        }
        
        if discovery_type == DiscoveryType.BROADCAST:
            results = await self._broadcast_discovery(criteria)
        elif discovery_type == DiscoveryType.TARGETED:
            results = await self._targeted_discovery(criteria)
        elif discovery_type == DiscoveryType.INDUSTRY:
            results = await self._industry_discovery(criteria)
        elif discovery_type == DiscoveryType.CAPABILITY:
            results = await self._capability_discovery(criteria)
        elif discovery_type == DiscoveryType.LOCATION:
            results = await self._location_discovery(criteria)
        else:
            results = []
        
        discovery_record["results_count"] = len(results)
        discovery_record["boardrooms_found"] = [br.enterprise_identity.company_name for br in results]
        self.discovery_history.append(discovery_record)
        
        self.logger.info(f"Discovery completed: {len(results)} boardrooms found")
        return results
    
    async def _broadcast_discovery(self, criteria: DiscoveryCriteria) -> List[BoardroomNode]:
        """Perform broadcast discovery across the network"""
        # Use directory for broadcast discovery
        return self.directory.find_boardrooms(criteria)
    
    async def _targeted_discovery(self, criteria: DiscoveryCriteria) -> List[BoardroomNode]:
        """Perform targeted discovery based on specific criteria"""
        # More focused search using multiple indices
        results = self.directory.find_boardrooms(criteria)
        
        # Additional filtering for targeted discovery
        if len(results) > 10:  # Limit for targeted discovery
            # Prioritize by verification date (newer first)
            results.sort(key=lambda br: br.enterprise_identity.verified_at, reverse=True)
            results = results[:10]
        
        return results
    
    async def _industry_discovery(self, criteria: DiscoveryCriteria) -> List[BoardroomNode]:
        """Discover boardrooms in specific industries"""
        if not criteria.industry:
            return []
        
        return self.directory.find_boardrooms(criteria)
    
    async def _capability_discovery(self, criteria: DiscoveryCriteria) -> List[BoardroomNode]:
        """Discover boardrooms with specific capabilities"""
        if not criteria.capabilities:
            return []
        
        return self.directory.find_boardrooms(criteria)
    
    async def _location_discovery(self, criteria: DiscoveryCriteria) -> List[BoardroomNode]:
        """Discover boardrooms in specific locations"""
        if not criteria.location:
            return []
        
        return self.directory.find_boardrooms(criteria)
    
    async def discover_by_industry(self, industry: str, max_results: int = 20) -> List[BoardroomNode]:
        """Convenience method to discover boardrooms by industry"""
        criteria = DiscoveryCriteria(industry=industry, max_results=max_results)
        return await self.discover_boardrooms(criteria, DiscoveryType.INDUSTRY)
    
    async def discover_by_capability(self, capabilities: List[str], max_results: int = 20) -> List[BoardroomNode]:
        """Convenience method to discover boardrooms by capabilities"""
        criteria = DiscoveryCriteria(capabilities=set(capabilities), max_results=max_results)
        return await self.discover_boardrooms(criteria, DiscoveryType.CAPABILITY)
    
    async def discover_by_location(self, location: str, max_results: int = 20) -> List[BoardroomNode]:
        """Convenience method to discover boardrooms by location"""
        criteria = DiscoveryCriteria(location=location, max_results=max_results)
        return await self.discover_boardrooms(criteria, DiscoveryType.LOCATION)
    
    async def map_network_connections(self) -> Dict[str, Any]:
        """Map connections between boardrooms in the network"""
        network_map = {}
        
        for node_id, boardroom in self.directory.registered_boardrooms.items():
            network_map[node_id] = {
                "enterprise": boardroom.enterprise_identity.company_name,
                "industry": boardroom.enterprise_identity.industry,
                "status": boardroom.status.value,
                "connections": list(self.network_map.get(node_id, set())),
                "active_agents": list(boardroom.active_agents),
                "capabilities": list(boardroom.capabilities)
            }
        
        return {
            "total_nodes": len(network_map),
            "network_map": network_map,
            "mapped_at": datetime.now().isoformat()
        }
    
    def record_connection(self, from_node_id: str, to_node_id: str):
        """Record a connection between two boardrooms"""
        if from_node_id not in self.network_map:
            self.network_map[from_node_id] = set()
        self.network_map[from_node_id].add(to_node_id)
        
        # Also record reverse connection for bidirectional mapping
        if to_node_id not in self.network_map:
            self.network_map[to_node_id] = set()
        self.network_map[to_node_id].add(from_node_id)
    
    def get_discovery_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent discovery operations history"""
        history = sorted(self.discovery_history, 
                        key=lambda x: x["timestamp"], reverse=True)
        return history[:limit]
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        stats = self.directory.get_directory_stats()
        
        # Add discovery-specific stats
        stats.update({
            "total_discoveries": len(self.discovery_history),
            "network_connections": sum(len(connections) for connections in self.network_map.values()) // 2,
            "connected_nodes": len(self.network_map)
        })
        
        return stats

# Factory functions
def create_boardroom_directory() -> BoardroomDirectory:
    """Create a new boardroom directory"""
    return BoardroomDirectory()

def create_network_discovery(directory: BoardroomDirectory = None) -> NetworkDiscovery:
    """Create a new network discovery service"""
    return NetworkDiscovery(directory)