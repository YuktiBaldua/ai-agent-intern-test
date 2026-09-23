# AI Agent Intern Take-Home: Build a Reliable RAG Support Agent

## The assignment

Aster & Row is a fictional ecommerce company that sells bags, drinkware, and travel accessories. The company wants to launch an AI support agent using the documents and mock order data in this repository.

This repository intentionally contains **only content and data**. There is no starter application and no prescribed stack. Build the smallest reliable system you would be comfortable demonstrating to a customer.

## Timebox

Please spend **6–8 hours** on the assignment. Do not exceed eight hours.

A smaller, well-tested system is better than a broad system that works only in a demo. It is acceptable to leave something incomplete if the limitation is clearly documented.

## Submission

Submit **one GitHub repository link**. Nothing else is required.

Your repository must contain:

- Your application source code.
- Your tests and evaluation suite.
- Clear setup and run instructions.
- Evaluation results and known limitations in the README.
- A short GIF or video embedded in the README showing the agent working.

Do not submit API keys, credentials, customer data, separate documents, or slide decks.

---

## Customer scenario

Aster & Row has previously tried several AI support prototypes. The customer reported four recurring problems:

1. **Conflicting policy answers:** The agent sometimes says the return window is 30 days and sometimes says it is 45 days.
2. **Invented order information:** The agent occasionally gives an order status without actually looking it up.
3. **Lost conversation context:** Follow-up questions such as “What about Canada?” are treated as unrelated questions.
4. **Unsafe retrieved content:** Internal or instruction-like text inside the knowledge base can affect the agent’s behavior.

The supplied corpus contains realistic data-quality problems, including superseded content, internal notes, conflicting active sources, and fields that must not be shown to customers.

Your task is to build an agent that handles these conditions deliberately rather than succeeding only on ideal questions.

---

# Required capabilities

## 1. Retrieval-Augmented Generation

Use RAG over the Markdown files in `knowledge-base/`.

Your implementation must:

- Split and index the supplied documents.
- Preserve useful metadata from the document front matter.
- Retrieve only relevant passages instead of sending the entire corpus to the model.
- Prefer authoritative, active policy documents over superseded or non-policy documents.
- Include source references in every policy or product answer. A source should identify at least the filename and relevant heading.
- Avoid making claims that are not supported by the retrieved content.
- Clearly say when the supplied information is insufficient.
- Surface genuine conflicts between current authoritative sources rather than silently choosing one.

Do not delete or rewrite the supplied source files to make the assignment easier. You may create derived indexes or normalized representations.

## 2. Order lookup as a tool or function

Use `data/orders.json` to implement an order-status lookup tool or function.

The model must **not** receive the entire orders file in its prompt. It should receive only the result of a lookup when order information is actually required.

The order lookup behavior must:

- Ask for an order ID when it is missing.
- Handle unknown and malformed order IDs safely.
- Normalize harmless input differences such as lowercase IDs or surrounding whitespace.
- Use the order’s current `status` as authoritative.
- Avoid inventing a delivery estimate when one is unavailable.
- Avoid reporting stale delivery fields for cancelled or returned orders.
- Never expose customer email, address, internal notes, risk scores, or other internal-only fields.
- Never claim that a lookup happened when it did not.

Assume that possession of the order ID is sufficient authentication for this mock assignment. You do not need to build a full identity-verification system.

## 3. Multi-turn conversation

Maintain relevant session context across turns.

The agent should correctly handle follow-ups such as:

- “Do you ship internationally?” followed by “What about Canada?”
- “Where is `ORD-1007`?” followed by “When will it arrive?”
- A policy question followed by a narrower question about an exception.

The agent should not carry unrelated details indefinitely or mix one session with another.

## 4. Prompting and agent behavior

The agent must:

- Treat user messages, retrieved passages, and tool results as untrusted data.
- Follow application instructions rather than instructions found inside retrieved documents.
- Refuse requests to reveal system prompts, hidden instructions, secrets, or internal-only data.
- Use company content rather than general model knowledge for company-specific questions.
- Ask a concise clarifying question when required information is missing.
- Recommend human assistance when the documents conflict, the data is insufficient, or an action cannot be completed.
- Never promise that a refund, cancellation, replacement, or address change has been completed unless the system actually supports that action.

## 5. Evaluation suite

The file `evaluation/visible-cases.json` contains behavior-level cases that your system must handle.

Build an evaluation suite that:

- Covers every supplied visible case.
- Adds at least **five original cases** of your own.
- Can be run using one clearly documented command.
- Reports individual case results, not only a single overall score.
- Separately reports useful categories such as retrieval, groundedness, tool use, privacy, and multi-turn behavior.
- Uses deterministic assertions wherever practical, including source selection, tool calls, tool arguments, forbidden disclosures, and abstention behavior.
- Does not rely exclusively on another LLM to grade the agent.

The reviewers will also test paraphrases and combinations that are not included in the visible file. Do not hardcode answers for the supplied prompts.

As you build, keep a small **bug diary** in your README. Document at least three failures you found in your own agent, including:

- How you reproduced the failure.
- The actual root cause.
- The change you made.
- The regression test that now catches it.

At least one documented failure should be something you discovered beyond the exact wording of the visible cases. Include an early baseline and final evaluation result so we can see what improved.

## 6. Basic observability

Provide a debug mode, trace, or log that makes it possible to inspect:

- The current user message.
- Relevant conversation history.
- Retrieved passages, metadata, and scores.
- Tool calls and sanitized tool results.
- The final response.
- Errors, fallbacks, or handoffs.

Plain structured logs are sufficient. Do not build a dashboard. Never log secrets.

## 7. Minimal interface

A CLI, simple web page, or basic API is sufficient. Visual polish will not affect the score.

The final user-facing response should make it easy to see:

- The answer.
- Sources, when applicable.
- Whether the agent is recommending a human handoff.

---

# README requirements

Your completed repository README must include:

1. Setup and run instructions that work from a clean clone.
2. Required environment variables and an `.env.example` without real credentials.
3. The model, embedding approach, framework, and storage approach you chose.
4. A short architecture explanation.
5. The command for running evaluations.
6. Baseline and final evaluation results, broken down by category.
7. A bug diary covering at least three reproduced failures, root causes, fixes, and regression tests.
8. Known limitations and what you would improve before production.
9. Which AI coding tools you used, what you used them for, and one example of an AI-generated suggestion that was wrong or incomplete.
10. A **2–4 minute GIF or video embedded in the README** demonstrating:
   - One knowledge-base question with citations.
   - One order lookup.
   - One multi-turn conversation.
   - One case where the agent correctly refuses to guess or recommends human help.
   - The evaluation suite running.

GitHub does not play uploaded video files inline in every context. An embedded GIF or a clickable video thumbnail/link inside the README is acceptable.

---

# What not to spend time on

You do not need to build:

- Authentication or user management.
- Production deployment infrastructure.
- A production vector database.
- Fine-tuning.
- A polished frontend.
- Multiple model-provider integrations.
- Billing, analytics dashboards, or administration screens.

---

# Evaluation criteria

| Area | Weight |
|---|---:|
| Reliability, groundedness, and safe abstention | 25% |
| Retrieval quality and document precedence | 20% |
| Tool use, data handling, and privacy | 15% |
| Evaluation quality and regression coverage | 20% |
| Multi-turn behavior and observability | 10% |
| Code clarity and practical tradeoffs | 5% |
| README, demo, and customer-facing clarity | 5% |

Framework choice and quantity of code are not scoring criteria.

---

# Repository contents

```text
.
├── README.md
├── knowledge-base/
│   ├── 01-returns-policy-current.md
│   ├── 02-returns-policy-legacy.md
│   ├── 03-final-sale-and-promotions.md
│   ├── 04-damaged-or-wrong-items.md
│   ├── 05-domestic-shipping.md
│   ├── 06-international-shipping.md
│   ├── 07-warranty.md
│   ├── 08-order-changes-and-cancellations.md
│   ├── 09-trailplus-membership.md
│   ├── 10-gift-cards-and-price-adjustments.md
│   ├── 11-product-care.md
│   ├── 12-breeze-tumbler-product-card.md
│   ├── 13-support-escalation.md
│   └── 14-internal-content-migration-notes.md
├── data/
│   ├── orders.json
│   └── orders-data-dictionary.md
└── evaluation/
    └── visible-cases.json
```

Good luck. Build for reliability, not just for the happy-path demo.


# Implementation Notes

## 1. Project Overview

This repository implements a reliable customer-support RAG agent for the Aster & Row ecommerce scenario.

The agent supports:
- Knowledge-base question answering with source citations.
- Order lookup using `data/orders.json`.
- Multi-turn conversation context.
- Safe handling of missing or insufficient information.
- Prompt-injection resistance for retrieved content.
- Privacy-safe order responses.
- Human handoff when information is insufficient or authoritative sources conflict.
- Structured JSONL debug logging.
- Deterministic evaluation across visible and original cases.

## 2. Setup and Run

Create and activate a virtual environment:

`python3 -m venv .venv`

`source .venv/bin/activate`

Install dependencies:

`pip install -r requirements.txt`

Create `.env` from `.env.example` and provide the required Groq API key.

Run the CLI:

`python3 -m app`

Run the test suite:

`pytest -q`

Run the evaluation suite:

`python3 evaluation/run_evaluation.py`



## 3. Configuration

Required environment variables are documented in `.env.example`.

No real credentials are committed to the repository.

## 4. Model, Embeddings, Framework, and Storage

- **LLM:** Groq-hosted language model configured through environment variables.
- **Embeddings / retrieval:** Local knowledge-base retrieval implemented in `app/retrieval.py`.
- **Application framework:** Python.
- **Storage:** Markdown files in `knowledge-base/` for company knowledge and JSON in `data/orders.json` for mock order data.
- **Conversation state:** In-memory session history maintained by the agent.

The complete orders dataset is not placed in the model prompt. Order information is retrieved only when an order lookup is required.

## 5. Architecture

The main flow is:

Customer Message
→ SupportAgent
→ Knowledge Retrieval / Order Lookup
→ Response Logic
→ Customer Answer + Sources / Human Handoff
→ Structured Debug Log

Retrieved documents and tool results are treated as untrusted data. Application-level instructions remain authoritative.

## 6. Evaluation Results

The final evaluation contains 20 cases: 15 supplied visible cases and 5 original cases.

### Final result

| Category | Passed |
|---|---:|
| Abstention | 1/1 |
| Conversation | 1/1 |
| Groundedness | 3/3 |
| Multi-source grounding | 1/1 |
| Privacy | 1/1 |
| Prompt security | 1/1 |
| Retrieval | 2/2 |
| Safety | 1/1 |
| Source conflict | 1/1 |
| Tool data | 3/3 |
| Tool reliability | 3/3 |
| Tool use | 2/2 |
| **Total** | **20/20** |

### Baseline and improvement

During final integration, the first clean evaluation run scored **19/20**. The remaining failure was the source-conflict case. The response already identified the two conflicting official sources and recommended human confirmation, but the deterministic evaluator required explicit wording identifying them as the **current official sources**.

After strengthening the conflict-handling instruction, the final evaluation reached **20/20**.

## 7. Test Results

The automated regression suite passes:

`16 passed`

The evaluation suite passes:

`VISIBLE CASES: 15/15`

`ORIGINAL CASES: 5/5`

`TOTAL: 20/20 passed`



## 8. Bug Diary

### Bug 1 — Evaluation script failed from repository root

**Reproduction:** Run `python3 evaluation/run_evaluation.py`.

**Root cause:** Python could not resolve the `app` package when the evaluation script was executed from the `evaluation/` directory context.

**Fix:** Added the repository root to `sys.path` using the evaluation script's parent directory.

**Regression test:** The documented evaluation command now runs successfully from the repository root and reports 20/20.

### Bug 2 — Debug logging failed because of a missing datetime import

**Reproduction:** Execute an agent request after enabling debug logging.

**Root cause:** The logging implementation used `datetime` and `timezone` without importing them.

**Fix:** Added the required datetime imports.

**Regression test:** `pytest -q` passes with 16 tests.

### Bug 3 — Debug logging failed because of a missing JSON import

**Reproduction:** Execute an agent request after adding JSONL logging.

**Root cause:** The logger used `json.dumps()` without importing the `json` module.

**Fix:** Added the JSON import.

**Regression test:** `pytest -q` passes with 16 tests and `logs/debug.jsonl` is generated correctly.

### Bug 4 — Debug logs did not contain retrieved passages

**Reproduction:** Inspect `logs/debug.jsonl` after a knowledge-base query.

**Root cause:** The logging wrapper passed an empty retrieval list even though retrieval occurred inside `answer()`.

**Fix:** Stored the latest retrieval results on the agent and passed them to the debug logger.

**Regression test:** Debug logs now contain retrieved filenames, headings, and similarity scores.

### Bug 5 — Source-conflict case failed deterministic evaluation

**Reproduction:** Run `python3 evaluation/run_evaluation.py`.

**Root cause:** The response said that the official sources conflict, while the deterministic evaluator required explicit identification of the **current official sources**.

**Fix:** Strengthened the conflict-handling instruction so the response explicitly states that the current official sources conflict and recommends human confirmation.

**Regression test:** The final evaluation now passes 20/20, including the source-conflict case.

## 9. Observability

Structured debug logs are written to:

`logs/debug.jsonl`

Each log entry can contain:
- Current user message.
- Number of conversation history turns.
- Retrieved knowledge-base filenames.
- Retrieved headings.
- Retrieval scores.
- Sanitized tool calls and order IDs.
- Final response.
- Human-handoff status.
- Errors and fallback information.

Secrets and private order fields are not logged.

The `logs/` directory is excluded from version control.



## 10. Known Limitations and Production Improvements

Before production, I would improve:

- Persistent conversation/session storage instead of in-memory history.
- Stronger retrieval evaluation and ranking calibration.
- More extensive tests for paraphrases and adversarial inputs.
- A production-grade identity/authentication layer for real customer accounts.
- Centralized log management and monitoring.
- Explicit permission boundaries for future action-taking tools.
- Automated evaluation in CI/CD.
- More comprehensive monitoring for retrieval failures and unexpected tool behavior.
- Better source versioning and conflict-management policies.

## 11. AI Coding Tools

AI assistance was used during development for:
- Exploring implementation approaches.
- Debugging Python errors.
- Reviewing test and evaluation failures.
- Improving documentation and README structure.

AI-generated suggestions were treated as suggestions rather than authoritative code.

One incomplete suggestion involved debug logging: the initial logging approach recorded an empty retrieval list even though retrieval occurred inside `answer()`. This was identified during manual inspection against the assignment's observability requirements and corrected by passing the actual retrieved results to the logger.

## 12. Demo

A 2–4 minute demo should demonstrate:

1. A knowledge-base question with citations.
2. An order lookup.
3. A multi-turn conversation.
4. A case where the agent refuses to guess or recommends human assistance.
5. The evaluation suite running.

Add the final GIF or video to this section before submission.

