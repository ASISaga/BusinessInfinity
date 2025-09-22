"""Shim module: re-export InvestorAgent from RealmOfAgents/Investor.

Keeps backward compatibility for imports referencing
`BusinessInfinity.agents.InvestorAgent` while using the
canonical implementation in `RealmOfAgents/Investor/InvestorAgent.py`.
"""

from RealmOfAgents.Investor.InvestorAgent import InvestorAgent

__all__ = ["InvestorAgent"]