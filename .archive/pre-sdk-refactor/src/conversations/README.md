# Business Infinity Conversations System

This implementation provides a complete boardroom conversation system for Business Infinity as specified in `conversations/specification.md`.

## Features

- **40 Conversation Types**: All conversation types from the specification including strategic, financial, operational, technical, and external stakeholder communications
- **15 Agent Roles**: Complete set of internal agents (Founder, CEO, CFO, CTO, CMO, COO, CHRO, Investor) and external stakeholders (Customer, Partner, Supplier, Regulator)
- **A2A Communication**: Agent-to-Agent communication system for both internal and external stakeholder interactions
- **Signature Workflows**: Complete signature and delegation system with role-based permissions
- **Audit Trail Integration**: All conversation activities are logged with comprehensive audit trails
- **Template System**: Pre-configured conversation templates for different types and roles

## Quick Start

### Basic Usage

```python
from conversations.boardroom_conversations import BoardroomConversationManager
from conversations.conversation_system import ConversationType, ConversationRole

# Initialize conversation manager
conv_manager = BoardroomConversationManager()

# Create a strategic conversation
conv_id = await conv_manager.create_conversation(
    conversation_type=ConversationType.STRATEGIC_FRAME,
    champion=ConversationRole.FOUNDER,
    title="AI Strategy Framework",
    content="Proposed framework for integrating AI across operations"
)

# Sign the conversation
success = await conv_manager.sign_conversation(
    conv_id, 
    ConversationRole.FOUNDER, 
    "Sarah Chen (Founder)"
)
```

### A2A Communication

```python
# Internal A2A communication
a2a_id = await conv_manager.create_a2a_communication(
    from_agent=ConversationRole.CEO,
    to_agent=ConversationRole.CTO,
    conversation_type=ConversationType.TECHNICAL_DECISION,
    message_content="Need technical assessment for new AI infrastructure"
)

# External stakeholder A2A communication
external_id = await conv_manager.create_a2a_communication(
    from_agent=ConversationRole.CMO,
    to_agent=ConversationRole.CUSTOMER,
    conversation_type=ConversationType.CUSTOMER_ENROLLMENT_EXT,
    message_content="New product announcement"
)
```

### Business Infinity Integration

```python
from business_infinity import BusinessInfinity, BusinessInfinityConfig

# Initialize Business Infinity
config = BusinessInfinityConfig()
bi = BusinessInfinity(config)

# Create strategic conversation
conv_id = await bi.create_strategic_conversation(
    title="Digital Transformation Strategy",
    content="Comprehensive digital transformation roadmap"
)

# Create investment conversation
investment_id = await bi.create_investment_conversation(
    amount=1500000,
    purpose="AI infrastructure expansion"
)

# External stakeholder communication
external_id = await bi.create_external_stakeholder_communication(
    stakeholder_type="customer",
    message="New AI-powered features available"
)
```

## Architecture

The conversation system consists of:

1. **Core System** (`conversation_system.py`): Base classes, enums, and data structures
2. **Boardroom Manager** (`boardroom_conversations.py`): High-level conversation management and A2A communication
3. **Integration Layer**: Integration with autonomous boardroom and Business Infinity
4. **Audit Integration**: Complete audit trail for all conversation activities

## Conversation Types

The system implements all conversation types from the specification:

### Strategic & Governance
- Strategic Frame Conversations
- High-Risk Decision Conversations  
- Governance Review Conversations
- Company Frame Conversations

### Financial & Investment
- Investment Decision Conversations
- Budget Commitment Conversations
- Payment & Occurrence Conversations
- Risk Assessment Conversations

### Operational
- Operational Frame Conversations
- Coordination & Handoff Conversations
- Completion Conversations
- Occurrence Verification Conversations

### Technical
- Technical Decision Conversations
- Telemetry Occurrence Conversations
- Integration Coordination Conversations
- Boundary Conversations (Data/Privacy)

### External Stakeholder
- Customer Enrollment & Feedback Conversations
- Partner Enrollment & SLA Conversations
- Supplier Procurement & Delivery Conversations
- Regulator Boundary & Audit Conversations

## Agent Roles & Responsibilities

Each agent role has specific conversation types they champion and signature authorities as defined in the specification:

- **Founder**: Strategic frames, high-risk decisions, delegation authority
- **CEO**: Company frames, executive coordination, external stakeholder relationships  
- **CFO**: Financial decisions, budget commitments, compliance verification
- **CTO**: Technical decisions, telemetry, data privacy boundaries
- **CMO**: Market possibilities, customer enrollment, relationship management
- **COO**: Operational frames, commitment verification, handoff coordination
- **CHRO**: People processes, conflict resolution, culture management
- **Investor**: Investment decisions, risk assessment, governance review

## Testing

Run the comprehensive test suite:

```bash
python test_conversations.py
```

The test suite validates:
- Conversation creation and management
- A2A communication (internal and external)
- Signature workflows
- Integration with Business Infinity
- Template system functionality

## Next Steps

The conversation system is ready for:
1. Integration with real storage backends (Azure Table Storage, CosmosDB)
2. Connection to actual MCP servers for external stakeholder communication
3. Integration with LoRA adapters for enhanced agent responses
4. UI/Dashboard integration for conversation management
5. Advanced workflow automation based on conversation completion