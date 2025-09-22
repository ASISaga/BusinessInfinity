"""
Shim module: re-export ChiefTechnologyOfficer from RealmOfAgents/CTO.

Keeps backward compatibility for imports referencing
`BusinessInfinity.agents.ChiefTechnologyOfficer` while using the
canonical implementation in `RealmOfAgents/CTO/ChiefTechnologyOfficer.py`.
"""

from RealmOfAgents.CTO.ChiefTechnologyOfficer import ChiefTechnologyOfficer

__all__ = ["ChiefTechnologyOfficer"]