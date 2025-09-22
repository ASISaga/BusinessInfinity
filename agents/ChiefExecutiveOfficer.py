"""Shim module: re-export ChiefExecutiveOfficer from RealmOfAgents/CEO.

This file keeps backward compatibility for imports that reference
`BusinessInfinity.agents.ChiefExecutiveOfficer` while the canonical
implementation lives in `RealmOfAgents/CEO/ChiefExecutiveOfficer.py`.
"""

from RealmOfAgents.CEO.ChiefExecutiveOfficer import ChiefExecutiveOfficer

__all__ = ["ChiefExecutiveOfficer"]