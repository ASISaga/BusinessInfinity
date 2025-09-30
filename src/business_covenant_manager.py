"""
BusinessCovenantManager - Handles covenant and network management for Business Infinity
"""
import logging
from typing import Dict, Any, Optional, List


class BusinessCovenantManager:
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.covenant_id = None
        self.covenant_status = "not_created"
        self.covenant_manager = None
        self.verification_service = None
        self.network_discovery = None

    async def initialize(self):
        # Restore covenant, verification, and network discovery services if available
        self.logger.info("BusinessCovenantManager initializing...")
        self.covenant_manager = getattr(self.config, "covenant_manager", None)
        self.verification_service = getattr(self.config, "verification_service", None)
        self.network_discovery = getattr(self.config, "network_discovery", None)
        self.covenant_id = None
        self.covenant_status = "not_created"
        await self.initialize_covenant()
        self.logger.info("BusinessCovenantManager initialized")

    async def initialize_covenant(self):
        if not getattr(self.config, "enable_covenant_compliance", True) or not self.covenant_manager:
            self.logger.info("Covenant compliance disabled, skipping covenant initialization")
            return
        covenant_id = await self._load_existing_covenant()
        if covenant_id:
            self.covenant_id = covenant_id
            self.covenant_status = await self.covenant_manager.get_covenant_status(covenant_id)
            self.logger.info(f"Loaded existing covenant: {covenant_id} (status: {self.covenant_status})")
        elif getattr(self.config, "linkedin_company_url", None):
            covenant_id = await self._create_enterprise_covenant()
            if covenant_id:
                self.covenant_id = covenant_id
                self.covenant_status = "draft"
                self.logger.info(f"Created new covenant: {covenant_id}")
        else:
            self.logger.warning("No LinkedIn company URL provided, covenant creation skipped")

    async def shutdown(self):
        self.logger.info("BusinessCovenantManager shutdown")

    async def publish_covenant(self) -> bool:
        self.logger.info("Stub: publish_covenant")
        return True

    async def get_covenant_status(self) -> Dict[str, Any]:
        self.logger.info("Stub: get_covenant_status")
        return {"covenant_exists": False, "status": "not_created"}

    async def propose_covenant_amendment(self, changes: Dict[str, Any], rationale: str, proposer_agent: str = "ceo") -> Optional[str]:
        self.logger.info("Stub: propose_covenant_amendment")
        return None

    async def vote_on_amendment(self, amendment_id: str, agent_id: str, vote: str, rationale: str = None) -> bool:
        self.logger.info("Stub: vote_on_amendment")
        return True

    async def discover_peer_boardrooms(self, criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        self.logger.info("Stub: discover_peer_boardrooms")
        return []

    async def get_compliance_statistics(self) -> Dict[str, Any]:
        self.logger.info("Stub: get_compliance_statistics")
        return {}

    async def _load_existing_covenant(self) -> Optional[str]:
        return None

    async def _create_enterprise_covenant(self) -> Optional[str]:
        try:
            enterprise_data = {
                "company_name": self.config.company_name,
                "linkedin_url": self.config.linkedin_company_url,
                "industry": self.config.industry,
                "jurisdiction": "United States",
                "mission_statement": f"To operate {self.config.company_name} as an autonomous, transparent, and collaborative enterprise within the global network of verified businesses.",
                "core_values": ["Innovation", "Transparency", "Collaboration", "Integrity", "Excellence", "Sustainability"],
                "declaration_of_intent": (
                    f"We, {self.config.company_name}, hereby commit to operating as a verified member "
                    f"of the Global Boardroom Network, maintaining the highest standards of transparency, "
                    f"accountability, and collaboration in all our autonomous business operations."
                )
            }
            governance_preferences = {
                "quorum_requirement": self.config.covenant_quorum_requirement,
                "consensus_threshold": self.config.covenant_consensus_threshold,
                "amendment_cooling_period": self.config.amendment_cooling_period,
                "federation_participation": self.config.federation_participation,
                "public_reporting": False,
                "external_arbitration": False
            }
            covenant_id = await self.covenant_manager.create_covenant(enterprise_data, governance_preferences)
            return covenant_id
        except Exception as e:
            self.logger.error(f"Failed to create enterprise covenant: {e}")
            return None

    async def publish_covenant(self) -> bool:
        if not self.covenant_manager or not self.covenant_id:
            self.logger.error("Cannot publish covenant - covenant not initialized")
            return False
        try:
            success = await self.covenant_manager.publish_covenant(self.covenant_id)
            if success:
                self.covenant_status = "pending"
                self.logger.info("Covenant published successfully")
            return success
        except Exception as e:
            self.logger.error(f"Failed to publish covenant: {e}")
            return False

    async def get_covenant_status(self) -> Dict[str, Any]:
        if not self.covenant_manager or not self.covenant_id:
            return {"covenant_exists": False, "status": "not_created", "message": "No covenant initialized"}
        try:
            covenant = await self.covenant_manager.get_covenant(self.covenant_id)
            if not covenant:
                return {"covenant_exists": False, "status": "not_found"}
            return {
                "covenant_exists": True,
                "covenant_id": self.covenant_id,
                "status": self.covenant_status,
                "company_name": covenant.get("identity", {}).get("company_name"),
                "verification_status": covenant.get("identity", {}).get("linkedin_verification", {}).get("verification_status"),
                "recognition_count": covenant.get("provenance", {}).get("recognition_status", {}).get("recognition_count", 0),
                "bic_badge": covenant.get("provenance", {}).get("recognition_status", {}).get("bic_badge", {}),
                "last_validated": covenant.get("compliance_metadata", {}).get("last_validated"),
                "compliance_score": covenant.get("compliance_metadata", {}).get("validation_score", 0)
            }
        except Exception as e:
            self.logger.error(f"Failed to get covenant status: {e}")
            return {"error": str(e)}

    async def propose_covenant_amendment(self, changes: Dict[str, Any], rationale: str, proposer_agent: str = "ceo") -> Optional[str]:
        if not self.covenant_manager or not self.covenant_id:
            self.logger.error("Cannot propose amendment - covenant not initialized")
            return None
        try:
            amendment_id = await self.covenant_manager.propose_amendment(self.covenant_id, proposer_agent, changes, rationale)
            self.logger.info(f"Amendment proposed: {amendment_id}")
            return amendment_id
        except Exception as e:
            self.logger.error(f"Failed to propose amendment: {e}")
            return None

    async def vote_on_amendment(self, amendment_id: str, agent_id: str, vote: str, rationale: str = None) -> bool:
        if not self.covenant_manager or not self.covenant_id:
            self.logger.error("Cannot vote on amendment - covenant not initialized")
            return False
        try:
            success = await self.covenant_manager.vote_on_amendment(self.covenant_id, amendment_id, agent_id, vote, rationale)
            if success:
                self.logger.info(f"Vote cast by {agent_id} on amendment {amendment_id}: {vote}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to vote on amendment: {e}")
            return False

    async def discover_peer_boardrooms(self, criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if not self.network_discovery:
            self.logger.error("Network discovery not initialized")
            return []
        try:
            from .network.discovery import DiscoveryCriteria, DiscoveryType
            discovery_criteria = DiscoveryCriteria(
                industry=criteria.get("industry") if criteria else self.config.industry,
                verification_required=True,
                max_results=criteria.get("max_results", 20) if criteria else 20
            )
            if criteria and "capabilities" in criteria:
                discovery_criteria.capabilities = set(criteria["capabilities"])
            boardrooms = await self.network_discovery.discover_boardrooms(discovery_criteria, DiscoveryType.INDUSTRY)
            results = []
            for boardroom in boardrooms:
                results.append({
                    "node_id": boardroom.node_id,
                    "company_name": boardroom.enterprise_identity.company_name,
                    "industry": boardroom.enterprise_identity.industry,
                    "size": boardroom.enterprise_identity.size,
                    "location": boardroom.enterprise_identity.location,
                    "verification_status": boardroom.enterprise_identity.verification_status,
                    "capabilities": list(boardroom.capabilities),
                    "status": boardroom.status.value
                })
            self.logger.info(f"Discovered {len(results)} peer boardrooms")
            return results
        except Exception as e:
            self.logger.error(f"Failed to discover peer boardrooms: {e}")
            return []

    async def get_compliance_statistics(self) -> Dict[str, Any]:
        if not self.covenant_manager:
            return {"error": "Covenant management not initialized"}
        try:
            stats = self.covenant_manager.get_compliance_statistics()
            if self.covenant_id:
                covenant_status = await self.get_covenant_status()
                stats["enterprise_covenant"] = covenant_status
            return stats
        except Exception as e:
            self.logger.error(f"Failed to get compliance statistics: {e}")
            return {"error": str(e)}
