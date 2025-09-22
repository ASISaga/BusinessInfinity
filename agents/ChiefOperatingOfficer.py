"""Shim module: re-export ChiefOperatingOfficer from RealmOfAgents/COO.

Keeps backward compatibility for imports referencing
`BusinessInfinity.agents.ChiefOperatingOfficer` while using the
canonical implementation in `RealmOfAgents/COO/ChiefOperatingOfficer.py`.
"""

from RealmOfAgents.COO.ChiefOperatingOfficer import ChiefOperatingOfficer

__all__ = ["ChiefOperatingOfficer"]