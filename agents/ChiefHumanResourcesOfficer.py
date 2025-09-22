"""Shim module: re-export ChiefHumanResourcesOfficer from RealmOfAgents/CHRO.

Keeps backward compatibility for imports referencing
`BusinessInfinity.agents.ChiefHumanResourcesOfficer` while using the
canonical implementation in `RealmOfAgents/CHRO/ChiefHumanResourcesOfficer.py`.
"""

from RealmOfAgents.CHRO.ChiefHumanResourcesOfficer import ChiefHumanResourcesOfficer

__all__ = ["ChiefHumanResourcesOfficer"]