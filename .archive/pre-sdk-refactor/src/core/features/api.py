"""
Consolidated API Orchestration
Merges functionality from /api/orchestrator.py and related API handling
"""

import os
import json
import uuid
import datetime
import requests
import logging
from typing import Dict, Any, Optional
import azure.functions as func

from .environment import UnifiedEnvManager
from ..agents import agent_manager
from .storage import UnifiedStorageManager
from .ml_pipeline import UnifiedMLManager

# Import authentication
try:
    from ...authentication import validate_jwt, UNAUTHORIZED_MSG
except ImportError:
    def validate_jwt(token):
        return {"valid": True}
    
    UNAUTHORIZED_MSG = "Unauthorized"


class UnifiedAPIOrchestrator:
    """
    Unified API orchestration that consolidates:
    - LinkedIn authentication
    - HTTP trigger handling
    - Auth login/refresh
    - Conversation management
    - Message handling
    """
    
    def __init__(self):
        self.env = UnifiedEnvManager()
        self.agent_manager = agent_manager
        # Lazy initialization of managers
        self._storage_manager = None
        self._ml_manager = None
    
    @property
    def storage_manager(self):
        """Lazy initialization of storage manager"""
        if self._storage_manager is None:
            self._storage_manager = UnifiedStorageManager()
        return self._storage_manager
    
    @property
    def ml_manager(self):
        """Lazy initialization of ML manager"""
        if self._ml_manager is None:
            self._ml_manager = UnifiedMLManager()
        return self._ml_manager
    
    def handle_servicebus_message(self, message_body):
        """
        Handle messages received from Azure Service Bus queue trigger.
        Process, store, or forward the message based on business logic.
        """
        logging.info(f"Processing Service Bus message: {message_body}")
        
        try:
            # Parse message if it's JSON
            if isinstance(message_body, str):
                try:
                    message_data = json.loads(message_body)
                except json.JSONDecodeError:
                    message_data = {"raw_message": message_body}
            else:
                message_data = message_body
            
            # Extract message type and route accordingly
            message_type = message_data.get("type", "unknown")
            
            if message_type == "agent_request":
                return self._handle_agent_request(message_data)
            elif message_type == "agent_event":
                return self._handle_agent_event(message_data)
            elif message_type == "decision_event":
                return self._handle_decision_event(message_data)
            else:
                logging.warning(f"Unknown message type: {message_type}")
                return True
                
        except Exception as e:
            logging.error(f"Error processing service bus message: {e}")
            return False
    
    def _handle_agent_request(self, message_data):
        """Handle agent request messages"""
        agent_id = message_data.get("agent_id")
        request = message_data.get("request", "")
        
        if agent_id and request:
            # Queue the request for processing
            try:
                self.storage_manager.enqueue_request({
                    "agent_id": agent_id,
                    "request": request,
                    "timestamp": datetime.datetime.utcnow().isoformat()
                })
                return True
            except Exception as e:
                logging.error(f"Error queuing agent request: {e}")
                return False
        
        return False
    
    def _handle_agent_event(self, message_data):
        """Handle agent event messages"""
        event_type = message_data.get("event_type")
        event_data = message_data.get("data", {})
        
        try:
            self.storage_manager.enqueue_event({
                "event_type": event_type,
                "data": event_data,
                "timestamp": datetime.datetime.utcnow().isoformat()
            })
            return True
        except Exception as e:
            logging.error(f"Error queuing agent event: {e}")
            return False
    
    def _handle_decision_event(self, message_data):
        """Handle decision event messages"""
        # Process decision events through the orchestrator
        from .. import orchestrator
        
        try:
            result = orchestrator.handle_business_event({
                "type": message_data.get("event_type", "decision_event"),
                "data": message_data.get("data", {})
            })
            logging.info(f"Decision event processed: {result}")
            return True
        except Exception as e:
            logging.error(f"Error processing decision event: {e}")
            return False
    
    def linkedin_auth_redirect(self, req: func.HttpRequest):
        """Redirect user to LinkedIn OAuth"""
        client_id = self.env.get("LINKEDIN_CLIENT_ID", "YOUR_LINKEDIN_CLIENT_ID")
        redirect_uri = self.env.get("LINKEDIN_REDIRECT_URI", "YOUR_REDIRECT_URI")
        state = str(uuid.uuid4())
        
        linkedin_auth_url = (
            f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={client_id}"
            f"&redirect_uri={redirect_uri}&state={state}&scope=r_liteprofile%20r_emailaddress"
        )
        return {"redirect_url": linkedin_auth_url, "mimetype": "text/html"}

    def linkedin_auth_callback(self, req: func.HttpRequest):
        """Exchange code for access token and get user info"""
        code = req.params.get("code")
        state = req.params.get("state")
        
        client_id = self.env.get("LINKEDIN_CLIENT_ID", "YOUR_LINKEDIN_CLIENT_ID")
        client_secret = self.env.get("LINKEDIN_CLIENT_SECRET", "YOUR_LINKEDIN_CLIENT_SECRET")
        redirect_uri = self.env.get("LINKEDIN_REDIRECT_URI", "YOUR_REDIRECT_URI")
        
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret
        }
        
        try:
            token_resp = requests.post(token_url, data=data)
            token_resp.raise_for_status()
            token_json = token_resp.json()
            access_token = token_json.get("access_token")
            
            # Get user info
            headers = {"Authorization": f"Bearer {access_token}"}
            profile_resp = requests.get("https://api.linkedin.com/v2/people/~", headers=headers)
            profile_resp.raise_for_status()
            profile_data = profile_resp.json()
            
            email_resp = requests.get("https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))", headers=headers)
            email_resp.raise_for_status()
            email_data = email_resp.json()
            
            email = email_data.get("elements", [{}])[0].get("handle~", {}).get("emailAddress", "")
            
            return {
                "profile": profile_data,
                "email": email,
                "mimetype": "application/json"
            }
        except Exception as e:
            logging.error(f"LinkedIn auth error: {e}")
            return {
                "error": "Authentication failed",
                "mimetype": "application/json"
            }

    def extract_name(self, req: func.HttpRequest):
        """Extract name from request (HTTP trigger)"""
        name = req.params.get('name')
        if not name:
            try:
                req_body = req.get_json()
            except ValueError:
                req_body = None
            if req_body:
                name = req_body.get('name')

        if name:
            return {
                "message": f"Hello, {name}. This HTTP triggered function executed successfully.",
                "status_code": 200
            }
        else:
            return {
                "message": "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
                "status_code": 200
            }

    def login(self, req: func.HttpRequest) -> func.HttpResponse:
        """Handle login requests"""
        try:
            req_body = req.get_json()
            username = req_body.get("username")
            password = req_body.get("password")
            
            # Simple authentication logic (enhance as needed)
            if username and password:
                # Generate a simple token (in production, use proper JWT)
                token = f"token_{uuid.uuid4()}"
                return func.HttpResponse(
                    json.dumps({"token": token, "username": username}),
                    mimetype="application/json",
                    status_code=200
                )
            else:
                return func.HttpResponse(
                    json.dumps({"error": "Username and password required"}),
                    mimetype="application/json",
                    status_code=400
                )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    def refresh(self, req: func.HttpRequest) -> func.HttpResponse:
        """Handle token refresh requests"""
        try:
            req_body = req.get_json()
            old_token = req_body.get("token")
            
            if old_token:
                # Generate new token (enhance with proper validation)
                new_token = f"token_{uuid.uuid4()}"
                return func.HttpResponse(
                    json.dumps({"token": new_token}),
                    mimetype="application/json",
                    status_code=200
                )
            else:
                return func.HttpResponse(
                    json.dumps({"error": "Token required"}),
                    mimetype="application/json",
                    status_code=400
                )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    def start_conversation(self, req: func.HttpRequest):
        """Start a new conversation"""
        try:
            req_body = req.get_json()
            domain = req_body.get("domain", "general")
            
            conv_id = str(uuid.uuid4())
            
            # Create conversation in storage
            try:
                self.storage_manager.create_conversation(conv_id, domain)
                return {
                    "conversationId": conv_id,
                    "domain": domain,
                    "status_code": 201
                }
            except Exception as e:
                logging.error(f"Error creating conversation: {e}")
                return {
                    "error": "Failed to create conversation",
                    "status_code": 500
                }
                
        except Exception as e:
            return {
                "error": f"Invalid request: {str(e)}",
                "status_code": 400
            }

    async def post_message(self, req: func.HttpRequest):
        """Post a message to a conversation"""
        try:
            conversation_id = req.route_params.get("id")
            req_body = req.get_json()
            message = req_body.get("message", "")
            sender = req_body.get("sender", "user")
            
            if not message:
                return {
                    "error": "Message content required",
                    "status_code": 400
                }
            
            # Get conversation
            conv_json = self.storage_manager.get_conversation(conversation_id)
            if not conv_json:
                return {
                    "error": "Conversation not found",
                    "status_code": 404
                }
            
            conv = json.loads(conv_json)
            domain = conv.get("domain", "general")
            
            # Add user message to conversation
            messages = json.loads(conv.get("messages", "[]"))
            messages.append({
                "sender": sender,
                "text": message,
                "time": datetime.datetime.utcnow().isoformat()
            })
            conv["messages"] = json.dumps(messages)
            
            # Get agent response if sender is user
            if sender == "user":
                try:
                    agent_response = await self.agent_manager.ask_agent(domain, message)
                    if agent_response:
                        self.storage_manager.upsert_conversation(conv, domain, agent_response)
                        return {
                            "message": "Message posted and agent response added",
                            "agent_response": json.loads(agent_response),
                            "status_code": 200
                        }
                except Exception as e:
                    logging.error(f"Error getting agent response: {e}")
            
            # Update conversation without agent response
            self.storage_manager.upsert_conversation(conv)
            return {
                "message": "Message posted",
                "status_code": 200
            }
            
        except Exception as e:
            logging.error(f"Error posting message: {e}")
            return {
                "error": f"Failed to post message: {str(e)}",
                "status_code": 500
            }

    def get_conversation(self, req: func.HttpRequest):
        """Get a conversation by ID"""
        try:
            conversation_id = req.route_params.get("id")
            conv_json = self.storage_manager.get_conversation(conversation_id)
            
            if conv_json:
                return {
                    "conversation": json.loads(conv_json),
                    "status_code": 200
                }
            else:
                return {
                    "error": "Conversation not found",
                    "status_code": 404
                }
        except Exception as e:
            return {
                "error": f"Failed to get conversation: {str(e)}",
                "status_code": 500
            }

    def get_messages(self, req: func.HttpRequest):
        """Get messages for a conversation"""
        try:
            conversation_id = req.route_params.get("id")
            conv_json = self.storage_manager.get_conversation(conversation_id)
            
            if conv_json:
                return {
                    "conv_json": conv_json,
                    "status_code": 200
                }
            else:
                return {
                    "error": "Conversation not found", 
                    "status_code": 404
                }
        except Exception as e:
            return {
                "error": f"Failed to get messages: {str(e)}",
                "status_code": 500
            }

    async def mentor_test(self, req: func.HttpRequest):
        """Test mentor functionality with an agent"""
        try:
            req_body = req.get_json()
            domain = req_body.get("domain", "general")
            question = req_body.get("question", "")
            
            if not question:
                return {
                    "error": "Question is required",
                    "status_code": 400
                }
            
            # Use agent manager to get response
            answer_json = await self.agent_manager.ask_agent(domain, question)
            if answer_json:
                return {
                    "answer_json": answer_json,
                    "status_code": 200
                }
            else:
                return {
                    "error": f"Agent {domain} not found",
                    "status_code": 404
                }
                
        except Exception as e:
            return {
                "error": f"Mentor test failed: {str(e)}",
                "status_code": 500
            }

    def mentorsubmitqa(self, req: func.HttpRequest):
        """Submit Q&A pair for mentor training"""
        try:
            req_body = req.get_json()
            domain = req_body.get("domain", "")
            question = req_body.get("question", "")
            answer = req_body.get("answer", "")
            
            if not all([domain, question, answer]):
                return {
                    "error": "Domain, question, and answer are required",
                    "status_code": 400
                }
            
            # Upload Q&A pair to storage
            self.storage_manager.upload_mentor_qa_pair(domain, question, answer)
            return {"status_code": 200}
            
        except Exception as e:
            return {
                "error": f"Failed to submit Q&A pair: {str(e)}",
                "status_code": 500
            }

    def mentorlistqa(self, req: func.HttpRequest):
        """List Q&A pairs for a domain"""
        try:
            domain = req.params.get("domain", "")
            if not domain:
                return {
                    "error": "Domain parameter required",
                    "status_code": 400
                }
            
            pairs_json = self.storage_manager.get_mentor_qa_pairs(domain)
            return {
                "pairs_json": pairs_json,
                "status_code": 200
            }
            
        except Exception as e:
            return {
                "error": f"Failed to list Q&A pairs: {str(e)}",
                "status_code": 500
            }

    def mentortriggerfine_tune(self, req: func.HttpRequest):
        """Trigger fine-tuning for a domain"""
        try:
            req_body = req.get_json()
            domain = req_body.get("domain", "")
            
            if not domain:
                return {
                    "error": "Domain is required",
                    "status_code": 400
                }
            
            # Invoke ML pipeline for fine-tuning
            result_json = self.ml_manager.invoke_pipeline(domain)
            return {
                "result_json": result_json,
                "status_code": 200
            }
            
        except Exception as e:
            return {
                "error": f"Failed to trigger fine-tuning: {str(e)}",
                "status_code": 500
            }

    def list_agents(self, req: func.HttpRequest):
        """List all available agents"""
        try:
            agents_json = self.agent_manager.get_agent_profiles()
            return {
                "agents_json": agents_json,
                "status_code": 200
            }
        except Exception as e:
            return {
                "error": f"Failed to list agents: {str(e)}",
                "status_code": 500
            }

    def get_agent(self, req: func.HttpRequest):
        """Get a specific agent profile"""
        try:
            agent_id = req.route_params.get("agentId")
            prof_json = self.agent_manager.get_agent_profile(agent_id)
            
            if prof_json:
                return {
                    "prof_json": prof_json,
                    "status_code": 200
                }
            else:
                return {
                    "error": f"Agent {agent_id} not found",
                    "status_code": 404
                }
        except Exception as e:
            return {
                "error": f"Failed to get agent: {str(e)}",
                "status_code": 500
            }

    async def chat(self, req: func.HttpRequest):
        """Chat with a specific agent"""
        try:
            agent_id = req.route_params.get("agentId")
            req_body = req.get_json()
            message = req_body.get("message", "")
            
            if not message:
                return {
                    "error": "Message is required",
                    "status_code": 400
                }
            
            answer_json = await self.agent_manager.ask_agent(agent_id, message)
            if answer_json:
                return {
                    "answer_json": answer_json,
                    "status_code": 200
                }
            else:
                return {
                    "error": f"Agent {agent_id} not found",
                    "status_code": 404
                }
                
        except Exception as e:
            return {
                "error": f"Chat failed: {str(e)}",
                "status_code": 500
            }