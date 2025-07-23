

# LoRA Adapter Training Script
# This script defines a class to automate the process of training LoRA adapters for a language model using HuggingFace Transformers and PEFT.
# Steps:
#   1. Load base model and tokenizer
#   2. Define and attach multiple LoRA adapters
#   3. Prepare the training dataset
#   4. Set up training arguments
#   5. Train the model and save adapters

import os
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import get_peft_config, get_peft_model, LoraConfig, TaskType
from datasets import load_dataset

from LoRATrainer import LoRATrainer

if __name__ == "__main__":
    # Example usage: initialize and run the LoRA trainer
    trainer = LoRATrainer(
        model_name="meta-llama/Llama-3.1-8B-Instruct",
        data_path="path/to/your/jsonl",
        output_dir="outputs/"
    )
    trainer.train()