# Business Infinity — Mentor Mode Specification

## Purpose
Provide a safe, guided environment for fine‑tuning and testing domain‑specific LLMs, allowing stakeholders to mentor agents, test reasoning, and adjust domain lexicons without impacting live operations.

---

## Objectives
- Allow controlled experimentation with model behaviour.
- Capture human feedback as structured training signals.
- Test model responses against historical and synthetic scenarios.
- Provide both web and VS Code interfaces for different user types.

---

## Key Features
- **Sandboxed Environment:** Isolated from production decision loops.
- **Prompt/Response Testing:** Evaluate outputs against expected reasoning patterns.
- **Domain Lexicon Editor:** Add, remove, or adjust domain‑specific terms and heuristics.
- **Scenario Playback:** Replay past decisions with updated models.
- **Performance Benchmarks:** Compare model versions on accuracy, alignment, and confidence.
- **Mentor Feedback Loop:** Store feedback for future fine‑tuning.
- **Multi-Interface Support:** Web UI for business users, VS Code extension for developers.

---

## Implementation Status

### ✅ Completed Features
- **Backend API Endpoints:** Complete set of mentor mode APIs in function_app.py
- **Core Mentor Mode Class:** Local implementation with training job management
- **Web Interface:** Full-featured HTML dashboard with chat, training, and monitoring
- **Agent Integration:** Seamless integration with Business Infinity agents
- **Configuration System:** JSON-based configuration with environment variable support

### 🚧 In Progress / Future Enhancements
- **External LoRA Integration:** Connection to RealmOfAgents FineTunedLLM system
- **Advanced Scenario Management:** Persistent scenario storage and complex test cases  
- **Real-time Training Logs:** Live streaming of training progress and metrics
- **Production Deployment Pipeline:** Automated deployment of trained adapters

---

## UI Modules

### Web Dashboard (`/mentor/ui`)
- **Mentor Console:** Prompt editor, output viewer, scoring panel
- **Agent Management:** View and select available agents with LoRA versions
- **Training Interface:** Start fine-tuning jobs and monitor progress
- **Scenario Library:** Select past or synthetic cases for testing
- **Lexicon Manager:** Curate domain‑specific vocabulary and rules

### VS Code Extension (`/mentor` directory)
- **Chat Interface:** Integrated chat with Language Model Chat Provider API
- **Training Controls:** Commands for fine-tuning and deployment
- **Log Streaming:** Real-time training logs in VS Code output panel
- **Agent Selector:** Quick picker for available agents and versions
- **Status Indicators:** Show active agent, LoRA version, and job status

---

## API Endpoints

### Agent Management
- `GET /mentor/agents` - List agents with LoRA versions and capabilities
- `POST /mentor/chat/{agent_id}` - Chat with agent in sandboxed environment

### Training & Deployment  
- `POST /mentor/fine-tune/{agent_id}` - Start fine-tuning job with dataset
- `GET /mentor/logs/{job_id}` - Get training logs and progress
- `POST /mentor/deploy/{agent_id}` - Deploy trained adapter version

### UI Access
- `GET /mentor/ui` - Serve web-based mentor mode dashboard

---

## Configuration

### Environment Variables
```bash
MENTOR_MODE_ENABLED=true
OPENAIAPIKEY=your_openai_api_key
```

### Configuration File (`config/mentormodeconfig.json`)
```json
{
  "enabled": true,
  "mentor_llm": {
    "type": "openai", 
    "model": "gpt-4",
    "apikeyenv": "OPENAIAPIKEY"
  },
  "review": {
    "min_confidence": 0.75,
    "feedback_types": ["rating", "comment"]
  }
}
```

---

## Interaction Flows

### 1. Agent Testing Flow
1. **Select Agent** → Choose from available business agents (CEO, CFO, CTO, etc.)
2. **Chat Interface** → Send test prompts and evaluate responses  
3. **Collect Feedback** → Rate responses and provide improvement suggestions
4. **Iterate** → Refine prompts and test different scenarios

### 2. Fine-tuning Flow
1. **Select Agent & Dataset** → Choose agent and training data source
2. **Start Training** → Initiate LoRA fine-tuning job
3. **Monitor Progress** → View real-time logs and metrics
4. **Evaluate Results** → Test trained model against validation scenarios
5. **Deploy or Rollback** → Push to production or revert to previous version

### 3. Scenario Management Flow  
1. **Create Scenario** → Define test case with expected outputs
2. **Run Tests** → Execute scenario against multiple agent versions
3. **Compare Results** → Analyze performance differences
4. **Update Training** → Use results to improve fine-tuning data

---

## Architecture Integration

### Business Infinity Core
- **MentorMode Class:** `core/mentor_mode.py` - Main mentor functionality
- **Business Agent Integration:** Seamless interaction with existing C-Suite agents
- **Configuration Management:** Extends BusinessInfinityConfig for mentor settings

### Azure Functions Integration  
- **API Routes:** Mentor endpoints integrated with main function app
- **Authentication:** Consistent with Business Infinity security model
- **Error Handling:** Graceful degradation when external dependencies unavailable

### Future Integration Points
- **RealmOfAgents FineTunedLLM:** External LoRA management system
- **Azure Machine Learning:** Production model training and deployment
- **Service Bus Integration:** Event-driven training job orchestration

---

## Governance & Trust Elements
- **Clear Separation:** Sandbox environment isolated from production decisions
- **Version Control:** Complete rollback capability for model versions  
- **Audit Trail:** All mentor interventions logged and tracked
- **Access Control:** Role-based permissions for training and deployment
- **Safety Checks:** Automated validation before production deployment

---

## Observability & Metrics
- **Training Metrics:** Track job success rates, training time, model performance
- **Usage Analytics:** Monitor mentor mode usage patterns and user feedback
- **Agent Performance:** Compare pre/post training agent effectiveness
- **System Health:** Monitor sandbox environment and resource usage

---

## Development Notes

### VS Code Extension Development
The `/mentor` directory contains a TypeScript VS Code extension that provides:
- Language Model Chat Provider integration
- Azure Functions API client (`amlClient.ts`)
- Command palette integration for training operations
- Real-time log streaming capabilities

**Note:** Extension requires compilation and packaging before distribution.

### Future Migration
As noted in the issue, the `/mentor` directory will eventually be moved to a dedicated repository. The current implementation is designed with this separation in mind:
- Self-contained functionality in core/mentor_mode.py
- Clear API boundaries between mentor mode and main application
- Configuration abstraction for easy environment migration