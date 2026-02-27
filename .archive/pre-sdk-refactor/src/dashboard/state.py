# state.py
founder_state = {
    "plans": { "plan-001": {"id": "plan-001", "title": "Q4 GTM Acceleration", "status": "draft"} },
    "comments": []
}

investor_state = { "risk": { "pf-001": {"market": 35, "operational": 25, "liquidity": 15, "other": 25} } }

finance_state = {
    "budgets": { "bgt-001": {"id": "bgt-001", "title": "Marketing Q4", "amount": 120000, "status": "pending"} },
    "liquidity": { "cash": 2400000, "monthly_burn": 160000, "runway_months": 15 }
}

tech_state = {
    "incidents": [
        {"id": "INC-1001", "sev": 1, "status": "open"},
        {"id": "INC-1002", "sev": 2, "status": "open"},
        {"id": "INC-1003", "sev": 2, "status": "open"}
    ]
}

ops_state = {
    "alerts": [
        {"id": "AL-42", "type": "SLA", "status": "open"},
        {"id": "AL-43", "type": "Throughput", "status": "open"}
    ]
}