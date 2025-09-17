"""
Queue Triggers for Azure Functions

This module contains all Azure Storage Queue triggers consolidated from function_app.py
and azure_functions/
"""

import json
import logging
import azure.functions as func
from azure.storage.queue import QueueClient
import os
import time

# Import consolidated core system
from core import storage_manager, agent_manager

# Import utilities
try:
    from utils.governance import validate_request, GovernanceError
except ImportError:
    def validate_request(request_type, data):
        return True
    
    class GovernanceError(Exception):
        pass


def register_queue_triggers(app: func.FunctionApp):
    """Register all queue trigger handlers with the FunctionApp"""
    
    # Queue trigger function for agent events (consolidated from function_app.py and azure_functions/)
    @app.queue_trigger(arg_name="msg", queue_name="%QUEUE_AGENT_EVENTS%", 
                       connection="AZURE_QUEUES_CONNECTION_STRING")
    async def agent_events_trigger(msg: func.QueueMessage):
        """Agent events queue trigger - consolidated functionality"""
        data = json.loads(msg.get_body().decode("utf-8"))
        
        try:
            validate_request("message", {"role": data.get("role"), "payload": data})
            row = storage_manager.to_row(data["boardroomId"], data["conversationId"], data)
            with storage_manager.get_table_client() as t:
                t.create_entity(row)
        except ImportError as e:
            logging.error(f"Failed to import dependencies: {e}")
            return
        except Exception as ge:
            logging.warning(f"Message rejected by governance: {ge}")
            return

    # Queue trigger for agent requests (from azure_functions/agent_requests_trigger.py)
    @app.queue_trigger(arg_name="msg", queue_name="%QUEUE_AGENT_REQUESTS%",
                       connection="AZURE_QUEUES_CONNECTION_STRING")
    async def agent_requests_trigger(msg: func.QueueMessage):
        """Agent requests queue trigger - processes agent execution requests"""
        try:
            env = json.loads(msg.get_body().decode("utf-8"))
            agent_id = env["senderAgentId"]
            args = env["payload"]
            
            # Map action+args to a prompt. For production, select prompt per action schema.
            prompt = f"Action={args.get('action')}\nArgs={json.dumps(args.get('args', {}))}"
            output = await agent_manager.run_agent(agent_id, prompt)

            # Create event response
            event = {
                **env,
                "messageType": "toolResult",
                "payload": {"action": args.get("action"), "result": output},
                "timestamp": time.time()
            }
            
            # Send result to events queue
            events_queue_name = os.getenv("QUEUE_AGENT_EVENTS", "agent-events")
            queue_conn = os.getenv("AZURE_QUEUES_CONNECTION_STRING")
            if queue_conn and events_queue_name:
                queue_client = QueueClient.from_connection_string(queue_conn, events_queue_name)
                queue_client.send_message(json.dumps(event))
                
        except Exception as e:
            logging.error(f"Error processing agent request: {e}")
            return