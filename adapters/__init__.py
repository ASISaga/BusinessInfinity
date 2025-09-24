"""
Business Infinity LoRA Adapters Module

This module implements the complete LoRA adapter system for Business Infinity
boardroom agents as defined in the adapter specifications.

Key Components:
- LoRAAdapterManager: Manages domain and leadership adapter loading/fusion
- SelfLearningSystem: Implements continuous learning with mentor feedback
- ModelUpgradeManager: Handles 8B → 13B model upgrades
- EvaluationHarness: Comprehensive evaluation metrics and testing
- AdapterOrchestrator: Main coordination layer

Usage:
    from adapters import initialize_adapter_system, generate_boardroom_response
    
    # Initialize the adapter system
    orchestrator = await initialize_adapter_system()
    
    # Generate response from CFO agent
    response = await generate_boardroom_response("cfo", "Analyze Q4 budget allocation")
    
    # Evaluate the response
    evaluation = await evaluate_boardroom_response("cfo", response["response"])

Architecture:
- Base Model: Llama-3.1-8B-Instruct (QLoRA 4-bit)
- Domain Adapters: CFO, CMO, COO, CTO, Founder, Investor (rank 32-48)
- Leadership Adapter: Cross-role tone and synthesis (rank 12)
- Fusion: Weighted combination (domain 0.68-0.78, leadership 0.22-0.32)
- Self-Learning: 60-80% original + 20-40% mentor feedback data
- Upgrade Path: Preserves learning when migrating to 13B model
"""

from .lora_adapter_manager import (
    LoRAAdapterManager, 
    BoardroomRole, 
    AdapterType,
    AdapterConfig,
    ModelConfig
)

from .self_learning_system import (
    SelfLearningSystem,
    LearningPhase,
    DatasetType,
    Situation,
    MentorFeedback,
    TrainingExample,
    LearningMetrics
)

from .model_upgrade_manager import (
    ModelUpgradeManager,
    UpgradePhase,
    UpgradeStatus,
    UpgradeCondition,
    PerformanceComparison,
    UpgradeJob
)

from .evaluation_harness import (
    EvaluationHarness,
    MetricType,
    EvaluationLevel,
    RoleFidelityMetrics,
    LeadershipClarityMetrics,
    ConflictIndexMetrics,
    GuardrailComplianceMetrics,
    EvaluationResult,
    EvaluationScenario
)

from .adapter_orchestrator import (
    AdapterOrchestrator,
    SystemStatus,
    SystemMetrics,
    adapter_orchestrator,
    initialize_adapter_system,
    generate_boardroom_response,
    evaluate_boardroom_response,
    start_learning_cycle,
    get_system_status
)

__version__ = "1.0.0"

__all__ = [
    # Core managers
    "LoRAAdapterManager",
    "SelfLearningSystem", 
    "ModelUpgradeManager",
    "EvaluationHarness",
    "AdapterOrchestrator",
    
    # Data classes and enums
    "BoardroomRole",
    "AdapterType",
    "AdapterConfig",
    "ModelConfig",
    "LearningPhase",
    "DatasetType",
    "UpgradePhase", 
    "UpgradeStatus",
    "MetricType",
    "EvaluationLevel",
    "SystemStatus",
    
    # Key data structures
    "Situation",
    "MentorFeedback",
    "TrainingExample",
    "LearningMetrics",
    "UpgradeCondition",
    "PerformanceComparison",
    "UpgradeJob",
    "RoleFidelityMetrics",
    "LeadershipClarityMetrics", 
    "ConflictIndexMetrics",
    "GuardrailComplianceMetrics",
    "EvaluationResult",
    "EvaluationScenario",
    "SystemMetrics",
    
    # Global orchestrator
    "adapter_orchestrator",
    
    # Convenience functions
    "initialize_adapter_system",
    "generate_boardroom_response",
    "evaluate_boardroom_response",
    "start_learning_cycle",
    "get_system_status"
]

# Module-level documentation
__doc__ += """

Adapter System Architecture:

1. LoRA Adapter Loading Pipeline:
   - Domain-specific adapters for each boardroom role
   - Single leadership adapter for executive framing
   - Weighted fusion with role-specific weights
   - Support for runtime adapter swapping

2. Self-Learning Loop:
   - Situation generation for agent evaluation
   - Mentor feedback collection and processing
   - Dataset expansion with versioning
   - Continuous fine-tuning with blended datasets

3. Model Upgrade System:
   - 8B → 13B migration with preserved learning
   - Parallel evaluation and performance comparison
   - Gradual transition with rollback capabilities
   - Distillation for style continuity

4. Evaluation Framework:
   - Role fidelity scoring
   - Leadership clarity assessment
   - Conflict resolution measurement
   - Guardrail compliance checking

Integration Points:
- Business Infinity autonomous boardroom
- FineTunedLLM external components (when available)
- Azure ML for training pipelines
- MCP servers for business system integration

For detailed specifications, see:
- /adapters/Specifications.md
- /adapters/Readme.md
"""