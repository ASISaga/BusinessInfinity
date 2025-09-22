"""Shim module: re-export ChiefMarketingOfficer from RealmOfAgents/CMO.

Keeps backward compatibility for imports referencing
`BusinessInfinity.agents.ChiefMarketingOfficer` while using the
canonical implementation in `RealmOfAgents/CMO/ChiefMarketingOfficer.py`.
"""

from RealmOfAgents.CMO.ChiefMarketingOfficer import ChiefMarketingOfficer

__all__ = ["ChiefMarketingOfficer"]