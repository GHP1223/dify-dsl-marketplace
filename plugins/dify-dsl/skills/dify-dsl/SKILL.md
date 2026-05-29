---
name: dify-dsl
description: Design, generate, review, refactor, and validate Dify Workflow, Chatflow, and RAG Pipeline DSL. Use when user mentions Dify DSL, Dify workflow, Chatflow, RAG pipeline, Dify YAML, or any task involving creating/modifying/reviewing Dify application configurations.
---

# Dify DSL Skill

Design, generate, review, refactor, and validate Dify Workflow, Chatflow, and RAG Pipeline DSL.

This is a unified skill pack converted from the original 12-skill Dify DSL architecture. All downstream workflows are organized as reference docs in [references/](references/).

## Step 1: Intent Recognition & Routing

Before doing any DSL work, classify the user's intent:

| Intent | Condition | Workflow |
|--------|-----------|----------|
| Brainstorm | Requirements still unclear, unknowns exist | [Brainstorming Workflow](#brainstorming) |
| Author | Create new DSL from clear requirements | [Authoring Workflow](#authoring) |
| Review | Read-only analysis of existing DSL | [Review Workflow](#review) |
| Refactor | Fix, optimize, or restructure existing DSL | [Refactor Workflow](#refactor) |
| Template | Only choose a template/skeleton | [Template Selection](#template-selection) |
| Governance | Delivery/release judgment | [Governance](#governance) |
| Subagent Review | Multi-party independent review needed | [Subagent Review](#subagent-review) |
| Validate | Test the skill itself with fixtures | [Forward Testing](#forward-testing) |

If the task is NOT related to Dify DSL (workflow, advanced-chat, rag_pipeline), do NOT use this skill.

## Step 2: Load Foundations First

For ALL DSL tasks, read the shared foundation knowledge before proceeding:

1. [Foundations Index](references/dify-dsl-foundations---index.md) — start here
2. [Common DSL Structure](references/dify-dsl-foundations---common-dsl.md)
3. [Task Routing](references/dify-dsl-foundations---task-routing.md)
4. [Orchestration Modes](references/dify-dsl-foundations---orchestration-modes.md)
5. [Selector Templates](references/dify-dsl-foundations---selector-templates.md)
6. [Output Contract](references/dify-dsl-foundations---output-contract.md)
7. [Validation Contract](references/dify-dsl-foundations---validation-contract.md)

## Step 3: Execute the Targeted Workflow

### Brainstorming

When requirements are still fuzzy. Do NOT generate or modify DSL until all **blocking unknowns** are cleared.

- Read: [Brainstorming Design Doc Template](references/dify-dsl-brainstorming---design-doc-template.md)
- Read: [Spec Review Checklist](references/dify-dsl-brainstorming---spec-review-checklist.md)
- Maintain an "unknowns ledger" — classify each as **blocking** or **non-blocking**
- Ask one question at a time, prefer option-style questions
- Present 2-3 candidate solutions with trade-offs
- Only route forward when blocking unknowns are zero

**Blocking unknowns** (must clear before proceeding):
- Is this new DSL, read-only review, or refactor?
- Target mode: `workflow`, `advanced-chat`, or `rag_pipeline`?
- For refactor: is file modification allowed?
- For new: output draft only, or write to disk?
- Success criteria defined?

### Authoring

When requirements are clear and the goal is to produce a DSL draft.

1. Load foundations (Step 2)
2. [Node Knowledge](references/dify-dsl-nodes---index.md) — select and configure nodes
3. [Template Library](references/dify-dsl-templates---index.md) — optional template starting point
4. Build: nodes list → edges list → field checklist → DSL draft

**Minimum output:**
1. Mode judgment (workflow / advanced-chat / rag_pipeline)
2. Template choice (if applicable) with rationale
3. Node list with types
4. Edge list with connections
5. Field checklist
6. Complete DSL draft (YAML)
7. Remaining items to confirm
8. Whether subagent review is recommended

### Review

Read-only analysis of existing DSL. Do NOT modify files.

1. Load foundations (Step 2)
2. [Node Knowledge](references/dify-dsl-nodes---index.md) — analyze node correctness
3. [Quality: Review Checklist](references/dify-dsl-quality---review-checklist.md)
4. [Quality: Graded Review Model](references/dify-dsl-quality---graded-review-model.md)
5. Run deterministic lint: `python3 scripts/lint_dsl.py <file.yml>`
6. If multi-party review needed → [Subagent Review](#subagent-review)

**Minimum output:**
1. Mode judgment
2. Node list
3. Edge list
4. Field checklist
5. Risk grading
6. Final conclusion (import-ready / needs fixes / not deliverable)

### Refactor

Fix, optimize, or restructure existing DSL.

1. Load foundations (Step 2)
2. [Quality: Fix Strategies](references/dify-dsl-quality---fix-strategies.md)
3. [Quality: Anti-patterns](references/dify-dsl-quality---anti-patterns.md)
4. [Quality: Optimization Playbook](references/dify-dsl-quality---optimization-playbook.md)
5. [Node Knowledge](references/dify-dsl-nodes---index.md) — node-level fixes
6. Run lint first: `python3 scripts/lint_dsl.py <file.yml>`

**Minimum output:**
1. Problem attribution
2. Fix/refactor plan (prefer minimal fix over full rewrite)
3. Change impact summary
4. Modified DSL
5. Remaining risks

### Template Selection

When the user only wants to pick a template/skeleton.

1. [Templates Index](references/dify-dsl-templates---index.md)
2. [Templates Library](references/dify-dsl-templates---templates-library.md)
3. [Template Validation Status](references/dify-dsl-templates---template-validation-status.md)
4. [Template Variants](references/dify-dsl-templates---template-variants.md)

### Governance

Delivery/release judgment — "can this be shipped?"

1. [Governance Index](references/dify-dsl-governance---index.md)
2. [Evaluation Gates](references/dify-dsl-governance---evaluation-gates.md)
3. [Change Impact Review](references/dify-dsl-governance---change-impact-review.md)
4. [Coverage Matrix](references/dify-dsl-governance---coverage-matrix.md)
5. [Observability Contract](references/dify-dsl-governance---observability-contract.md)

### Subagent Review

Multi-party independent review orchestration.

1. [Subagent Review Index](references/dify-dsl-subagent-review---index.md)
2. [Mode Selection Matrix](references/dify-dsl-subagent-review---mode-selection-matrix.md)
3. [Orchestration Playbook](references/dify-dsl-subagent-review---orchestration-playbook.md)
4. [Quality: Subagent Review](references/dify-dsl-quality---subagent-review.md)

**Four review modes:**
- **Async Parallel** (default): 3 independent reviewers in parallel
- **Sync Serial**: sequential review, each builds on previous
- **Single Subagent**: narrow risk scope, small sample
- **No Subagent**: platform limitation fallback (must mark "not independently reviewed")

### Forward Testing

Validate the skill itself using real fixtures and replay testing.

- Scripts: see [scripts/](scripts/) directory
- Key commands:
  - `python3 scripts/lint_dsl.py <file.yml>` — deterministic DSL lint
  - `python3 scripts/fast_test_dsl.py <file.yml>` — quick DSL analysis
  - `python3 scripts/run_validation_suite.py` — full validation suite
- Playbook: [Forward Test Playbook](references/dify-dsl-forward-testing---forward-test-playbook.md)

## Constraints

- Do NOT generate DSL when requirements are still unclear → use brainstorming
- Do NOT modify files during a read-only review
- Do NOT upgrade a "minimal fix" to a full rewrite without explicit authorization
- Do NOT claim "ready to import" or "fully verified" — route to review/governance for those conclusions
- Do NOT leak `oracle.json` expected answers to test threads
- Always run `lint_dsl.py` before claiming quality checks are done
- Prefer minimal sufficient solutions over "doing more"

## Reference Architecture

```
references/
├── dify-dsl-foundations---*.md     # Shared base: modes, selectors, contracts
├── dify-dsl-nodes---*.md           # 21 node type docs
├── dify-dsl-templates---*.md       # Template library & variants
├── dify-dsl-quality---*.md         # Review rules, anti-patterns, fix strategies
├── dify-dsl-governance---*.md      # Delivery gates, coverage, observability
├── dify-dsl-subagent-review---*.md # Multi-review orchestration
├── dify-dsl-forward-testing---*.md # Skill validation playbook
└── dify-dsl-brainstorming---*.md   # Design doc templates, checklists
```

## Scripts

| Script | Purpose |
|--------|---------|
| `lint_dsl.py` | Deterministic DSL validation (50+ error codes) |
| `fast_test_dsl.py` | Quick DSL structure analysis |
| `fast_test_suite.py` | Batch DSL analysis |
| `run_validation_suite.py` | Full forward testing suite |
| `compare_validation_reports.py` | Compare two validation reports |
| `check_forward_test_cases.py` | Validate test case structure |
| `check_replay_outputs.py` | Validate replay outputs vs expectations |

## Fixtures

Sample DSL files in `fixtures/` cover:
- Minimal examples: `min-workflow.yml`, `min-advanced-chat.yml`, `min-rag-pipeline.yml`
- Working patterns: agent tools, branching, iteration, loops, knowledge retrieval
- Broken samples: invalid selectors, missing fields, duplicate configs
- Real examples: GHP remote sensing multi-agent system (`ghp_*.yml`)
