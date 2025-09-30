"""
LoRA Adapter Manager for Business Infinity Boardroom Agents

This module implements the LoRA adapter loading, management, and orchestration
system as defined in the adapter specifications. Provides domain-specific and
leadership adapter fusion with configurable weights.

Architecture:
- Domain LoRAs: CFO, CMO, COO, CTO, Founder, Investor
- Leadership LoRA: Cross-role tone and decision framing
- Orchestration: Always one domain + leadership adapter
- Model Support: Llama-3.1-8B-Instruct → 13B upgrade path
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# LoRA and model imports
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import PeftModel, LoraConfig, get_peft_model
    LORA_AVAILABLE = True
except ImportError:
    LORA_AVAILABLE = False
    logging.warning("LoRA libraries not available - using stubs")

logger = logging.getLogger(__name__)


class BoardroomRole(Enum):
    """Boardroom roles with LoRA adapters"""
    CFO = "cfo"
    CMO = "cmo" 
    COO = "coo"
    CTO = "cto"
    FOUNDER = "founder"
    INVESTOR = "investor"


class AdapterType(Enum):
    """Types of LoRA adapters"""
    DOMAIN = "domain"
    LEADERSHIP = "leadership"


@dataclass
class AdapterConfig:
    """Configuration for a LoRA adapter"""
    role: str
    adapter_type: AdapterType
    rank: int
    alpha: int
    target_modules: List[str]
    layer_range: Tuple[int, int]
    fusion_weight: float
    path: str
    version: str = "v1.0.0"
    performance_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ModelConfig:
    """Configuration for base model"""
    model_name: str = "meta-llama/Llama-3.1-8B-Instruct"
    quantization: str = "QLoRA-4bit"
    device: str = "auto"
    max_memory: Optional[Dict[str, str]] = None


class LoRAAdapterManager:
    """
    Manages LoRA adapter loading, orchestration, and inference for boardroom agents.
    
    Key Features:
    - Domain + Leadership adapter fusion
    - Configurable fusion weights per role
    - Model upgrade path (8B → 13B)
    - Performance metrics tracking
    """
    
    def __init__(self, config_path: str = None, model_config: ModelConfig = None):
        self.config_path = config_path or self._default_config_path()
        self.model_config = model_config or ModelConfig()
        
        # State
        self.base_model = None
        self.tokenizer = None
        self.loaded_adapters: Dict[str, Any] = {}
        self.adapter_configs: Dict[str, AdapterConfig] = {}
        self.active_model = None
        
        # Load adapter configurations
        self._load_adapter_configs()
        
        logger.info(f"LoRA Adapter Manager initialized with config: {self.config_path}")
    
    def _default_config_path(self) -> str:
        """Get default adapter configuration path"""
        return os.path.join(os.path.dirname(__file__), "adapter_configs.json")
    
    def _load_adapter_configs(self):
        """Load adapter configurations from JSON file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    
                for role_key, config in config_data.get("domain_adapters", {}).items():
                    self.adapter_configs[f"domain_{role_key}"] = AdapterConfig(
                        role=role_key,
                        adapter_type=AdapterType.DOMAIN,
                        rank=config["rank"],
                        alpha=config["alpha"], 
                        target_modules=config["target_modules"],
                        layer_range=tuple(config["layer_range"]),
                        fusion_weight=config["fusion_weight"],
                        path=config.get("path", f"./adapters/{role_key}_domain_lora")
                    )
                
                # Leadership adapter config
                leadership_config = config_data.get("leadership_adapter", {})
                self.adapter_configs["leadership"] = AdapterConfig(
                    role="leadership",
                    adapter_type=AdapterType.LEADERSHIP,
                    rank=leadership_config.get("rank", 12),
                    alpha=leadership_config.get("alpha", 12),
                    target_modules=leadership_config.get("target_modules", ["o_proj", "down_proj"]),
                    layer_range=tuple(leadership_config.get("layer_range", [24, 32])),
                    fusion_weight=0.0,  # Will be set based on role
                    path=leadership_config.get("path", "./adapters/leadership_lora")
                )
                
            else:
                # Generate default configs based on specifications
                self._generate_default_configs()
                
        except Exception as e:
            logger.error(f"Failed to load adapter configs: {e}")
            self._generate_default_configs()
    
    def _generate_default_configs(self):
        """Generate default adapter configurations based on specifications"""
        
        # Domain adapter configs based on specifications
        domain_configs = {
            "cfo": {"rank": 48, "alpha": 32, "fusion_weight": 0.78},
            "cmo": {"rank": 48, "alpha": 32, "fusion_weight": 0.68},
            "coo": {"rank": 48, "alpha": 32, "fusion_weight": 0.74},
            "cto": {"rank": 48, "alpha": 32, "fusion_weight": 0.72},
            "founder": {"rank": 36, "alpha": 18, "fusion_weight": 0.70},
            "investor": {"rank": 40, "alpha": 32, "fusion_weight": 0.76}
        }
        
        standard_target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
        
        for role, config in domain_configs.items():
            self.adapter_configs[f"domain_{role}"] = AdapterConfig(
                role=role,
                adapter_type=AdapterType.DOMAIN,
                rank=config["rank"],
                alpha=config["alpha"],
                target_modules=standard_target_modules,
                layer_range=(8, 28),  # Middle-upper layers
                fusion_weight=config["fusion_weight"],
                path=f"./adapters/{role}_domain_lora"
            )
        
        # Leadership adapter
        self.adapter_configs["leadership"] = AdapterConfig(
            role="leadership",
            adapter_type=AdapterType.LEADERSHIP,
            rank=12,
            alpha=12,
            target_modules=["o_proj", "down_proj"],
            layer_range=(24, 32),  # Upper layers only
            fusion_weight=0.0,  # Set dynamically based on role
            path="./adapters/leadership_lora"
        )
        
        logger.info("Generated default adapter configurations")
    
    async def initialize_model(self):
        """Initialize the base model and tokenizer"""
        if not LORA_AVAILABLE:
            logger.warning("LoRA libraries not available - using stub implementation")
            self.base_model = "stub_model"
            self.tokenizer = "stub_tokenizer"
            return
            
        try:
            logger.info(f"Loading base model: {self.model_config.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_config.model_name,
                trust_remote_code=True
            )
            
            # Load model with quantization if specified
            if self.model_config.quantization == "QLoRA-4bit":
                from transformers import BitsAndBytesConfig
                
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True
                )
                
                self.base_model = AutoModelForCausalLM.from_pretrained(
                    self.model_config.model_name,
                    quantization_config=quantization_config,
                    device_map=self.model_config.device,
                    max_memory=self.model_config.max_memory,
                    trust_remote_code=True
                )
            else:
                self.base_model = AutoModelForCausalLM.from_pretrained(
                    self.model_config.model_name,
                    device_map=self.model_config.device,
                    trust_remote_code=True
                )
            
            logger.info("Base model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            # Fallback to stub implementation
            self.base_model = "stub_model"
            self.tokenizer = "stub_tokenizer"
    
    async def load_adapter(self, adapter_id: str) -> bool:
        """Load a specific LoRA adapter"""
        if adapter_id not in self.adapter_configs:
            logger.error(f"Adapter configuration not found: {adapter_id}")
            return False
        
        config = self.adapter_configs[adapter_id]
        
        if not LORA_AVAILABLE:
            logger.info(f"Stub: Loading adapter {adapter_id} for role {config.role}")
            self.loaded_adapters[adapter_id] = f"stub_adapter_{adapter_id}"
            return True
        
        try:
            if os.path.exists(config.path):
                # Load existing adapter
                adapter_model = PeftModel.from_pretrained(
                    self.base_model, 
                    config.path,
                    adapter_name=adapter_id
                )
                self.loaded_adapters[adapter_id] = adapter_model
                logger.info(f"Loaded existing adapter: {adapter_id}")
            else:
                # Create new adapter with configuration
                peft_config = LoraConfig(
                    r=config.rank,
                    lora_alpha=config.alpha,
                    target_modules=config.target_modules,
                    lora_dropout=0.1,
                    bias="none",
                    task_type="CAUSAL_LM"
                )
                
                adapter_model = get_peft_model(self.base_model, peft_config)
                self.loaded_adapters[adapter_id] = adapter_model
                logger.info(f"Created new adapter: {adapter_id}")
                
                # TODO: Add actual training logic here
                logger.warning(f"Adapter {adapter_id} created but not trained")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load adapter {adapter_id}: {e}")
            return False
    
    async def load_role_adapters(self, role: BoardroomRole) -> Tuple[bool, Dict[str, Any]]:
        """
        Load domain + leadership adapters for a specific boardroom role.
        Always loads exactly one domain adapter + leadership adapter.
        
        Returns:
            Tuple of (success, adapter_info)
        """
        role_str = role.value
        domain_adapter_id = f"domain_{role_str}"
        leadership_adapter_id = "leadership"
        
        adapter_info = {
            "role": role_str,
            "domain_adapter": domain_adapter_id,
            "leadership_adapter": leadership_adapter_id,
            "fusion_weights": {}
        }
        
        # Load domain adapter
        domain_success = await self.load_adapter(domain_adapter_id)
        if not domain_success:
            logger.error(f"Failed to load domain adapter for role {role_str}")
            return False, adapter_info
        
        # Load leadership adapter
        leadership_success = await self.load_adapter(leadership_adapter_id)
        if not leadership_success:
            logger.error(f"Failed to load leadership adapter")
            return False, adapter_info
        
        # Set fusion weights
        domain_config = self.adapter_configs[domain_adapter_id]
        domain_weight = domain_config.fusion_weight
        leadership_weight = 1.0 - domain_weight
        
        adapter_info["fusion_weights"] = {
            "domain": domain_weight,
            "leadership": leadership_weight
        }
        
        logger.info(f"Loaded adapters for {role_str}: domain={domain_weight:.2f}, leadership={leadership_weight:.2f}")
        
        return True, adapter_info
    
    async def generate_response(self, role: BoardroomRole, prompt: str, max_length: int = 512) -> str:
        """
        Generate response using role-specific adapter fusion.
        
        Args:
            role: Boardroom role for adapter selection
            prompt: Input prompt
            max_length: Maximum response length
            
        Returns:
            Generated response text
        """
        # Load adapters for role if not already loaded
        success, adapter_info = await self.load_role_adapters(role)
        if not success:
            return f"Error: Failed to load adapters for role {role.value}"
        
        if not LORA_AVAILABLE:
            return f"[STUB] {role.value.upper()} response to: {prompt[:50]}... (LoRA fusion: domain={adapter_info['fusion_weights']['domain']:.2f}, leadership={adapter_info['fusion_weights']['leadership']:.2f})"
        
        try:
            # Apply domain + leadership adapter fusion
            # TODO: Implement weighted adapter fusion when PEFT supports it
            # For now, use domain adapter as primary
            
            domain_adapter_id = adapter_info["domain_adapter"]
            model = self.loaded_adapters.get(domain_adapter_id, self.base_model)
            
            # Encode prompt
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            
            # Generate with domain adapter
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=max_length,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove original prompt from response
            response = response[len(prompt):].strip()
            
            logger.info(f"Generated response for {role.value} using adapter fusion")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate response for {role.value}: {e}")
            return f"Error generating response: {str(e)}"
    
    async def get_adapter_metrics(self, adapter_id: str) -> Dict[str, Any]:
        """Get performance metrics for a specific adapter"""
        if adapter_id not in self.adapter_configs:
            return {"error": f"Adapter {adapter_id} not found"}
        
        config = self.adapter_configs[adapter_id]
        
        # Return current metrics (would be updated during training/evaluation)
        return {
            "adapter_id": adapter_id,
            "role": config.role,
            "type": config.adapter_type.value,
            "version": config.version,
            "rank": config.rank,
            "alpha": config.alpha,
            "fusion_weight": config.fusion_weight,
            "performance_metrics": config.performance_metrics,
            "status": "loaded" if adapter_id in self.loaded_adapters else "not_loaded"
        }
    
    async def list_all_adapters(self) -> Dict[str, Any]:
        """List all available adapters with their configurations"""
        adapters = {}
        
        for adapter_id, config in self.adapter_configs.items():
            adapters[adapter_id] = await self.get_adapter_metrics(adapter_id)
        
        return {
            "total_adapters": len(adapters),
            "domain_adapters": {k: v for k, v in adapters.items() if "domain_" in k},
            "leadership_adapter": adapters.get("leadership", {}),
            "model_config": {
                "base_model": self.model_config.model_name,
                "quantization": self.model_config.quantization
            }
        }
    
    async def upgrade_to_13b(self, preserve_learning: bool = True) -> Dict[str, Any]:
        """
        Upgrade from 8B to 13B model while preserving learned knowledge.
        
        This is a stub implementation that would integrate with the actual
        model upgrade pipeline described in the specifications.
        
        Args:
            preserve_learning: Whether to preserve self-learning dataset
            
        Returns:
            Upgrade status and information
        """
        logger.info("Starting model upgrade from 8B to 13B...")
        
        upgrade_info = {
            "status": "started",
            "source_model": self.model_config.model_name,
            "target_model": "meta-llama/Llama-3.1-13B-Instruct",
            "preserve_learning": preserve_learning,
            "steps": [
                "Preserve original dataset",
                "Carry forward self-learning dataset", 
                "Generate distillation data from 8B",
                "Retrain domain + leadership LoRAs on 13B",
                "Run parallel evaluation",
                "Migrate self-learning loop to 13B"
            ],
            "estimated_duration": "2-4 hours"
        }
        
        # TODO: Implement actual upgrade logic
        # This would involve:
        # 1. Saving current adapter states and training data
        # 2. Loading 13B model
        # 3. Retraining adapters with blended datasets
        # 4. Running evaluation comparing 8B vs 13B performance
        # 5. Migrating active system to 13B when ready
        
        logger.info("Model upgrade initiated (stub implementation)")
        return upgrade_info
    
    def save_adapter_configs(self):
        """Save current adapter configurations to JSON file"""
        try:
            config_data = {
                "domain_adapters": {},
                "leadership_adapter": {}
            }
            
            for adapter_id, config in self.adapter_configs.items():
                if config.adapter_type == AdapterType.DOMAIN:
                    config_data["domain_adapters"][config.role] = {
                        "rank": config.rank,
                        "alpha": config.alpha,
                        "target_modules": config.target_modules,
                        "layer_range": list(config.layer_range),
                        "fusion_weight": config.fusion_weight,
                        "path": config.path,
                        "version": config.version
                    }
                elif config.adapter_type == AdapterType.LEADERSHIP:
                    config_data["leadership_adapter"] = {
                        "rank": config.rank,
                        "alpha": config.alpha,
                        "target_modules": config.target_modules,
                        "layer_range": list(config.layer_range),
                        "path": config.path,
                        "version": config.version
                    }
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Adapter configurations saved to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save adapter configs: {e}")