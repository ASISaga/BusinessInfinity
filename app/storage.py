import os, json, time
from typing import Dict, Any, List, Optional
from azure.data.tables import TableClient
from azure.storage.queue import QueueClient

TABLE_CONN = os.getenv("AZURE_TABLES_CONNECTION_STRING")
QUEUE_CONN = os.getenv("AZURE_QUEUES_CONNECTION_STRING")
TABLE_NAME = os.getenv("TABLE_NAME", "BoardroomMessages")
REQ_QUEUE = os.getenv("QUEUE_AGENT_REQUESTS", "agent-requests")
EVT_QUEUE = os.getenv("QUEUE_AGENT_EVENTS", "agent-events")

def table() -> TableClient:
    return TableClient.from_connection_string(TABLE_CONN, table_name=TABLE_NAME)

def queue(name: str) -> QueueClient:
    return QueueClient.from_connection_string(QUEUE_CONN, name)

def to_row(boardroom_id: str, conversation_id: str, env: Dict[str, Any]) -> Dict[str, Any]:
    # PartitionKey: boardroomId|conversationId; RowKey: sortable timestamp
    pk = f"{boardroom_id}|{conversation_id}"
    rk = f"{int(time.time()*1000):013d}-{env['messageId']}"
    return {
        "PartitionKey": pk,
        "RowKey": rk,
        "Envelope": json.dumps(env)
    }

def from_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return json.loads(row["Envelope"])

def enqueue_request(msg: Dict[str, Any]) -> None:
    q = queue(REQ_QUEUE)
    q.send_message(json.dumps(msg))

def enqueue_event(msg: Dict[str, Any]) -> None:
    q = queue(EVT_QUEUE)
    q.send_message(json.dumps(msg))

def query_messages(boardroom_id: str, conversation_id: str, since: Optional[str]) -> List[Dict[str, Any]]:
    with table() as t:
        pk = f"{boardroom_id}|{conversation_id}"
        if since:
            flt = f"PartitionKey eq '{pk}' and RowKey gt '{since}'"
        else:
            flt = f"PartitionKey eq '{pk}'"
        return [from_row(e) for e in t.query_entities(flt, results_per_page=100)]