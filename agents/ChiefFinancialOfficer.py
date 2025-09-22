"""Shim module: re-export ChiefFinancialOfficer from RealmOfAgents/CFO.

Keeps backward compatibility for imports referencing
`BusinessInfinity.agents.ChiefFinancialOfficer` while using the
canonical implementation in `RealmOfAgents/CFO/ChiefFinancialOfficer.py`.
"""

from RealmOfAgents.CFO.ChiefFinancialOfficer import ChiefFinancialOfficer

__all__ = ["ChiefFinancialOfficer"]