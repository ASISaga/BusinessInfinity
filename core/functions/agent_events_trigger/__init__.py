import json
import logging
import azure.functions as func
from ..app.governance import validate_request, GovernanceError
from ..app.storage import to_row, table

async def main(msg: func.QueueMessage):
    data = json.loads(msg.get_body().decode("utf-8"))
    try:
        validate_request("message", {"role": data.get("role"), "payload": data})
    except GovernanceError as ge:
        logging.warning(f"Message rejected by governance: {ge}")
        return
    row = to_row(data["boardroomId"], data["conversationId"], data)
    with table() as t:
        t.create_entity(row)