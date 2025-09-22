"""
Minimal API Server for BusinessInfinity MVP
Uses Python's built-in HTTP server to avoid external dependencies
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import asyncio
import threading
from typing import Dict, Any, Optional
import traceback

from mvp_agents import agent_manager

logger = logging.getLogger(__name__)


class MVPAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MVP API"""
    
    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response"""
        response_json = json.dumps(data, indent=2)
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(response_json.encode())
    
    def _send_html_response(self, html: str, status_code: int = 200):
        """Send HTML response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def _get_request_body(self) -> Optional[Dict[str, Any]]:
        """Get JSON request body"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode()
                return json.loads(body)
        except Exception as e:
            logger.error(f"Error reading request body: {e}")
        return None
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            params = parse_qs(parsed_url.query)
            
            if path == '/':
                self._handle_index()
            elif path == '/health':
                self._handle_health()
            elif path == '/agents':
                self._handle_list_agents()
            elif path.startswith('/agents/'):
                agent_id = path.split('/')[-1]
                self._handle_get_agent(agent_id)
            elif path == '/dashboard':
                self._handle_dashboard()
            else:
                self._send_json_response({"error": "Not found"}, 404)
                
        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self._send_json_response({"error": "Internal server error"}, 500)
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            body = self._get_request_body()
            
            if path.startswith('/agents/') and path.endswith('/chat'):
                agent_id = path.split('/')[-2]
                self._handle_chat(agent_id, body)
            else:
                self._send_json_response({"error": "Not found"}, 404)
                
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self._send_json_response({"error": "Internal server error"}, 500)
    
    def _handle_index(self):
        """Handle index page"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Business Infinity MVP</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .agent-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
                .agent-card { border: 1px solid #ddd; padding: 15px; border-radius: 8px; background: #f9f9f9; }
                .agent-card h3 { margin: 0 0 10px 0; color: #333; }
                .chat-button { background: #007bff; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
                .chat-button:hover { background: #0056b3; }
            </style>
        </head>
        <body>
            <h1>Business Infinity MVP</h1>
            <p>Your AI-powered C-Suite and Founder agents are ready to assist.</p>
            
            <div id="agents">Loading agents...</div>
            
            <script>
                // Load agents
                fetch('/agents')
                    .then(response => response.json())
                    .then(agents => {
                        const container = document.getElementById('agents');
                        container.innerHTML = '<div class="agent-list">' + 
                            agents.map(agent => `
                                <div class="agent-card">
                                    <h3>${agent.name}</h3>
                                    <p><strong>Role:</strong> ${agent.role}</p>
                                    <p><strong>Conversations:</strong> ${agent.conversation_count}</p>
                                    <button class="chat-button" onclick="window.location.href='/dashboard?agent=${agent.id}'">
                                        Chat with ${agent.role}
                                    </button>
                                </div>
                            `).join('') + 
                        '</div>';
                    })
                    .catch(error => {
                        document.getElementById('agents').innerHTML = '<p>Error loading agents: ' + error.message + '</p>';
                    });
            </script>
        </body>
        </html>
        """
        self._send_html_response(html)
    
    def _handle_health(self):
        """Handle health check"""
        self._send_json_response({
            "status": "healthy",
            "service": "BusinessInfinity MVP",
            "agents_available": len(agent_manager.agents),
            "version": "1.0.0-mvp"
        })
    
    def _handle_list_agents(self):
        """Handle list agents request"""
        agents = agent_manager.list_agents()
        self._send_json_response(agents)
    
    def _handle_get_agent(self, agent_id: str):
        """Handle get agent profile request"""
        profile = agent_manager.get_agent_profile(agent_id)
        if profile:
            self._send_json_response(profile)
        else:
            self._send_json_response({"error": "Agent not found"}, 404)
    
    def _handle_chat(self, agent_id: str, body: Dict[str, Any]):
        """Handle chat request with agent"""
        if not body or 'message' not in body:
            self._send_json_response({"error": "Message is required"}, 400)
            return
        
        message = body['message']
        context = body.get('context', {})
        
        # Run async chat in thread
        def run_chat():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    agent_manager.ask_agent(agent_id, message, context)
                )
                if response:
                    self._send_json_response({
                        "agent_id": agent_id,
                        "message": message,
                        "response": response
                    })
                else:
                    self._send_json_response({"error": "Agent not found or failed to respond"}, 404)
            except Exception as e:
                logger.error(f"Chat error: {e}")
                self._send_json_response({"error": "Internal server error"}, 500)
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_chat)
        thread.start()
        thread.join(timeout=30)  # 30 second timeout
        
        if thread.is_alive():
            self._send_json_response({"error": "Request timeout"}, 408)
    
    def _handle_dashboard(self):
        """Handle dashboard page"""
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)
        selected_agent = params.get('agent', ['ceo'])[0]
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Business Infinity Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }}
                .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
                .agent-selector {{ margin-bottom: 20px; }}
                .chat-container {{ display: flex; gap: 20px; height: 600px; }}
                .chat-messages {{ flex: 1; border: 1px solid #ddd; padding: 20px; overflow-y: auto; background: #f9f9f9; }}
                .agent-info {{ width: 300px; border: 1px solid #ddd; padding: 20px; background: #fff; }}
                .message {{ margin-bottom: 15px; }}
                .user-message {{ color: #007bff; font-weight: bold; }}
                .agent-response {{ color: #333; margin-left: 20px; }}
                .chat-input {{ display: flex; gap: 10px; margin-top: 20px; }}
                .chat-input input {{ flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }}
                .chat-input button {{ padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }}
                .chat-input button:hover {{ background: #0056b3; }}
                select {{ padding: 8px; border-radius: 4px; border: 1px solid #ddd; }}
                .back-button {{ padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 4px; text-decoration: none; }}
                .back-button:hover {{ background: #545b62; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Business Infinity Dashboard</h1>
                <a href="/" class="back-button">← Back to Home</a>
            </div>
            
            <div class="agent-selector">
                <label for="agent-select">Select Agent: </label>
                <select id="agent-select" onchange="switchAgent()">
                    <option value="">Loading...</option>
                </select>
            </div>
            
            <div class="chat-container">
                <div class="chat-messages" id="messages">
                    <p>Select an agent to start chatting...</p>
                </div>
                <div class="agent-info" id="agent-info">
                    <h3>Agent Information</h3>
                    <div id="agent-details">Select an agent to view details...</div>
                </div>
            </div>
            
            <div class="chat-input">
                <input type="text" id="message-input" placeholder="Type your message here..." onkeypress="if(event.key==='Enter') sendMessage()">
                <button onclick="sendMessage()">Send</button>
            </div>
            
            <script>
                let currentAgent = '{selected_agent}';
                let chatHistory = [];
                
                // Load agents into selector
                fetch('/agents')
                    .then(response => response.json())
                    .then(agents => {{
                        const select = document.getElementById('agent-select');
                        select.innerHTML = agents.map(agent => 
                            `<option value="${{agent.id}}" ${{agent.id === currentAgent ? 'selected' : ''}}>${{agent.name}}</option>`
                        ).join('');
                        
                        if (currentAgent) {{
                            loadAgentInfo();
                        }}
                    }});
                
                function switchAgent() {{
                    currentAgent = document.getElementById('agent-select').value;
                    chatHistory = [];
                    document.getElementById('messages').innerHTML = '<p>Chat cleared. Start a new conversation...</p>';
                    loadAgentInfo();
                }}
                
                function loadAgentInfo() {{
                    if (!currentAgent) return;
                    
                    fetch(`/agents/${{currentAgent}}`)
                        .then(response => response.json())
                        .then(agent => {{
                            document.getElementById('agent-details').innerHTML = `
                                <h4>${{agent.name}}</h4>
                                <p><strong>Role:</strong> ${{agent.role}}</p>
                                <p><strong>Created:</strong> ${{new Date(agent.created_at).toLocaleDateString()}}</p>
                                <p><strong>Conversations:</strong> ${{agent.conversation_count}}</p>
                            `;
                        }});
                }}
                
                function sendMessage() {{
                    const input = document.getElementById('message-input');
                    const message = input.value.trim();
                    if (!message || !currentAgent) return;
                    
                    // Add user message to chat
                    addMessage('You', message, 'user-message');
                    input.value = '';
                    
                    // Show thinking indicator
                    const thinkingId = addMessage(currentAgent.toUpperCase(), 'Thinking...', 'agent-response');
                    
                    // Send to agent
                    fetch(`/agents/${{currentAgent}}/chat`, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ message: message }})
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        // Remove thinking indicator
                        document.getElementById(thinkingId).remove();
                        
                        if (data.response) {{
                            addMessage(currentAgent.toUpperCase(), data.response, 'agent-response');
                        }} else {{
                            addMessage(currentAgent.toUpperCase(), 'Sorry, I had trouble processing that request.', 'agent-response');
                        }}
                    }})
                    .catch(error => {{
                        // Remove thinking indicator
                        document.getElementById(thinkingId).remove();
                        addMessage(currentAgent.toUpperCase(), 'Error: ' + error.message, 'agent-response');
                    }});
                }}
                
                function addMessage(sender, text, className) {{
                    const messagesDiv = document.getElementById('messages');
                    const messageDiv = document.createElement('div');
                    const messageId = 'msg-' + Date.now() + '-' + Math.random();
                    messageDiv.id = messageId;
                    messageDiv.className = 'message';
                    messageDiv.innerHTML = `<div class="${{className}}">${{sender}}:</div><div class="agent-response">${{text}}</div>`;
                    messagesDiv.appendChild(messageDiv);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                    return messageId;
                }}
            </script>
        </body>
        </html>
        """
        self._send_html_response(html)
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass


class MVPServer:
    """Simple HTTP server for MVP"""
    
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.server = None
        
    def start(self):
        """Start the server"""
        try:
            self.server = HTTPServer((self.host, self.port), MVPAPIHandler)
            logger.info(f"BusinessInfinity MVP Server starting at http://{self.host}:{self.port}")
            print(f"🚀 BusinessInfinity MVP Server running at http://{self.host}:{self.port}")
            print("📊 Available endpoints:")
            print(f"   • http://{self.host}:{self.port}/ - Main interface")
            print(f"   • http://{self.host}:{self.port}/health - Health check")
            print(f"   • http://{self.host}:{self.port}/agents - List agents")
            print(f"   • http://{self.host}:{self.port}/dashboard - Dashboard")
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")
            if self.server:
                self.server.shutdown()
        except Exception as e:
            logger.error(f"Server error: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = MVPServer()
    server.start()