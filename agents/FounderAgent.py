"""Shim module: re-export FounderAgent from RealmOfAgents/Founder.

Keeps backward compatibility for imports referencing
`BusinessInfinity.agents.FounderAgent` while using the
canonical implementation in `RealmOfAgents/Founder/FounderAgent.py`.
"""

from RealmOfAgents.Founder.FounderAgent import FounderAgent

__all__ = ["FounderAgent"]