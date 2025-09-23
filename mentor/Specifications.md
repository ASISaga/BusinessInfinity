# Mentor Mode VS Code Extension Specification

## 1. Purpose
Provide a developer‑centric control surface inside VS Code to:
- Test LLM LoRA adapters for each Boardroom agent.
- Trigger fine‑tuning jobs.
- Monitor training progress and metrics.
- Deploy updated adapters to production.

---

## 2. Components

### 2.1 VS Code Extension
- **Language Model Chat Provider API** implementation.
- **Agent Selector**: Lists all Boardroom agents (from AML metadata).
- **Chat Interface**: Send prompts to selected agent’s LoRA model and receive streamed responses.
- **Commands**:
  - `boardroom.listAgents` → Fetch agent list + LoRA versions.
  - `boardroom.chatWithAgent` → Send prompt to AML endpoint.
  - `boardroom.fineTuneAgent` → Trigger fine‑tuning job via Azure Function.
  - `boardroom.viewTrainingLogs` → Stream AML logs into VS Code output panel.
  - `boardroom.deployAdapter` → Update Boardroom registry to new LoRA version.
  - `boardroom.compareVersions` → Run side‑by‑side tests between LoRA versions.

### 2.2 Azure Functions Backend
- **Endpoints**:
  - `GET /agents` → Returns agent metadata from AML.
  - `POST /chat/:agentId` → Routes prompt to AML Online Endpoint with correct LoRA.
  - `POST /fine-tune/:agentId` → Starts AML fine‑tuning job.
  - `GET /logs/:jobId` → Streams training logs.
  - `POST /deploy/:agentId` → Updates Boardroom registry mapping.
- **Security**:
  - Azure AD authentication.
  - Role‑based access (developer/admin).

### 2.3 Azure Machine Learning
- **Assets**:
  - Base model.
  - Per‑agent LoRA adapters (registered models).
- **Jobs**:
  - Fine‑tuning jobs triggered by Azure Functions.
  - Versioning for rollback and comparison.
- **Endpoints**:
  - Online inference endpoints per agent.

---

## 3. Data Flow
1. **Agent List Retrieval**  
   VS Code → Azure Function `/agents` → AML model registry → VS Code displays list.
2. **Chat Request**  
   VS Code → `/chat/:agentId` → AML endpoint (base + LoRA) → Streamed response back to VS Code.
3. **Fine‑Tune Job**  
   VS Code → `/fine-tune/:agentId` → AML job start → Logs streamed via `/logs/:jobId`.
4. **Deploy Adapter**  
   VS Code → `/deploy/:agentId` → Boardroom registry updated → New LoRA live.
5. **Version Comparison**  
   VS Code → Chat with two LoRA versions → Display outputs side‑by‑side.

---

## 4. UI/UX in VS Code
- **Chat Panel**: Standard Copilot‑style chat with agent selector.
- **Output Panel**: Real‑time training logs.
- **Quick Pick Menus**: For selecting agents, datasets, or LoRA versions.
- **Status Bar Indicators**: Show active agent, LoRA version, and training job status.

---

## 5. Technical Requirements
- **Language**: TypeScript (compiled to JS for VS Code extension host).
- **Runtime**: Node.js (extension host).
- **Dependencies**:
  - `axios` for HTTP calls.
  - `@types/vscode` for API typings.
- **Auth**: Azure AD OAuth token stored in VS Code’s secure storage.
- **Streaming**: Use `sendPartialResponse()` for incremental output in chat.

---

## 6. Security & Access Control
- Only authenticated developers can trigger fine‑tuning or deploy adapters.
- Read‑only access for testing agents without making changes.
- Audit logs stored in Azure Table Storage.