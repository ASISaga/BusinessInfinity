# Domain-Tuned LLM Blueprint

## Purpose
Provide the agent with domain-specific reasoning, language, and heuristics by fine-tuning on the work and principles of legendary figures in the field.

## Characteristics
- **Stateless:** No internal memory; all context is injected at runtime.
- **Embedded lexicon:** Domain vocabulary and mental models live in the model weights.
- **Legendary heuristics:** Encoded decision patterns from domain greats.
- **Modes:** Convergent (precision) and divergent (exploration) generation.

## Inputs
- **Task prompt:** Natural-language instruction from the agent.
- **Ephemeral context bundle:** Assembled by the agent from organizational data and live signals.
- **Constraints:** Tone, length, compliance rules, output preferences.

## Outputs
- **Content artifacts:** Drafts, outlines, scripts, plans.
- **Critiques:** Remarkability/tone assessments, risk flags, improvement suggestions.
- **Scores:** Alignment with vision, purpose, and legendary lens.

## Invocation Pattern
1. Agent assembles context bundle.
2. Agent sends task prompt + context to LLM.
3. LLM returns task-shaped output with optional rationale.
4. Agent decides persistence horizon (short-term vs long-term).

## Design Principles
- **Alignment-first:** Always reason through vision and purpose.
- **Generosity:** Offer value before asks.
- **Clarity:** Avoid jargon unless audience-specific.
- **Adaptability:** Output format matches task needs.