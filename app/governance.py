from typing import Dict, Any

class GovernanceError(Exception): 
    """Exception raised when governance validation fails"""
    pass

def validate_request(context: str, payload: Dict[str, Any]) -> None:
    """
    Validate requests based on context and payload
    Context ∈ {"inference","message","training"}
    """
    # Insert role/scope/tool checks here. Raise on deny.
    # Example: deny network scope for training from non‑governance role.
    if context == "training" and payload.get("role") != "Governance":
        # Allow demo training only if explicit demo flag on payload
        if not payload.get("demo", False):
            raise GovernanceError("Training not permitted for this role.")
    
    # Add other validation rules as needed
    pass