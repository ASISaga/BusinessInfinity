from typing import Dict, Any

# Minimal MCP‑UI schema generator; expand as needed.
def get_ui_schema(role: str, scope: str) -> Dict[str, Any]:
    return {
        "role": role,
        "scope": scope,
        "panels": [
            {
                "panelId": "cmo-panel",
                "title": "Marketing",
                "actions": [
                    {
                        "id": "generate_q_plan",
                        "label": "Generate Q Marketing Plan",
                        "agentId": "cmo",
                        "uiType": "form",
                        "argsSchema": {
                            "quarter": {"type": "string", "enum": ["Q1","Q2","Q3","Q4"]},
                            "focus": {"type": "string"}
                        },
                        "scope": ["local","network"]
                    }
                ]
            }
        ]
    }