import json
import logging
import azure.functions as func
from ...features.storage import storage_manager

async def main(msg: func.QueueMessage):
    data = json.loads(msg.get_body().decode("utf-8"))
    try:
        # TODO: Move governance validation to a feature
        # validate_request("message", {"role": data.get("role"), "payload": data})
        pass
    except Exception as ge:
        logging.warning(f"Message rejected: {ge}")
        return
    row = storage_manager.to_row(data["boardroomId"], data["conversationId"], data)
    table_client = storage_manager.get_table_client("messages")
    table_client.create_entity(row)