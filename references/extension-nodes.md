# Extension Node Format Library

Each node specification includes required fields, optional fields, output fields, and the complete data block format extracted from Dify source code entities (`api/core/workflow/nodes/*/entities.py`) and real 0.6.0 exports.

---

## Container Rules (loop / iteration)

From Dify source code `api/models/workflow.py` and `api/core/workflow/workflow_entry.py`.

### loop

Container node for repeated execution. Each iteration depends on previous results.

**Required data fields:**
| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `type` | string | — | `"loop"` |
| `title` | string | — | Display name |
| `start_node_id` | string | — | Points to `loop-start` child id |
| `loop_count` | integer | — | Max iterations |
| `logical_operator` | string | `"and"` | `"and"` or `"or"` for break_conditions |
| `break_conditions` | array | `[]` | Each: `{id, variable_selector, comparison_operator, value, varType}` |
| `error_handle_mode` | string | `"terminated"` | `"terminated"`, `"continue-on-error"`, `"remove-abnormal-output"` |

**Optional data fields:** `loop_variables`, `desc`, `selected`

**Wrapper:** `type: custom`, `zIndex: 1`

```yaml
data:
  break_conditions: []
  error_handle_mode: terminated
  logical_operator: and
  loop_count: 20
  selected: false
  start_node_id: <loop_start_id>
  title: 循环
  type: loop
```

### loop-start

Internal entry node for loop iteration.

**Required data fields:** `type: "loop-start"`, `title`, `isInLoop: true`

**Wrapper:** `type: custom-loop-start`, `width: 44`, `height: 48`, `draggable: false`, `selectable: false`, `parentId: <loop_id>`, `zIndex: 1002`

```yaml
data:
  desc: ''
  isInLoop: true
  selected: false
  title: ''
  type: loop-start
```

### loop-end

Internal exit node for loop iteration.

**Required data fields:** `type: "loop-end"`, `title`, `isInLoop: true`, `isInIteration: false`, `loop_id`

**Wrapper:** `type: custom-simple`, `width: 243`, `height: 52`, `parentId: <loop_id>`, `zIndex: 1002`. Do NOT add `draggable/selectable`.

```yaml
data:
  isInIteration: false
  isInLoop: true
  loop_id: <loop_id>
  selected: false
  title: 退出循环
  type: loop-end
```

### iteration

Container node for parallel/non-parallel iteration over array items.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"iteration"` |
| `iterator_selector` | array | Source array selector `[node_id, field]` |
| `output_selector` | array | Child output selector `[node_id, field]` |
| `output_type` | string | `"array[string]"`, `"array[number]"`, `"array[object]"` |
| `is_parallel` | boolean | |
| `parallel_nums` | integer | Default 10 |
| `start_node_id` | string | Points to `iteration-start` child |
| `error_handle_mode` | string | |

**Wrapper:** `type: custom`

### iteration-start

Same as loop-start but `type: "iteration-start"`, wrapper `type: custom-iteration-start`.

---

## agent

Autonomous agent with reasoning strategy and tool access. From `api/core/workflow/nodes/agent/entities.py`.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"agent"` |
| `agent_strategy_provider_name` | string | e.g. `"langgenius/agent/agent"` |
| `agent_strategy_name` | string | `"ReAct"` or `"function_calling"` |
| `agent_strategy_label` | string | `"ReAct"` or `"FunctionCalling"` |
| `agent_parameters` | object | `{model, query, instruction, tools}` each as `{type, value}` |
| `plugin_unique_identifier` | string | Versioned plugin id |

**Optional data fields:** `tool_node_version`, `output_schema`, `desc`, `selected`, `memory`, `meta`

**agent_parameters structure:**
```yaml
agent_parameters:
  instruction:
    type: constant
    value: 'You are a helpful assistant.'
  model:
    type: constant
    value:
      completion_params: {}
      mode: chat
      model: gpt-4o
      model_type: llm
      provider: langgenius/openai/openai
      type: model-selector
  query:
    type: constant
    value: '{{#sys.query#}}'
  tools:
    type: constant
    value: []
```

**Output:** `text` (string), `usage` (object), `steps` (array[object])

**Strategies:**
| name | label | provider_name |
|------|-------|--------------|
| `ReAct` | ReAct | `langgenius/agent/agent` |
| `function_calling` | FunctionCalling | `langgenius/agent/agent` |

```yaml
data:
  agent_parameters:
    instruction:
      type: constant
      value: 'You are a helpful assistant.'
    model:
      type: constant
      value:
        completion_params: {}
        mode: chat
        model: gpt-4o
        model_type: llm
        provider: langgenius/openai/openai
        type: model-selector
    query:
      type: constant
      value: '{{#sys.query#}}'
    tools:
      type: constant
      value: []
  agent_strategy_label: ReAct
  agent_strategy_name: ReAct
  agent_strategy_provider_name: langgenius/agent/agent
  desc: ''
  output_schema: null
  plugin_unique_identifier: langgenius/agent:0.0.37@<hash>
  selected: false
  title: Agent
  type: agent
```

---

## assigner (variable-assigner)

Assigns values to conversation variables. Chatflow/advanced-chat only.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"assigner"` |
| `version` | string | `"2"` (strongly recommended) |
| `items` | array | List of assignment operations |

**items[] fields:**
| Field | Type | Notes |
|-------|------|-------|
| `variable_selector` | array | Target `[domain, name]` e.g. `[conversation, phase]` |
| `input_type` | string | `"variable"` or `"constant"` |
| `operation` | string | `over-write`, `clear`, `append`, `extend`, `set`, `+=`, `-=`, `*=`, `/=`, `remove-first`, `remove-last` |
| `value` | mixed | Selector array (variable) or literal (constant) |
| `write_mode` | string | Same as `operation` |

```yaml
data:
  desc: ''
  items:
    - input_type: variable
      operation: over-write
      value:
        - <agent_id>
        - text
      variable_selector:
        - conversation
        - output_var
      write_mode: over-write
    - input_type: constant
      operation: over-write
      value: 'next_phase'
      variable_selector:
        - conversation
        - phase
  selected: false
  title: 变量赋值
  type: assigner
  version: '2'
```

---

## knowledge-retrieval

Queries knowledge bases for RAG. From `api/core/workflow/nodes/knowledge_retrieval/entities.py`.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"knowledge-retrieval"` |
| `dataset_ids` | array | Dataset UUID strings |
| `query_variable_selector` | array | `[node_id, field]` for query text |
| `retrieval_mode` | string | `"multiple"` or `"single"` |

**Mode-dependent fields:**
| Mode | Required | Notes |
|------|----------|-------|
| `multiple` | `multiple_retrieval_config` | `{top_k, score_threshold_enabled, reranking_enable, reranking_mode, reranking_model}` |
| `single` | `single_retrieval_config` | `{model}` |

**Optional fields:** `query_attachment_selector`, `metadata_filtering_mode` (`"disabled"`/`"automatic"`/`"manual"`), `metadata_model_config`, `metadata_filtering_conditions`, `vision`

**Output:** `result` (array[object] with `content`, `score`, `metadata`)

**Export note:** `dataset_ids` are encrypted via AES-CBC during export and decrypted on import. If decryption fails, the ID is filtered out.

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
    - <source_node_id>
    - sys.query
  retrieval_mode: multiple
  selected: false
  title: 知识检索
  type: knowledge-retrieval
```

---

## parameter-extractor

Extracts structured parameters from text via LLM.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"parameter-extractor"` |
| `model` | object | Provider/name/mode/completion_params |
| `query` | array | Variable selector for input text |
| `parameters` | array | Each: `{name, type, description, required}` |
| `reasoning_mode` | string | `"function_call"` or `"prompt"` |

**Parameter types:** `string`, `number`, `boolean`, `array[string]`, `array[number]`, `array[object]`

**Parameter name restrictions:** Cannot be `__reason` or `__is_success`.

**Optional fields:** `instruction`, `memory`, `vision`

**Output:** `{parameter_name}` for each parameter, plus `__reason` and `__is_success`

```yaml
data:
  desc: ''
  instruction: ''
  model:
    completion_params:
      temperature: 0.7
    mode: chat
    name: gpt-4o
    provider: langgenius/openai/openai
  parameters:
    - description: 城市名称
      name: city
      required: true
      type: string
  query:
    - start
    - query
  reasoning_mode: prompt
  selected: false
  title: 参数提取
  type: parameter-extractor
  variables: []
  vision:
    enabled: false
```

---

## question-classifier

LLM-based intent classification with multiple output branches.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"question-classifier"` |
| `model` | object | |
| `query_variable_selector` | array | |
| `classes` | array | Each: `{id, name}` |

**Optional fields:** `instruction`, `memory`, `vision`, `topics`

**Edge routing:** `sourceHandle` uses `classes[*].id` values.

```yaml
data:
  classes:
    - id: '1'
      name: 分类A
    - id: '2'
      name: 分类B
  desc: ''
  instructions: ''
  model:
    completion_params:
      temperature: 0.7
    mode: chat
    name: gpt-4o
    provider: langgenius/openai/openai
  query_variable_selector:
    - start
    - query
  selected: false
  title: 问题分类
  topics: []
  type: question-classifier
  vision:
    enabled: false
```

---

## template-transform

Jinja2 template rendering. Supports filters (`| upper`, `| to_json`), conditionals (`{% if %}`), and loops (`{% for %}`).

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"template-transform"` |
| `template` | string | Jinja2 template with `{{ var }}` references |
| `variables` | array | Each: `{variable, value_selector: [node_id, field]}` |

**Output:** `output` (string)

```yaml
data:
  desc: ''
  selected: false
  template: '{{ arg1 }}的结果是：{{ arg2 }}'
  title: 模板转换
  type: template-transform
  variables:
    - value_selector:
        - <node_id>
        - text
      variable: arg1
```

---

## variable-aggregator

Merges multiple variable sources. Semantics: first non-empty result in order.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"variable-aggregator"` |
| `output_type` | string | `"string"`, `"array[string]"`, `"array[object]"`, etc. |
| `variables` | array | Array of `[node_id, field]` selector arrays |

**Optional:** `advanced_settings` with `group_enabled`, groups with `group_name`, `output_type`, `variables`

**Output:** `output` (type per `output_type`)

```yaml
data:
  desc: ''
  output_type: string
  selected: false
  title: 变量聚合
  type: variable-aggregator
  variables:
    - - <node_id_1>
      - text
    - - <node_id_2>
      - text
```

---

## document-extractor

Extracts text from uploaded documents.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"document-extractor"` |
| `variable_selector` | array | Points to file variable, typically `[start, file]` or `[sys, files]` |

**Output:** `text` (string)

```yaml
data:
  desc: ''
  is_array_file: true
  selected: false
  title: 文档提取
  type: document-extractor
  variable_selector:
    - start
    - file
```

---

## list-operator

Filters, sorts, and limits array data.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"list-operator"` |
| `variable` | array | Source array selector `[node_id, field]` |
| `filter_by` | object | `{enabled, conditions}` |
| `order_by` | object | `{enabled, key, value: asc|desc}` |
| `limit` | object | `{enabled, size}` — size: `-1` for disabled, >=1 for enabled |

**Optional:** `extract_by` with `enabled`, `index`

```yaml
data:
  desc: ''
  extract_by:
    enabled: false
  filter_by:
    conditions: []
    enabled: false
  limit:
    enabled: false
    size: -1
  order_by:
    enabled: false
    key: ''
    value: asc
  selected: false
  title: 列表操作
  type: list-operator
  variable:
    - <source_node_id>
    - result
```

---

## http-request

Makes HTTP API calls.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"http-request"` |
| `method` | string | `"get"`, `"post"`, `"put"`, `"delete"`, `"patch"`, `"head"` |
| `url` | string | Supports `{{#...#}}` references |
| `authorization` | object | `{type: no-auth|api-key, config: {type: bearer|basic|custom, api_key, header}}` |

**Optional fields:** `headers`, `params`, `body` (`{type: none|json|form-data|x-www-form-urlencoded, data}`), `timeout` (`{connect, read, write}`), `retry_config`, `ssl_verify`

**Output:** `body` (string), `status_code` (number), `headers` (object), `files` (array)

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

---

## tool

External tool invocation (builtin, API, MCP, workflow).

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"tool"` |
| `provider_id` | string | e.g. `"author/plugin/provider"` |
| `provider_name` | string | |
| `provider_type` | string | `"builtin"`, `"api"`, `"workflow"`, `"mcp"` |
| `tool_name` | string | Function identifier |
| `tool_label` | string | Display name |
| `tool_parameters` | object | Each param: `{type: mixed|variable|constant, value}` |

**Optional fields:** `plugin_unique_identifier`, `tool_node_version` (recommend `"2"`), `paramSchemas`, `tool_configurations`, `tool_description`, `is_team_authorization`, `output_schema`, `credential_id` — **stripped during export**

**Output:** `text` (string), `files` (array), `json` (object)

**Legacy compatibility:** Old `tool_configurations` entries with `type: "mixed"|"variable"|"constant"` are auto-migrated to `tool_parameters` during import.

```yaml
data:
  desc: ''
  is_team_authorization: true
  output_schema: null
  paramSchemas: []
  params: {}
  provider_id: <provider_id>
  provider_name: <provider_name>
  provider_type: builtin
  selected: false
  title: Tool
  tool_configurations: {}
  tool_label: <Tool Name>
  tool_name: <tool_name>
  tool_parameters: {}
  type: tool
```

---

## code

Python/JavaScript code execution in sandbox. No filesystem, no network, no OS commands.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"code"` |
| `code_language` | string | `"python3"` or `"javascript"` |
| `code` | string | Must define `main()` with params matching variables |
| `outputs` | object | `{output_name: {type, children}}` — maps return keys to types |
| `variables` | array | Input bindings: `{variable, value_selector: [node_id, field]}` |

**Output types:** `string`, `number`, `object`, `array[string]`, `array[number]`, `array[object]`

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
        - <source_node_id>
        - <source_field>
      variable: arg1
```

---

## human-input

Pauses workflow for human interaction.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"human-input"` |
| `delivery_methods` | array | At least one enabled: `{type: webapp|email, enabled, config}` |
| `user_actions` | array | Each: `{id, title}` — used as edge sourceHandle |

**Strongly recommended:** `form_content`, `inputs`, `timeout`, `timeout_unit`

```yaml
data:
  delivery_methods:
    - type: webapp
      enabled: true
      config: {}
  desc: ''
  form_content: ''
  inputs:
    - type: text-input
      output_variable_name: user_input
      required: true
  selected: false
  timeout: 360
  timeout_unit: minute
  title: 人工输入
  type: human-input
  user_actions:
    - id: submit
      title: 提交
```

---

## trigger-schedule

Cron-based scheduled execution entry. Cannot coexist with `start` node.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"trigger-schedule"` |
| `mode` | string | `"visual"` or `"cron"` |

**Mode-dependent:** `"cron"` needs `cron_expression`, `"visual"` needs `frequency` + `visual_config`

**Export sanitization:** `config` reset to defaults during export.

```yaml
data:
  cron_expression: '0 9 * * *'
  desc: ''
  mode: cron
  selected: false
  timezone: Asia/Shanghai
  title: 定时触发
  type: trigger-schedule
```

---

## trigger-webhook

Webhook event-driven entry. Cannot coexist with `start` node.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"trigger-webhook"` |
| `method` | string | `"POST"`, `"GET"` |
| `content_type` | string | e.g. `"application/json"` |

**Export sanitization:** `webhook_url` and `webhook_debug_url` cleared to `""`.

**CRITICAL:** `body` must be an ARRAY `[{name, type, required}]`, NOT an object.

```yaml
data:
  body: []
  content_type: application/json
  desc: ''
  headers: []
  method: post
  params: []
  response_body: ''
  selected: false
  status_code: 200
  title: Webhook
  type: trigger-webhook
```

---

## trigger-plugin

Plugin-specific trigger entry. Cannot coexist with `start` node.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"trigger-plugin"` |
| `plugin_id` | string | |
| `provider_id` | string | |
| `event_name` | string | |
| `subscription_id` | string | Cleared during export |
| `plugin_unique_identifier` | string | |
| `event_parameters` | object | Only supports constant inputs, not variable |

```yaml
data:
  desc: ''
  event_name: on_created
  event_parameters: {}
  plugin_id: plugin_x
  plugin_unique_identifier: provider/plugin:1.0.0
  provider_id: provider_x
  selected: false
  subscription_id: sub_x
  title: Plugin Trigger
  type: trigger-plugin
```

---

## knowledge-index

RAG pipeline terminal node. **Required for `kind: rag_pipeline`** — import fails without it.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"knowledge-index"` |
| `chunk_structure` | string | `"text_model"`, `"hierarchical_model"`, `"qa_model"` |
| `index_chunk_variable_selector` | array | |

```yaml
data:
  chunk_structure: text_model
  desc: ''
  index_chunk_variable_selector:
    - <chunker_tool_id>
    - result
  indexing_technique: economy
  selected: false
  title: 知识索引
  type: knowledge-index
```

---

## datasource

RAG pipeline entry node for document ingestion. Alternative to `start` in RAG pipelines.

**Required data fields:**
| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `"datasource"` |
| `plugin_id` | string | |
| `provider_name` | string | |
| `provider_type` | string | e.g. `"local_file"` |

**Datasource parameter types:** `"mixed"` → string value, `"variable"` → list[str] value, `"constant"` → str|int|float|bool value.

```yaml
data:
  datasource_configurations: {}
  datasource_name: upload-file
  datasource_parameters: {}
  desc: ''
  plugin_id: langgenius/file
  provider_name: file
  provider_type: local_file
  selected: false
  title: Data Source
  type: datasource
```
