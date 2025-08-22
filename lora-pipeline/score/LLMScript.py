import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load your fine‑tuned model
model_name = "path/to/your-finetuned-llama-3.1-8b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def init():
    global tokenizer, model
    # Already loaded above; could load from local path if bundled

def run(raw_data):
    try:
        data = json.loads(raw_data)
        vision = data.get("vision", "")
        decision = data.get("decision", "")

        # Prompt the model to evaluate alignment
        eval_prompt = f"Rate from 0 to 1 how well this decision aligns with the vision.\nVision: {vision}\nDecision: {decision}\nScore:"
        inputs = tokenizer(eval_prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=10)
        raw_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract numeric score from model output
        import re
        match = re.search(r"([0-1](?:\.\d+)?)", raw_text)
        score = float(match.group(1)) if match else None

        return {
            "alignment_score": score,
            "vision": vision,
            "decision": decision
        }
    except Exception as e:
        return {"error": str(e)}