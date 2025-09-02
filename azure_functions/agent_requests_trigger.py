"""
Agent Requests Trigger - Updated to use new trigger structure

This module now imports from the consolidated triggers module.
The actual trigger implementation is in triggers/queue_triggers.py
"""

import logging
from triggers.queue_triggers import register_queue_triggers

# For backward compatibility, we can still provide the main function
# but it now delegates to the consolidated trigger system
async def main(msg):
    """
    Legacy main function for backward compatibility.
    The actual trigger is now registered in triggers/queue_triggers.py
    """
    logging.info("agent_requests_trigger.main() called - this function is deprecated.")
    logging.info("Trigger functionality has been moved to triggers/queue_triggers.py")
    logging.info("Please use the new trigger registration system.")
    
    # We could call the new trigger function here if needed for compatibility
    # But it's better to use the new system directly