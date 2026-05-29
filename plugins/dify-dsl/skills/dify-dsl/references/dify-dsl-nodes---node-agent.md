# agent 节点

## 作用

执行 Agent 策略，并可接入工具参数。

## 必填字段

- `type: agent`
- `agent_strategy_provider_name`: 指定 agent 策略提供方。
- `agent_strategy_name`: 指定要执行的 agent 策略名称。
- `agent_strategy_label`: 指定策略展示名，便于区分不同 agent 节点。
- `agent_parameters`: 定义 agent 执行时所需参数集合。

## 选填字段

- `memory`: 需要让 agent 结合上下文历史推理时填写。
- `tool_node_version`: 当前推荐显式写，通常为 `"2"`；它不仅是兼容字段，也会影响 agent 工具参数的解析路径。

## 贯通性分析

- 上游通常提供用户输入、上下文变量或工具选择结果。
- 下游通常消费 agent 最终文本、结构化结果或 agent 中间轨迹摘要。
- 若 `agent_parameters` 中引用工具选择器或变量选择器，要确认上游节点真的产出了对应结构。

## 可承接上游节点

### 推荐

- `start`
- `assigner`
- `template-transform`
- `knowledge-retrieval`
- `tool`

### 可用但需人工确认

- `llm`
- `human-input`
- `variable-aggregator`
- 其他能提供上下文、参数或工具选择结果的节点

### 不推荐

- `end`
- `answer`
- 任意 `trigger-*`

## 可衔接下游节点

### 推荐

- `answer`
- `end`
- `if-else`
- `assigner`
- `template-transform`
- `code`

### 可用但需人工确认

- `tool`
- `human-input`
- `variable-aggregator`

### 不推荐

- `start`
- 任意 `trigger-*`
- `datasource`

## 编排约束

- `agent_parameters` 至少要与所选策略需要的参数名匹配。
- 每个参数值格式为 `{ type: constant, value: ... }`，`type` 通常是 `constant`。
- `agent_parameters.model.value` 是 model-selector 对象，含 `provider`、`model`、`mode`、`model_type`、`completion_params`、`type`。
- `agent_parameters.tools.value` 是工具列表，每个工具有 `enabled`、`provider_name`、`tool_name`、`tool_label`、`schemas`、`parameters` 等。
- `plugin_unique_identifier` 必须与 agent 插件版本精确匹配。
- 与 `tool` 节点不同，`agent` 更像”策略执行器”而不是单次工具调用。

## 节点完整结构

```yaml
- data:
    agent_parameters:
      instruction:
        type: constant
        value: '请根据用户输入{{#sys.query#}}和知识库{{#knowledge_node.result#}}完成分析任务'
      maximum_iterations:                                  # 可选
        type: constant
        value: 5
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
        value:
          - enabled: true
            extra:
              description: ''
            parameters:
              <param_name>:
                auto: 1
                value: null
            provider_name: <provider_name>
            schemas:
              - auto_generate: null
                default: null
                form: llm
                human_description:
                  en_US: <desc>
                  zh_Hans: <desc>
                label:
                  en_US: <label>
                  zh_Hans: <label>
                llm_description: <desc>
                max: null
                min: null
                name: <param_name>
                options: []
                placeholder: null
                precision: null
                required: true
                scope: null
                template: null
                type: string
            settings: {}
            tool_description: ''
            tool_label: <Tool Label>
            tool_name: <tool_name>
            type: builtin
    agent_strategy_label: ReAct
    agent_strategy_name: ReAct
    agent_strategy_provider_name: langgenius/agent/agent
    desc: ''
    output_schema: null
    plugin_unique_identifier: langgenius/agent:0.0.14@<hash>
    selected: false
    title: Agent
    type: agent
  height: 96
  id: agent
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

## 最小骨架

```yaml
data:
  agent_parameters:
    instruction:
      type: constant
      value: '你是助手'
    model:
      type: constant
      value:
        completion_params: {}
        mode: chat
        model: gpt-4o-mini
        model_type: llm
        provider: openai
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
  plugin_unique_identifier: langgenius/agent:0.0.14@<hash>
  selected: false
  title: Agent
  type: agent
```

支持的 agent 策略:
| agent_strategy_name | agent_strategy_label | agent_strategy_provider_name |
|---|---|---|
| `ReAct` | ReAct | `langgenius/agent/agent` |
| `function_calling` | FunctionCalling | `langgenius/agent/agent` |
| `mcp_agent` | MCP Agent | `hjlarry/agent/mcp_agent` |
