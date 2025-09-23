# Business Infinity - AOS-Based Business Application

Business Infinity is a comprehensive business application built on top of the Agent Operating System (AOS) from RealmOfAgents. It provides strategic decision-making, operational execution, and growth management capabilities through AI-powered C-Suite agents, Founder, and Investor agents.

## Architecture Overview

```
Business Infinity (Business Application Layer)
├── business_infinity.py          # Main Business Infinity application
├── business_agents.py           # Business-specific agent implementations
├── function_app.py              # Azure Functions HTTP API
├── core/                        # Core integration modules
│   ├── agents.py               # Unified agent management
│   └── utils.py                # Utility functions
└── mvp_agents.py               # Fallback MVP implementations

Agent Operating System (AOS Foundation)
├── RealmOfAgents/AgentOperatingSystem/
│   ├── aos_core.py             # Core AOS kernel
│   ├── AgentOperatingSystem.py # Main AOS entry point
│   ├── config.py               # Configuration management
│   ├── messaging.py            # Message bus infrastructure
│   ├── orchestration.py        # Workflow orchestration
│   ├── storage.py              # Storage abstraction
│   └── monitoring.py           # System monitoring
```

## Key Components

### 1. Business Infinity Core (`business_infinity.py`)

The main business application that orchestrates all business operations:

- **BusinessInfinity Class**: Main application orchestrator
- **BusinessInfinityConfig**: Configuration management
- **Strategic Decision Making**: Multi-agent collaborative decision processes
- **Business Workflow Execution**: End-to-end business process automation
- **Agent Management**: Registration and coordination of business agents

### 2. Business Agents (`business_agents.py`)

Specialized business agents built on AOS foundation:

- **BusinessCEO**: Strategic leadership and vision
- **BusinessCFO**: Financial leadership and analysis  
- **BusinessCTO**: Technology leadership and innovation
- **BusinessFounder**: Vision, innovation, and entrepreneurial leadership
- **BusinessInvestor**: Investment analysis and funding strategy

Each agent provides:
- Domain-specific expertise and analysis
- KPI tracking and performance metrics
- Collaborative decision-making capabilities
- Business context awareness

### 3. Azure Functions API (`function_app.py`)

RESTful API and event processing:

- **HTTP Endpoints**: `/health`, `/agents`, `/agents/{role}/ask`, `/decisions`, `/workflows/{name}`
- **Service Bus Integration**: Decision queue and business event processing
- **Fallback Support**: Graceful degradation when components unavailable

### 4. Unified Agent Management (`core/agents.py`)

Centralized agent management system:

- **UnifiedAgentManager**: Single interface for all agent operations
- **Backward Compatibility**: Support for legacy systems
- **Fallback Implementation**: MVP agents when full system unavailable

## Features

### Strategic Decision Making
- Multi-stakeholder decision processes
- Role-based expertise integration
- Consensus and delegation modes
- Decision history and tracking

### Business Workflow Orchestration
- Pre-defined business workflows (product launch, funding rounds)
- Custom workflow definition support
- Step-by-step execution with agent coordination
- Progress monitoring and status tracking

### Agent Collaboration
- Inter-agent communication via AOS message bus
- Collaborative analysis and recommendations
- Domain expertise sharing
- Performance monitoring and optimization

### Mentor Mode
- **Sandboxed Environment**: Safe testing and fine-tuning of business agents
- **Agent Training**: LoRA fine-tuning with domain-specific datasets
- **Web Interface**: Intuitive dashboard at `/mentor/ui` endpoint
- **VS Code Extension**: Developer-focused control surface in `/mentor` directory
- **Version Management**: Track and compare different agent model versions
- **Scenario Testing**: Evaluate agent performance against test cases

### Scalable Architecture
- Built on AOS foundation for reliability
- Azure Functions for serverless scaling
- Service Bus for event-driven processing
- Storage abstraction for data persistence

## Getting Started

### Prerequisites
- Python 3.9+
- Azure Functions Core Tools (for local development)
- Access to RealmOfAgents/AgentOperatingSystem

### Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp local.settings.json.template local.settings.json
   # Edit local.settings.json with your configuration
   ```

3. **Initialize Business Infinity**:
   ```python
   from business_infinity import create_business_infinity
   
   # Create Business Infinity instance
   bi = create_business_infinity()
   
   # Ask an agent
   response = await bi.ask_agent("CEO", "What's our market strategy?")
   
   # Make a strategic decision
   decision = await bi.make_strategic_decision({
       "type": "strategic",
       "context": "Market expansion opportunity"
   })
   ```

### Running Locally

1. **Start Azure Functions**:
   ```bash
   func start
   ```

2. **Test Health Endpoint**:
   ```bash
   curl http://localhost:7071/api/health
   ```

3. **Ask an Agent**:
   ```bash
   curl -X POST http://localhost:7071/api/agents/CEO/ask \
        -H "Content-Type: application/json" \
        -d '{"message": "What are our strategic priorities?"}'
   ```

## API Reference

### Health Check
```
GET /api/health
```
Returns system status and component availability.

### List Agents
```
GET /api/agents
```
Returns all available business agents with their roles and status.

### Ask Agent
```
POST /api/agents/{role}/ask
Content-Type: application/json

{
  "message": "Your question or request",
  "context": {}  // Optional context
}
```

### Strategic Decision
```
POST /api/decisions  
Content-Type: application/json

{
  "type": "strategic|financial|technical|operational",
  "context": "Decision context and parameters",
  "stakeholders": ["CEO", "CFO", "CTO"]  // Optional
}
```

### Execute Workflow
```
POST /api/workflows/{workflow_name}
Content-Type: application/json

{
  "params": {
    // Workflow-specific parameters
  }
}
```

## Configuration

### Business Infinity Config

```python
class BusinessInfinityConfig:
    business_name: str = "Business Infinity"
    industry: str = "Technology" 
    stage: str = "Growth"  # Startup, Growth, Mature
    market: str = "Global"
    
    # Agent configuration
    enable_c_suite: bool = True
    enable_founder: bool = True 
    enable_investor: bool = True
    
    # Operational settings
    decision_threshold: float = 0.7
    collaboration_mode: str = "consensus"  # consensus, delegation, hierarchy
    reporting_enabled: bool = True
    metrics_collection: bool = True
```

### Environment Variables

- `BUSINESS_NAME`: Your business name
- `BUSINESS_INDUSTRY`: Industry sector
- `BUSINESS_STAGE`: Business maturity stage
- `TARGET_MARKET`: Target market scope
- `ServiceBusConnection`: Azure Service Bus connection string

## Workflows

### Product Launch Workflow
1. Market Analysis (CMO)
2. Product Strategy (CEO)  
3. Technical Implementation (CTO)
4. Financial Planning (CFO)
5. Operational Readiness (COO)
6. Launch Execution (CEO)

### Funding Round Workflow
1. Financial Assessment (CFO)
2. Investor Outreach (Investor)
3. Pitch Preparation (Founder)
4. Due Diligence (CEO)
5. Negotiation (Founder)
6. Closing (CFO)

## Integration with AOS

Business Infinity leverages the Agent Operating System for:

- **Agent Lifecycle Management**: Registration, initialization, shutdown
- **Message Bus**: Inter-agent communication and event routing  
- **Decision Engine**: Structured decision-making processes
- **Workflow Orchestration**: Step-by-step process execution
- **Storage Management**: Persistent data and state management
- **System Monitoring**: Performance metrics and health tracking

## Development and Testing

### Running Tests
```bash
python validate_system.py
```

### Adding New Agents
1. Create agent class inheriting from `BusinessAgent`
2. Implement domain-specific analysis methods
3. Define expertise areas and decision frameworks
4. Register agent in `business_infinity.py`

### Adding New Workflows
1. Define workflow steps in `_get_business_workflow_definition`
2. Map steps to appropriate agents
3. Test workflow execution via API

## Deployment

### Azure Functions Deployment
```bash
# Build and deploy
func azure functionapp publish your-function-app-name
```

### Configuration
- Set environment variables in Azure Functions configuration
- Configure Service Bus connections
- Set up monitoring and logging

## Troubleshooting

### Common Issues

1. **AOS Not Available**: System falls back to MVP agents
2. **Agent Initialization Failed**: Check configuration and dependencies
3. **Decision Timeout**: Verify agent responsiveness and reduce complexity
4. **Workflow Stuck**: Check individual step execution and agent status

### Logging
- Enable DEBUG logging for detailed execution traces
- Check Azure Functions logs for runtime issues
- Monitor Service Bus for message processing status

## Contributing

1. Follow the established architecture patterns
2. Maintain backward compatibility where possible
3. Add comprehensive tests for new features
4. Update documentation for API changes

## License

[License details based on your project's license]