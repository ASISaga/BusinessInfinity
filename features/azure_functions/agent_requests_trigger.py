import json, time
import azure.functions as func
from azure.storage.queue import QueueClient
import os
from ...features.agents import agent_manager

EVT_QUEUE = os.getenv("QUEUE_AGENT_EVENTS", "agent-events")
QUEUE_CONN = os.getenv("AZURE_QUEUES_CONNECTION_STRING")

def events_queue() -> QueueClient:
    return QueueClient.from_connection_string(QUEUE_CONN, EVT_QUEUE)

async def main(msg: func.QueueMessage):
    env = json.loads(msg.get_body().decode("utf-8"))
    agent_id = env["senderAgentId"]
    args = env["payload"]
    # Map action+args to a prompt. For production, select prompt per action schema.
    prompt = f"Action={args.get('action')}\nArgs={json.dumps(args.get('args', {}))}"
    output = await agent_manager.run_agent(agent_id, prompt)

    event = {
        **env,
        "messageType": "toolResult",
        "payload": {"action": args.get("action"), "result": output},
        "timestamp": time.time()
    }
    events_queue().send_message(json.dumps(event))