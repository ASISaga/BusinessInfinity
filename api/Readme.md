# Multi-Agent Conversation REST API with Azure Functions & Cosmos DB

Below is a Python-based Azure Functions app that exposes a simple REST API to:

1. Start a multi-agent conversation  
2. Post a user message (invokes the correct domain agent)  
3. Retrieve the full message history  

We persist each conversation in Azure Cosmos DB (serverless) for low-volume, cost-effective storage.

---

1. Azure Resources & Configuration

1. Azure Functions (Consumption Plan)  
2. Azure Cosmos DB (Core SQL, serverless)  
3. Azure Blob Storage for JSON configs (agentdirectives.json, domainknowledge.json)  
4. Azure ML Online Endpoint (on-demand GPU)  
5. (Optional) Azure Container Apps for Chroma vector store (scale-to-zero)

App Settings (in Function App Configuration or local.settings.json)

Function App Layout

MyFunctionApp/
├── init.py # (not used)
├── host.json
├── local.settings.json
└── ConversationApi/
    ├── init.py # entry-point, registers all HTTP routes
    └── orchestrator.py # implements Start, PostMessage, GetMessages

# Cost-Effective Deployment Summary

- Azure Functions (Consumption): free grants → HTTP API  
- Azure Cosmos DB (serverless): pay only RU/s you consume  
- Azure Blob Storage: store JSON configs and Q&A logs at \$0.0184/GB-mo  
- Azure ML Online Endpoints: on-demand GPU (<\$0.90/hr) with auto-scale-0  
- Chroma on Azure Container Apps: scale-to-zero vector retrieval  

This API lets any Web client:

- POST /api/conversations → creates a conversation  
- POST /api/conversations/{id}/messages → sends a user message, returns agent reply  
- GET /api/conversations/{id}/messages → fetches the full chat history for display  

Your Web frontend can poll or subscribe to these endpoints to render live, multi-agent conversations.

# Mentor Interaction REST API with Azure Functions

Below is an extension of your existing Azure Functions app that adds endpoints for mentor-driven testing of domain-specific LLM/adapters, manual Q&A pair collection, and on-demand batch nuance fine-tuning via Azure ML pipelines.

---

1. New Azure Resources & Containers

1. Blob Storage  
   - Container mentorqa for mentor Q&A pairs  
2. Azure ML Pipeline Endpoint  
   - Named incr-pipeline-ep (as created previously) 

API Summary

| Endpoint | Method | Body / Query | Description |
|--------------------------------|--------|-----------------------------------------------------------------|-------------------------------------------------|
| /api/mentor/test | POST | { "domain": "...", "question": "..." } | Run LLM/adapter and return live answer |
| /api/mentor/qapair | POST | { "domain": "...", "question": "...", "answer": "..." } | Store a mentor-approved Q&A pair |
| /api/mentor/qapairs?domain= | GET | ?domain=sales | List stored Q&A pairs for a domain |
| /api/mentor/fine-tune | POST | { "domain": "sales" } | Trigger Azure ML pipeline for nuance fine-tuning|

---

4. Cost-Effective Deployment

- Azure Functions (Consumption):  
  Free grants for executions & GB-s.

- Blob Storage (mentorqa container):  
  Hot tier at \$0.0184/​GB-mo.

- Azure ML Pipeline Endpoint:  
  On-demand NC6 GPU, auto-scale 0→1 (billed by the second).

- Existing Services:  
  – Cosmos DB for user conversations (optional)  
  – Container Apps for Chroma (scale-to-zero, if used)

With this REST API in place, mentors can via a Web UI:

1. Test domain adapters in real time.  
2. Collect high-quality Q&A pairs.  
3. Kick off batch nuance fine-tuning on demand.

# Adding OAuth2 via Azure AD B2C to Secure Your Functions API

We’ll leverage Azure AD B2C for user sign-in (Authorization Code or ROPC flow) and protect all agent endpoints by validating JWTs.  

Below you’ll find:

- App Settings to configure B2C  
- A new Auth function for login/refresh  
- A helper to validate tokens  
- Updated orchestrator functions that enforce Authorization: Bearer <token>

1. Use Azure AD B2C as your OAuth2 provider—no custom identity server.  
2. Provide /auth/login and /auth/refresh for the Web client to obtain tokens.  
3. In every protected route, call validate_jwt to enforce Authorization: Bearer <token>.  
4. Manage your B2C user flows (signup/signin, password reset) in the Azure Portal.

Your Web client now:

- Redirects users to B2C or calls /auth/login (ROPC)  
- Stores the access_token and sends it in Authorization headers  
- Can refresh via /auth/refresh when expired  
- Only sees the multi-agent and mentor APIs once authenticated

# How It Works for the Mentor’s Web Client

1. List all agents  
   GET /api/agents ⇒  
   `json
   [
     {
       "domain":"sales",
       "name":"Aiden the Negotiator",
       "profile":"A seasoned sales strategist…",
       "purpose":"Help sales professionals…"
     },
     …
   ]
   `
2. Fetch one agent’s full details  
   GET /api/agents/hr ⇒  
   `json
   {
     "domain":"hr",
     "name":"Harper the People Partner",
     "profile":"An empathetic HR leader…",
     "purpose":"Guide HR leaders…",
     "context":[ … ]
   }
   `
   
All calls must include a valid Authorization: Bearer <access_token> header obtained from your B2C /auth/login flow. The mentor’s Web client can now dynamically discover each agent’s human name, profile description, purpose, and core context.