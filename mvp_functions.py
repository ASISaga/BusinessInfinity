"""
MVP Azure Functions Replacement
Provides Azure Functions compatible endpoints using simple JSON responses
"""

import json
import logging
import os
from typing import Dict, Any, Optional
import asyncio
import threading

# MVP imports
from mvp_agents import agent_manager

logger = logging.getLogger(__name__)


class MVPFunction:
    """Simple function wrapper for MVP Azure Functions compatibility"""
    
    def __init__(self):
        self.agent_manager = agent_manager
    
    def create_response(self, data: Any, status_code: int = 200) -> Dict[str, Any]:
        """Create a standard response"""
        return {
            "statusCode": status_code,
            "body": json.dumps(data) if not isinstance(data, str) else data,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        }
    
    def health_check(self, req: Dict[str, Any] = None) -> Dict[str, Any]:
        """Health check endpoint"""
        return self.create_response({
            "status": "healthy",
            "service": "BusinessInfinity MVP Functions",
            "agents_available": len(self.agent_manager.agents),
            "version": "1.0.0-mvp",
            "endpoints": [
                "/health",
                "/agents",
                "/agents/{agent_id}",
                "/agents/{agent_id}/chat"
            ]
        })
    
    def list_agents(self, req: Dict[str, Any] = None) -> Dict[str, Any]:
        """List all available agents"""
        try:
            agents = self.agent_manager.list_agents()
            return self.create_response(agents)
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            return self.create_response({"error": "Failed to list agents"}, 500)
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get specific agent profile"""
        try:
            profile = self.agent_manager.get_agent_profile(agent_id)
            if profile:
                return self.create_response(profile)
            else:
                return self.create_response({"error": "Agent not found"}, 404)
        except Exception as e:
            logger.error(f"Error getting agent {agent_id}: {e}")
            return self.create_response({"error": "Failed to get agent"}, 500)
    
    def chat_with_agent(self, agent_id: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Chat with specific agent"""
        try:
            if not message:
                return self.create_response({"error": "Message is required"}, 400)
            
            # Run async chat in thread
            response = None
            error = None
            
            def run_chat():
                nonlocal response, error
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response = loop.run_until_complete(
                        self.agent_manager.ask_agent(agent_id, message, context or {})
                    )
                except Exception as e:
                    error = e
                finally:
                    loop.close()
            
            thread = threading.Thread(target=run_chat)
            thread.start()
            thread.join(timeout=30)  # 30 second timeout
            
            if thread.is_alive():
                return self.create_response({"error": "Request timeout"}, 408)
            
            if error:
                logger.error(f"Chat error: {error}")
                return self.create_response({"error": "Failed to process message"}, 500)
            
            if response:
                return self.create_response({
                    "agent_id": agent_id,
                    "message": message,
                    "response": response,
                    "timestamp": "2024-01-01T00:00:00Z"  # Simplified for MVP
                })
            else:
                return self.create_response({"error": "Agent not found or failed to respond"}, 404)
                
        except Exception as e:
            logger.error(f"Error in chat with agent {agent_id}: {e}")
            return self.create_response({"error": "Internal server error"}, 500)
    
    def process_http_request(self, method: str, path: str, body: Dict[str, Any] = None, query: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process HTTP request and route to appropriate function"""
        try:
            if method == "GET":
                if path == "/health":
                    return self.health_check()
                elif path == "/agents":
                    return self.list_agents()
                elif path.startswith("/agents/") and not path.endswith("/chat"):
                    agent_id = path.split("/")[-1]
                    return self.get_agent(agent_id)
                else:
                    return self.create_response({"error": "Endpoint not found"}, 404)
            
            elif method == "POST":
                if path.startswith("/agents/") and path.endswith("/chat"):
                    agent_id = path.split("/")[-2]
                    message = body.get("message", "") if body else ""
                    context = body.get("context", {}) if body else {}
                    return self.chat_with_agent(agent_id, message, context)
                else:
                    return self.create_response({"error": "Endpoint not found"}, 404)
            
            elif method == "OPTIONS":
                return self.create_response("", 200)
            
            else:
                return self.create_response({"error": "Method not allowed"}, 405)
                
        except Exception as e:
            logger.error(f"Error processing request {method} {path}: {e}")
            return self.create_response({"error": "Internal server error"}, 500)


# Global function instance
mvp_function = MVPFunction()


def azure_function_handler(req):
    """Main handler for Azure Functions compatibility"""
    try:
        # Extract request details (simplified for MVP)
        method = getattr(req, 'method', 'GET')
        url = getattr(req, 'url', '/health')
        path = url.split('?')[0]  # Remove query parameters
        
        # Get request body if present
        body = None
        if method == "POST":
            try:
                body = req.get_json() if hasattr(req, 'get_json') else {}
            except:
                body = {}
        
        # Process request
        result = mvp_function.process_http_request(method, path, body)
        
        # Return response
        if hasattr(req, 'HttpResponse'):
            # Azure Functions style response
            return req.HttpResponse(
                body=result["body"],
                status_code=result["statusCode"],
                headers=result["headers"],
                mimetype="application/json"
            )
        else:
            # Return raw result for testing
            return result
            
    except Exception as e:
        logger.error(f"Error in azure_function_handler: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
            "headers": {"Content-Type": "application/json"}
        }


# Export functions for testing
__all__ = [
    'mvp_function',
    'azure_function_handler',
    'MVPFunction'
]