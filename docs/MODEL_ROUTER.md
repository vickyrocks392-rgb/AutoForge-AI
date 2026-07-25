# Model Router

## Purpose

This document defines the model router — the component responsible for selecting and routing tasks to the appropriate LLM (Large Language Model) provider and model. The model router abstracts the complexity of multi-provider, multi-model LLM access behind a unified interface, enabling the platform to use the best model for each task while managing cost, latency, and availability.

## Scope

This document covers model selection strategies, provider abstraction, routing logic, and cost management. It does not cover task execution or agent service implementation — those concerns are addressed in their respective documents.

---

## Overview

The model router is the gateway between the execution engine and LLM providers. It receives a task with its input and requirements, selects the optimal model for that task, sends the request to the appropriate provider, and returns the response. It handles provider-specific authentication, rate limiting, error handling, and cost tracking.

```
                    ┌──────────────┐
                    │  Execution   │
                    │  Engine      │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │    Model     │
                    │   Router     │
                    │              │
            ┌───────┤  ┌────────┐  ├───────┐
            │       │  │ Selector│  │       │
            │       │  └────────┘  │       │
            │       └──────┬───────┘       │
            │              │               │
     ┌──────▼──────┐ ┌─────▼──────┐ ┌──────▼──────┐
     │  Provider   │ │  Provider  │ │  Provider   │
     │  Adapter    │ │  Adapter   │ │  Adapter    │
     │  (OpenAI)   │ │  (Anthropic)│ │  (Local)    │
     └─────────────┘ └────────────┘ └─────────────┘
```

## Model Selection Strategy

The model router selects a model based on the following criteria:

### Task Requirements
- **Complexity** — Simple tasks (formatting, validation) use cheaper, faster models. Complex tasks (architecture design, code generation) use more capable models.
- **Context Window** — Tasks requiring large context (entire codebase analysis) need models with large context windows.
- **Output Format** — Tasks requiring structured output (JSON, code) need models with strong instruction following.
- **Latency Sensitivity** — Interactive tasks need low-latency models. Background tasks can use slower, more capable models.

### Cost Optimization
- **Token Budget** — Each task has a token budget. The router selects a model that can complete the task within budget.
- **Cost Per Token** — The router prefers the cheapest model that meets the task's requirements.
- **Provider Pricing** — The router considers provider-specific pricing and selects the most cost-effective option.

### Availability
- **Provider Health** — The router monitors provider health and avoids degraded or unavailable providers.
- **Rate Limits** — The router respects provider rate limits and queues requests if necessary.
- **Model Deprecation** — The router tracks model deprecation schedules and migrates to newer models automatically.

## Model Tiers

| Tier | Models | Use Case | Relative Cost |
|---|---|---|---|
| **Tier 1 — Fast** | GPT-4o-mini, Claude 3 Haiku, Llama 3 8B | Simple tasks, formatting, validation, classification | Low |
| **Tier 2 — Balanced** | GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro | Code generation, testing, documentation | Medium |
| **Tier 3 — Capable** | GPT-4.5, Claude 3.5 Opus, Gemini 2.0 Ultra | Architecture design, complex reasoning, planning | High |
| **Tier 4 — Specialized** | Code-specific models, fine-tuned models | Domain-specific tasks, custom fine-tuned agents | Variable |

## Provider Abstraction

Each LLM provider is accessed through a provider adapter that implements a common interface:

| Operation | Description |
|---|---|
| `generate()` | Send a prompt and receive a completion |
| `generateStream()` | Send a prompt and receive a streaming completion |
| `embed()` | Generate embeddings for a text input |
| `health()` | Check provider health and availability |
| `cost()` | Calculate cost for a given token count |

### Supported Provider Types

- **Cloud Providers** — OpenAI, Anthropic, Google, AWS Bedrock, Azure OpenAI
- **Local Providers** — Ollama, vLLM, LocalAI, llama.cpp
- **Self-Hosted** — Custom model endpoints, fine-tuned models

## Routing Logic

The routing algorithm operates as follows:

1. **Analyze Task** — Extract task requirements (complexity, context size, output format, latency)
2. **Query Model Registry** — Get list of available models matching task requirements
3. **Score Models** — Score each model on cost, capability, latency, and availability
4. **Select Model** — Choose the highest-scoring model
5. **Check Circuit Breaker** — Verify the selected model's circuit breaker is closed
6. **Dispatch** — Send the request through the appropriate provider adapter
7. **Monitor** — Track response time, token usage, and errors
8. **Fallback** — If the selected model fails, try the next highest-scoring model

## Cost Management

### Token Tracking
Every model request tracks:
- Input tokens
- Output tokens
- Cost per token
- Total cost

### Budget Enforcement
- **Per-Task Budget** — Maximum cost for a single task
- **Per-Project Budget** — Maximum cost for an entire project
- **Per-Time-Period Budget** — Maximum cost per hour/day

When a budget is exceeded, the router:
1. Logs the overage
2. Notifies the execution engine
3. Attempts to use a cheaper model
4. Pauses execution if no cheaper alternative exists

## Model Registry

The model registry maintains a catalog of all available models:

| Field | Description |
|---|---|
| `modelId` | Unique identifier |
| `provider` | Provider name (OpenAI, Anthropic, etc.) |
| `modelName` | Provider-specific model name |
| `tier` | Model tier (1–4) |
| `capabilities` | List of capabilities (code, reasoning, vision, etc.) |
| `contextWindow` | Maximum context window size |
| `costPerInputToken` | Cost per 1K input tokens |
| `costPerOutputToken` | Cost per 1K output tokens |
| `status` | active, degraded, deprecated, retired |
| `latency` | Average response latency |

## Future Implementation Notes

- The model router should support A/B testing of models for the same task type
- Model selection decisions should be logged for analysis and optimization
- The router should support model affinity — preferring models that have been successful for similar tasks
- Provider adapters should be pluggable via a common interface

## Open Questions

- Should the model router support multi-model orchestration — sending the same task to multiple models and selecting the best result?
- How should the router handle model-specific features (vision, tool use, structured output) that may not be available across all providers?
- Should the router support model caching — reusing responses for identical inputs?
- How should the router handle provider-specific content policies and safety filters?
- Should the router support dynamic model discovery — automatically detecting new models from providers?