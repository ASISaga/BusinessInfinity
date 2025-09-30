import json
import azure.functions as func
from datetime import datetime, timezone

# === Boardroom Conversation Endpoints ===

class ConversationsEndpoint:
    def __init__(self, business_infinity=None, logger=None):
        self.business_infinity = business_infinity
        self.logger = logger

    async def list_conversations(self, req: func.HttpRequest) -> func.HttpResponse:
        """List boardroom conversations with optional filtering"""
        try:
            if not self.business_infinity:
                return func.HttpResponse(
                    json.dumps({"error": "Business Infinity not available"}),
                    mimetype="application/json",
                    status_code=503
                )

            # Get query parameters
            champion = req.params.get('champion')
            status = req.params.get('status')
            limit = int(req.params.get('limit', 50))

            # Get conversations from Business Infinity
            conversations = []

            if champion:
                # Get conversations for specific agent
                agent_conversations = await self.business_infinity.get_agent_conversations(champion)
                if "championed" in agent_conversations:
                    conversations = agent_conversations["championed"]
            else:
                # Get all conversations (this would need a new method)
                conversations = []

            # Apply status filter if specified
            if status:
                conversations = [conv for conv in conversations if conv.get("status") == status]

            # Limit results
            conversations = conversations[:limit]

            return func.HttpResponse(
                json.dumps({
                    "conversations": conversations,
                    "count": len(conversations),
                    "champion": champion,
                    "status": status
                }),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error listing conversations: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    async def get_conversation(self, req: func.HttpRequest) -> func.HttpResponse:
        """Get a specific conversation by ID"""
        try:
            conversation_id = req.route_params.get('conversation_id')
            if not conversation_id:
                return func.HttpResponse(
                    json.dumps({"error": "Conversation ID required"}),
                    mimetype="application/json",
                    status_code=400
                )

            if not self.business_infinity or not self.business_infinity.autonomous_boardroom:
                return func.HttpResponse(
                    json.dumps({"error": "Business Infinity boardroom not available"}),
                    mimetype="application/json",
                    status_code=503
                )

            # Get conversation from boardroom
            conversation_manager = self.business_infinity.autonomous_boardroom.conversation_manager
            if not conversation_manager:
                return func.HttpResponse(
                    json.dumps({"error": "Conversation manager not available"}),
                    mimetype="application/json",
                    status_code=503
                )

            conversation = await conversation_manager.get_conversation(conversation_id)

            if conversation:
                return func.HttpResponse(
                    json.dumps({
                        "conversation": conversation.to_dict(),
                        "conversation_id": conversation_id
                    }),
                    mimetype="application/json",
                    status_code=200
                )
            else:
                return func.HttpResponse(
                    json.dumps({"error": "Conversation not found"}),
                    mimetype="application/json",
                    status_code=404
                )

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting conversation {conversation_id}: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    async def create_conversation(self, req: func.HttpRequest) -> func.HttpResponse:
        """Create a new boardroom conversation"""
        try:
            if not self.business_infinity:
                return func.HttpResponse(
                    json.dumps({"error": "Business Infinity not available"}),
                    mimetype="application/json",
                    status_code=503
                )

            # Parse request body
            try:
                conv_data = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    mimetype="application/json",
                    status_code=400
                )

            # Validate required fields
            required_fields = ["conversation_type", "champion", "title", "content"]
            for field in required_fields:
                if field not in conv_data:
                    return func.HttpResponse(
                        json.dumps({"error": f"Missing required field: {field}"}),
                        mimetype="application/json",
                        status_code=400
                    )

            # Create conversation
            conversation_id = await self.business_infinity.create_boardroom_conversation(
                conversation_type=conv_data["conversation_type"],
                champion_role=conv_data["champion"],
                title=conv_data["title"],
                content=conv_data["content"],
                context=conv_data.get("context", {})
            )

            if conversation_id:
                return func.HttpResponse(
                    json.dumps({
                        "conversation_id": conversation_id,
                        "status": "created",
                        "message": "Conversation created successfully"
                    }),
                    mimetype="application/json",
                    status_code=201
                )
            else:
                return func.HttpResponse(
                    json.dumps({"error": "Failed to create conversation"}),
                    mimetype="application/json",
                    status_code=500
                )

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error creating conversation: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    async def sign_conversation(self, req: func.HttpRequest) -> func.HttpResponse:
        """Sign a conversation"""
        try:
            conversation_id = req.route_params.get('conversation_id')
            if not conversation_id:
                return func.HttpResponse(
                    json.dumps({"error": "Conversation ID required"}),
                    mimetype="application/json",
                    status_code=400
                )

            if not self.business_infinity:
                return func.HttpResponse(
                    json.dumps({"error": "Business Infinity not available"}),
                    mimetype="application/json",
                    status_code=503
                )

            # Parse request body
            try:
                sign_data = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    mimetype="application/json",
                    status_code=400
                )

            # Validate required fields
            if "signer_role" not in sign_data or "signer_name" not in sign_data:
                return func.HttpResponse(
                    json.dumps({"error": "Missing required fields: signer_role, signer_name"}),
                    mimetype="application/json",
                    status_code=400
                )

            # Sign conversation
            success = await self.business_infinity.sign_conversation(
                conversation_id=conversation_id,
                signer_role=sign_data["signer_role"],
                signer_name=sign_data["signer_name"]
            )

            if success:
                return func.HttpResponse(
                    json.dumps({
                        "conversation_id": conversation_id,
                        "status": "signed",
                        "message": f"Conversation signed by {sign_data['signer_name']}",
                        "signer": {
                            "name": sign_data["signer_name"],
                            "role": sign_data["signer_role"]
                        }
                    }),
                    mimetype="application/json",
                    status_code=200
                )
            else:
                return func.HttpResponse(
                    json.dumps({"error": "Failed to sign conversation"}),
                    mimetype="application/json",
                    status_code=400
                )

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error signing conversation {conversation_id}: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    async def create_a2a_communication(self, req: func.HttpRequest) -> func.HttpResponse:
        """Create Agent-to-Agent communication"""
        try:
            if not self.business_infinity:
                return func.HttpResponse(
                    json.dumps({"error": "Business Infinity not available"}),
                    mimetype="application/json",
                    status_code=503
                )

            # Parse request body
            try:
                a2a_data = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    mimetype="application/json",
                    status_code=400
                )

            # Validate required fields
            required_fields = ["from_agent", "to_agent", "conversation_type", "message"]
            for field in required_fields:
                if field not in a2a_data:
                    return func.HttpResponse(
                        json.dumps({"error": f"Missing required field: {field}"}),
                        mimetype="application/json",
                        status_code=400
                    )

            # Create A2A communication
            conversation_id = await self.business_infinity.initiate_a2a_communication(
                from_agent=a2a_data["from_agent"],
                to_agent=a2a_data["to_agent"],
                conversation_type=a2a_data["conversation_type"],
                message=a2a_data["message"],
                context=a2a_data.get("context", {})
            )

            if conversation_id:
                return func.HttpResponse(
                    json.dumps({
                        "conversation_id": conversation_id,
                        "status": "created",
                        "message": "A2A communication created successfully",
                        "from_agent": a2a_data["from_agent"],
                        "to_agent": a2a_data["to_agent"]
                    }),
                    mimetype="application/json",
                    status_code=201
                )
            else:
                return func.HttpResponse(
                    json.dumps({"error": "Failed to create A2A communication"}),
                    mimetype="application/json",
                    status_code=500
                )

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error creating A2A communication: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    async def get_conversation_events(self, req: func.HttpRequest) -> func.HttpResponse:
        """Get conversation events for web client updates"""
        try:
            if not self.business_infinity or not self.business_infinity.autonomous_boardroom:
                return func.HttpResponse(
                    json.dumps({"error": "Business Infinity boardroom not available"}),
                    mimetype="application/json",
                    status_code=503
                )

            # Get query parameters
            since_timestamp = req.params.get('since')
            limit = int(req.params.get('limit', 100))

            # Get conversation manager
            conversation_manager = self.business_infinity.autonomous_boardroom.conversation_manager
            if not conversation_manager:
                return func.HttpResponse(
                    json.dumps({"error": "Conversation manager not available"}),
                    mimetype="application/json",
                    status_code=503
                )

            # Get web events
            events = await conversation_manager.get_web_events_since(since_timestamp)

            # Limit results
            events = events[:limit]

            return func.HttpResponse(
                json.dumps({
                    "events": events,
                    "count": len(events),
                    "since": since_timestamp,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                mimetype="application/json",
                status_code=200
            )

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting conversation events: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    async def conversations_dashboard(self, req: func.HttpRequest) -> func.HttpResponse:
        """Serve the conversations dashboard"""
        try:
            import os
            dashboard_path = os.path.join(os.path.dirname(__file__), "conversations", "dashboard.html")

            if os.path.exists(dashboard_path):
                with open(dashboard_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return func.HttpResponse(
                    content,
                    mimetype="text/html",
                    status_code=200
                )
            else:
                return func.HttpResponse(
                    "<h1>Dashboard not found</h1><p>The conversations dashboard file was not found.</p>",
                    mimetype="text/html",
                    status_code=404
                )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error serving conversations dashboard: {e}")
            return func.HttpResponse(
                f"<h1>Error</h1><p>Failed to load dashboard: {str(e)}</p>",
                mimetype="text/html",
                status_code=500
            )

