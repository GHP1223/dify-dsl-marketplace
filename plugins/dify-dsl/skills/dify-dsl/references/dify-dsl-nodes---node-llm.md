# llm 节点

## 作用

调用模型生成文本或结构化输出。

## 必填字段

- `type: llm`: 指定当前节点是模型调用节点。
- `model`: 指定要调用的模型与参数。
  - `provider`: 模型供应方标识。支持简单格式 `openai`、`siliconflow`，或全限定格式 `langgenius/siliconflow/siliconflow`。
  - `name`: 具体模型名，如 `gpt-4o-mini`、`deepseek-ai/DeepSeek-V3`。
  - `mode`: 固定 `chat`。
  - `completion_params`: 至少包含 `temperature: 0.7`。可选加 `max_tokens`、`frequency_penalty`、`stop: []`。
- `prompt_template`: 定义提示词结构。数组中每项含 `id`(uuid)、`role`(system/user)、`text`(模板文本)。
- `context`: 上下文控制。
  - `enabled`: `true`/`false`
  - `variable_selector`: 当 `enabled: true` 时必填，指向知识检索节点输出 `[knowledge_node_id, result]`

## 选填字段

- `memory`: chatflow 记忆窗口配置。含 `query_prompt_template`、`role_prefix`(user/assistant)、`window`(enabled/size)。
- `vision`: 多模态视觉配置。含 `enabled`、`configs`(detail/variable_selector)。
- `variables`: 输入变量映射数组，通常为 `[]`。
- `desc`: 节点描述，默认 `''`。
- `structured_output`: 需要模型按固定 schema 产出时填写。
- `structured_output_enabled`: 需要打开结构化输出开关时填写。

## 贯通性分析

- 上游通常接 `start` 输入、检索结果、模板转换结果、对话变量。
- 下游常接 `answer`、`end`、`if-else`、`assigner`、`template-transform`。
- 关键是 prompt 依赖变量是否齐全，以及下游消费的是 `text` 还是结构化输出。

## 可承接上游节点

### 推荐

- `start`
- `knowledge-retrieval`
- `template-transform`
- `assigner`

### 可用但需人工确认

- `code`
- `tool`
- `variable-aggregator`
- `question-classifier`
- 其他能提供文本、上下文或结构化提示词输入的节点

### 不推荐

- `end`
- `answer`
- `knowledge-index`

## 可衔接下游节点

### 推荐

- `answer`
- `end`
- `if-else`
- `assigner`
- `template-transform`

### 可用但需人工确认

- `code`
- `tool`
- `question-classifier`
- `human-input`
- `variable-aggregator`

### 不推荐

- `start`
- 任意 `trigger-*`
- `datasource`

## 编排约束

- `prompt_template` 在生产 DSL 中通常建议非空，但不要把“不能为空列表”当成源码硬约束。
- `mode` 要与模型能力匹配，常见是 `chat`。
- 若启用结构化输出，报告里要写清 schema 来源。

## 节点完整结构

```yaml
- data:
    context:
      enabled: false                    # 启用知识上下文时设为 true
      variable_selector: []             # enabled=true 时: [knowledge_node_id, result]
    desc: ''
    memory:                             # chatflow 记忆（选填）
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
        max_tokens: 4096                # 可选
        frequency_penalty: 0            # 可选
        stop: []                        # 可选
      mode: chat
      name: gpt-4o-mini
      provider: openai
    prompt_template:
      - id: <uuid>                      # 每项必须有唯一 id
        role: system
        text: '你是助手。'
      - id: <uuid>
        role: user
        text: '{{#sys.query#}}'
    selected: false
    title: LLM
    type: llm
    variables: []                       # 当引用其他节点变量时填写
    vision:                             # 多模态视觉（选填）
      enabled: false
      configs:                          # enabled=true 时填写
        detail: high
        variable_selector:
          - <node_id>
          - <variable_name>
  height: 96
  id: llm
  position:
    x: 400
    y: 282
  positionAbsolute:
    x: 400
    y: 282
  selected: false
  sourcePosition: right
  targetPosition: left
  type: custom
  width: 244
```

## 最小骨架（仅 `data` 块）

```yaml
data:
  context:
    enabled: false
    variable_selector: []
  desc: ''
  model:
    completion_params:
      temperature: 0.7
    mode: chat
    name: gpt-4o-mini
    provider: openai
  prompt_template:
    - id: <uuid>
      role: system
      text: '你是助手。'
    - id: <uuid>
      role: user
      text: '{{#sys.query#}}'
  selected: false
  title: LLM
  type: llm
  variables: []
  vision:
    enabled: false
```
