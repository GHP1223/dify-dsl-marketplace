---
name: dify-dsl-gen
description: Use when the user wants to generate, create, or build a Dify workflow, chatflow, chatbot, agent, or text-generation application DSL YAML file. Also use when modifying an existing Dify DSL YAML. Covers all 26 node types with formats extracted from real Dify 0.6.0 exports.
---

# Dify DSL Generator

Generate import-ready Dify DSL YAML through guided dialogue. All field names, ordering, and nesting are from real Dify 0.6.0 export files — never invent fields from memory.

## Critical Rules (NON-NEGOTIABLE)

These rules come from Dify source code and real import testing. **Violating any of them causes import failure or 500 errors.**

| # | Rule | If violated |
|---|------|-------------|
| 1 | `version: "0.6.0"` MUST be a quoted string | Import **FAILS** with version type error |
| 2 | `conversation_variables[].id` MUST be a valid UUID | **500** — database rejects non-UUID |
| 3 | Every edge MUST have `isInIteration: false` AND `isInLoop: false/true` in `data` | Workflow can't resolve container membership |
| 4 | Loop edges (`isInLoop: true`) MUST have `loop_id` matching loop container `id` | Graph validation fails |
| 5 | Loop internal nodes MUST have `parentId` pointing to loop container `id` | Container membership broken |
| 6 | `loop-start` wrapper: `type: custom-loop-start`, `draggable: false`, `selectable: false`, `width: 44`, `height: 48` | Canvas rendering broken |
| 7 | `loop-end` wrapper: `type: custom-simple`, `width: 243`, `height: 52`, no `draggable/selectable` | Canvas rendering broken |
| 8 | Edge ID format: `{source}-{sourceHandle}-{target}-target` | Canvas display issues |
| 9 | `start` and `trigger-*` nodes CANNOT coexist | Dify throws ValueError |
| 10 | `break_conditions` items need `id` field (UUID) | Potential runtime errors |
| 11 | LLM `completion_params` should only contain `temperature` | Extra params may cause issues |
| 12 | LLM `context.variable_selector` must be present (can be `[]`) | Field missing errors |

## When to Use

- User asks to create/build/generate a Dify workflow/chatflow/agent/chatbot
- User provides requirements for a Dify application
- User wants to modify an existing DSL YAML file

## When NOT to Use

- Reviewing or validating existing DSL (separate concern)
- Building Dify plugins (not DSL generation)
- RAG pipeline DSL (not yet supported)

## Confirmation Flow

Work through these steps with the user. Do NOT output YAML until all steps are confirmed.

### Step 1: Determine Mode

Ask the user which mode, or infer from their description. Present the inferred mode and wait for confirmation.

| Mode | `mode` value | Entry | Exit | When to use |
|------|-------------|-------|------|-------------|
| Workflow | `workflow` | `start` | `end` | Structured multi-step process, API/batch |
| Chatflow | `advanced-chat` | `start` | `answer` | Conversational, multi-turn dialogue |
| Chatbot | `agent-chat` | N/A | N/A | Simple single-model chatbot |
| Agent | `workflow` + `agent` node | `start` | `end`/`answer` | Autonomous agent with tools |
| Text generation | `workflow` or `advanced-chat` | `start` | `end`/`answer` | One-shot text generation |

### Step 2: Design Node List + Connections

Based on the user's requirements, propose:

1. A list of nodes (type + title + purpose)
2. The connections between them (source → target)

Present as:

```
Nodes:
  1. start — 用户输入
  2. llm — LLM推理
  3. answer — 回复

Connections:
  start → llm
  llm → answer
```

Ask: "Does this look right?" Wait for confirmation before proceeding.

### Step 3: Confirm Per-Node Details

For each node, ask about the details that affect the DSL:

**start:** Input variables (name, type, required, label). File upload config if needed.

**llm:** Model provider and name (e.g. `langgenius/openai/openai` / `gpt-4o`). System prompt content. Context from knowledge retrieval? (which node?). Temperature.

**answer:** Which upstream node's output to display? (usually `{{#llm.text#}}`)

**end:** Which upstream fields to expose as workflow outputs?

**code:** Input variables from upstream. Output variable names and types. Code logic (will be written as Python).

**http-request:** URL, method (get/post). Authorization type. Headers, body, params.

**tool:** Tool/plugin provider_id and tool_name. Parameter mappings from upstream nodes.

**agent:** Strategy (ReAct/FunctionCalling). Model. Tools list. Instruction text.

**if-else:** Number of branches. Condition logic per branch (variable to check, comparison operator, value).

**knowledge-retrieval:** Which dataset_ids to search. Which upstream text variable is the query. Reranking model.

**question-classifier:** Class names (categories). Query source.

**parameter-extractor:** Parameters to extract (name, type, description, required). Query source.

**iteration / loop:** Array source to iterate over. What to do inside the loop. Output type.

Ask one node at a time. Use option-style questions when possible.

### Step 4: Output DSL YAML

When ALL nodes are confirmed, output ONLY the DSL YAML content.

**CRITICAL OUTPUT RULES:**
- Output ONLY the YAML. No markdown fences, no introductory text, no "here is your DSL".
- Use exactly 2-space indentation.
- Use `version: 0.6.0`.
- Every node `data:` block includes `desc: ''` and `selected: false`.
- Every `prompt_template` entry has a UUID `id:` field.
- Node IDs use descriptive English strings (e.g. `llm`, `answer`, `code_1`) or timestamp numbers.
- Provider strings use fully-qualified format: `langgenius/openai/openai`.

## Incremental Modification

When the user provides an existing DSL YAML and asks to modify it:

1. Parse the existing YAML to identify all nodes, edges, UUIDs, and structure
2. Ask the user what specifically to change (add/remove nodes, change prompts, switch models, etc.)
3. Make ONLY the specified changes
4. Preserve ALL existing UUIDs, node IDs, edge IDs, position values untouched
5. Output the complete modified YAML following the same output rules as Step 4

## Node Format Library — Common Types (8)

Each node's `data:` block is extracted from real Dify 0.6.0 export files. When generating DSL, copy the field names, ordering, and structure exactly.

### start

```yaml
data:
  desc: ''
  selected: false
  title: 开始
  type: start
  variables: []
```

With input variables:
```yaml
  variables:
    - label: Query
      max_length: 48
      options: []
      required: true
      type: text-input
      variable: query
```

Variable types: `text-input`, `paragraph`, `select`, `number`, `file`, `file-list`

For file input:
```yaml
    - allowed_file_extensions: []
      allowed_file_types:
        - image
      allowed_file_upload_methods:
        - local_file
        - remote_url
      label: File
      max_length: 48
      options: []
      required: true
      type: file
      variable: my_file
```

### llm

```yaml
data:
  context:
    enabled: false
    variable_selector: []
  desc: ''
  memory:
    query_prompt_template: '{{#sys.query#}}'
    role_prefix:
      assistant: ''
      user: ''
    window:
      enabled: false
      size: 10
  model:
    completion_params:
      temperature: 0.7
    mode: chat
    name: gpt-4o
    provider: langgenius/openai/openai
  prompt_template:
    - id: <uuid>
      role: system
      text: 'You are a helpful assistant.'
  selected: false
  title: LLM
  type: llm
  vision:
    enabled: false
```

Output: `{{#llm_id.text#}}`

### answer

```yaml
data:
  answer: '{{#llm.text#}}'
  desc: ''
  selected: false
  title: 回复
  type: answer
  variables: []
```

### end

```yaml
data:
  desc: ''
  outputs:
    - value_selector:
        - llm
        - text
      variable: result
  selected: false
  title: 结束
  type: end
```

Only in `workflow` mode. Each output has `variable` (external name) and `value_selector` (internal source `[node_id, field]`).

### code

```yaml
data:
  code: |
    def main(arg1: str) -> dict:
        return {"result": arg1.upper()}
  code_language: python3
  desc: ''
  outputs:
    result:
      children: null
      type: string
  selected: false
  title: Code
  type: code
  variables:
    - value_selector:
        - start
        - query
      variable: arg1
```

Output types: `string`, `number`, `array[string]`, `array[object]`. `code_language`: `python3` or `javascript`.

### http-request

```yaml
data:
  authorization:
    type: no-auth
  body:
    type: none
  desc: ''
  headers: ''
  method: post
  params: ''
  retry_config:
    max_retries: 3
    retry_enabled: false
    retry_interval: 100
  selected: false
  timeout:
    connect: 10
    max_connect_timeout: 0
    max_read_timeout: 0
    max_write_timeout: 0
    read: 60
    write: 60
  title: HTTP
  type: http-request
  url: ''
```

Authorization — `api-key`:
```yaml
  authorization:
    config:
      api_key: ''
      header: Authorization
      type: bearer
    type: api-key
```

Body types: `none`, `json`, `form-data`, `x-www-form-urlencoded`.

### tool

```yaml
data:
  desc: ''
  is_team_authorization: true
  output_schema: null
  paramSchemas: []
  params: {}
  provider_id: ''
  provider_name: ''
  provider_type: builtin
  selected: false
  title: Tool
  tool_configurations: {}
  tool_description: ''
  tool_label: ''
  tool_name: ''
  tool_parameters: {}
  type: tool
```

`tool_parameters` format:
```yaml
  tool_parameters:
    <param_name>:
      type: mixed           # mixed (template), variable (selector), constant (literal)
      value: '{{#source_node.field#}}'
```

### if-else

```yaml
data:
  cases:
    - case_id: 'true'
      conditions:
        - comparison_operator: contains
          id: <uuid>
          value: 'keyword'
          varType: string
          variable_selector:
            - llm
            - text
      id: 'true'
      logical_operator: and
  desc: ''
  selected: false
  title: 条件分支
  type: if-else
```

Multiple branches:
```yaml
  cases:
    - case_id: 'true'
      conditions:
        - comparison_operator: '='
          id: <uuid>
          value: '1'
          varType: number
          variable_selector: [start, option]
      id: 'true'
      logical_operator: and
    - case_id: <uuid_2>
      conditions:
        - comparison_operator: '='
          id: <uuid>
          value: '2'
          varType: number
          variable_selector: [start, option]
      id: <uuid_2>
      logical_operator: and
```

Comparison operators: `contains`, `not contains`, `start with`, `end with`, `is`, `not empty`, `empty`, `=`, `>`, `<`, `>=`, `<=`, `in`, `not in`.

Edge `sourceHandle` matches `case_id`: `'true'`, `'false'` (else), or custom `<uuid>`.

### knowledge-retrieval

```yaml
data:
  dataset_ids:
    - <dataset_uuid>
  desc: ''
  multiple_retrieval_config:
    reranking_enable: true
    reranking_mode: reranking_model
    reranking_model:
      model: bge-reranker-v2-m3
      provider: langgenius/siliconflow/siliconflow
    top_k: 4
  query_variable_selector:
    - start
    - query
  retrieval_mode: multiple
  selected: false
  title: 知识检索
  type: knowledge-retrieval
```

Output: `{{#kr_id.result#}}`. `retrieval_mode`: `multiple` or `single`.

## Assembly Rules

### Mode Shells

**workflow mode:**
```yaml
app:
  description: ''
  icon: 🤖
  icon_background: '#FFEAD5'
  mode: workflow
  name: <app_name>
  use_icon_as_answer_icon: false
kind: app
version: 0.6.0
workflow:
  conversation_variables: []
  environment_variables: []
  features:
    file_upload:
      allowed_file_extensions: []
      allowed_file_types: []
      allowed_file_upload_methods: []
      enabled: false
      fileUploadConfig:
        audio_file_size_limit: 50
        batch_count_limit: 5
        file_size_limit: 15
        image_file_size_limit: 10
        video_file_size_limit: 100
        workflow_file_upload_limit: 10
      image:
        enabled: false
        number_limits: 3
        transfer_methods: []
      number_limits: 3
    opening_statement: ''
    retriever_resource:
      enabled: true
    sensitive_word_avoidance:
      enabled: false
    speech_to_text:
      enabled: false
    suggested_questions: []
    suggested_questions_after_answer:
      enabled: false
    text_to_speech:
      enabled: false
      language: ''
      voice: ''
  graph:
    edges: []
    nodes: []
    viewport:
      x: 0
      y: 0
      zoom: 1
```

**advanced-chat mode:** Same shell but `mode: advanced-chat`. Exit with `answer`, not `end`.

**agent-chat mode:**
```yaml
app:
  description: ''
  icon: 🤖
  icon_background: '#FFEAD5'
  mode: agent-chat
  name: <app_name>
  use_icon_as_answer_icon: false
kind: app
version: 0.6.0
model_config:
  agent_mode:
    enabled: true
    max_iteration: 5
    strategy: function_call
    tools: []
  model:
    completion_params: {}
    mode: chat
    name: gpt-4o
    provider: langgenius/openai/openai
  prompt_type: simple
  pre_prompt: ''
  sensitive_word_avoidance:
    enabled: false
```

### Node Wrapper

Every node in `graph.nodes[]`:
```yaml
- data:
    # ... node-specific data block
  height: <number>
  id: '<node_id>'
  position:
    x: <number>
    y: <number>
  positionAbsolute:
    x: <number>
    y: <number>
  selected: false
  sourcePosition: right
  targetPosition: left
  type: custom
  width: 244
```

Default positions: start at x=80, y=282. Each subsequent node: x += 350.
Default heights: start=88, llm=96, answer=103, end=88, code=88, http-request=106, tool=52, if-else=124, knowledge-retrieval=90.

### Edge Structure

**CRITICAL: Every edge must have BOTH `isInIteration` AND `isInLoop` in its `data` dict.** This is how Dify source code determines container membership.

**Outer edges** (outside any container):
```yaml
- data:
    isInIteration: false       # REQUIRED
    isInLoop: false            # REQUIRED
    sourceType: <source_node_type>
    targetType: <target_node_type>
  id: <source>-<sourceHandle>-<target>-target
  selected: false
  source: '<source_node_id>'
  sourceHandle: source
  target: '<target_node_id>'
  targetHandle: target
  type: custom
  zIndex: 0
```

**Loop container edges** (inside `loop` node):
```yaml
- data:
    isInIteration: false       # REQUIRED
    isInLoop: true             # REQUIRED
    loop_id: '<loop_container_id>'  # REQUIRED when isInLoop=true
    sourceType: <source_node_type>
    targetType: <target_node_type>
  id: <source>-<sourceHandle>-<target>-target
  selected: false
  source: '<source_node_id>'
  sourceHandle: source
  target: '<target_node_id>'
  targetHandle: target
  type: custom
  zIndex: 1002
```

Source handles:
- Normal flow: `sourceHandle: source`
- if-else true: `sourceHandle: 'true'`, false/else: `sourceHandle: 'false'`, custom: `sourceHandle: '<case_uuid>'`
- question-classifier: `sourceHandle: '<class_id>'`
- human-input: `sourceHandle: '<action_id>'`

### Variable References

| Context | Syntax | Example |
|---------|--------|---------|
| Node output (template) | `{{#node_id.field#}}` | `{{#llm.text#}}` |
| Selector array | `[node_id, field_name]` | `[llm, text]` |
| System query | `{{#sys.query#}}` | — |
| System files | `{{#sys.files#}}` | — |
| Environment var | `{{#env.VAR_NAME#}}` | `{{#env.API_KEY#}}` |
| Conversation var | `{{#conversation.var#}}` | `{{#conversation.count#}}` |
| Knowledge context | `{{#context#}}` | — |
| Aggregator output | `{{#agg_id.output#}}` | — |
| Parameter extractor | `{{#pe_id.param_name#}}` | `{{#pe_1.city#}}` |
| Knowledge retrieval | `{{#kr_id.result#}}` | — |
| Template transform | `{{#template_id.output#}}` | — |
| Document extractor | `{{#doc_id.text#}}` | — |
| Tool output | `{{#tool_id.text#}}` / `{{#tool_id.files#}}` | — |
| HTTP response | `{{#http_id.body#}}` / `{{#http_id.status_code#}}` | — |
| Iteration item | `{{#iter_start_id.item#}}` | — |

### Provider Strings

Always use fully-qualified format:
- `langgenius/openai/openai`
- `langgenius/siliconflow/siliconflow`
- `langgenius/google/google`
- `langgenius/anthropic/anthropic`
- `langgenius/azure_openai/azure_openai`

## Verification

### Automated Lint

After writing DSL to a `.yml` file, run the linter:

```bash
python scripts/lint_dsl.py <output.yml>
```

Or for JSON: `python scripts/lint_dsl.py <output.yml> --json`

The linter validates 16 node types: field completeness, selector validity, edge connectivity, mode requirements, duplicate IDs, and known format pitfalls. Source: [scripts/lint_dsl.py](scripts/lint_dsl.py).

### Manual Checklist

Also mentally verify:

1. `version: 0.6.0` at top level
2. All node IDs are unique
3. All `{{#id.field#}}` references match actual node IDs
4. All `[node_id, field]` selectors reference existing nodes
5. Every edge has valid `source` and `target` IDs
6. if-else `sourceHandle` matches `case_id` values
7. `prompt_template` entries all have `id: <uuid>`
8. Every node `data:` has `desc: ''` and `selected: false`
9. Indentation is consistently 2 spaces
10. `body:` in trigger-webhook is a list, not a map
11. `limit.size` is never 0 (use -1 for disabled)

### Common Errors and Fixes

| Error | Fix |
|-------|-----|
| "Invalid YAML" | Check 2-space indentation |
| "Field not recognized" | Copy exact field names from format library |
| "Node type not found" | Use exact strings like `if-else` not `if_else` |
| "Variable not found" | Check `{{#id#}}` matches a real node `id:` |
| "Version mismatch" | Use `version: 0.6.0` |
| trigger-webhook body error | `body:` must be list `- name: ...` not `key: value` map |
| list-operator limit error | `limit.size: -1` for disabled, positive int for enabled |

## References

| File | Purpose |
|------|---------|
| [references/extension-nodes.md](references/extension-nodes.md) | All 18 extended node types with required/optional/output fields from Dify source code entities |
| [references/import-rules.md](references/import-rules.md) | Import validation, export sanitization, version compatibility, container rules, graph constraints |
| [references/field-dict.md](references/field-dict.md) | Enum values, provider strings, model names, type lists |
| [references/templates.md](references/templates.md) | 3 complete import-ready DSL templates (minimal chatflow, loop orchestration, trigger workflow) |
| [scripts/lint_dsl.py](scripts/lint_dsl.py) | Automated DSL validator for 16 node types |
