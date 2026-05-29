# tool 节点

## 作用

调用 Dify 工具或插件工具。

## 必填字段

- `type: tool`: 指定当前节点是工具调用节点。
- `provider_id`: 工具提供方标识，用于定位工具来源。
- `provider_type`: 提供方类型，用于区分内置或插件来源。
- `provider_name`: 提供方展示名，便于识别具体来源。
- `tool_name`: 工具内部名称，决定实际调用哪个工具。
- `tool_label`: 工具展示名，便于画布识别。
- `tool_configurations`: 工具配置项，控制工具运行方式。
- `tool_parameters`: 工具入参映射，没有它通常无法完成实际调用。

## 选填字段

- `credential_id`: 工具需要绑定凭证时填写。
- `plugin_unique_identifier`: 工具来自插件市场或插件实例时填写。
- `tool_node_version`: 当前推荐显式写，通常为 `"2"`；旧 DSL 缺失该字段时，编辑器和运行时可能进入兼容解析路径。

## 贯通性分析

- 上游通常提供工具参数、文件、文本或结构化对象。
- 下游常接 `end`、`llm`、`code`、`knowledge-index`。
- 关键是动态参数 schema 与当前传入值类型一致，下游也要知道消费哪个工具输出字段。

## 可承接上游节点

### 推荐

- `start`
- `http-request`
- `template-transform`
- `assigner`
- `document-extractor`

### 可用但需人工确认

- `llm`
- `code`
- `knowledge-retrieval`
- `human-input`

### 不推荐

- `end`
- `answer`
- 任意 `trigger-*`

## 可衔接下游节点

### 推荐

- `end`
- `llm`
- `code`
- `knowledge-index`
- `variable-aggregator`
- `if-else`

### 可用但需人工确认

- `answer`
- `assigner`
- `template-transform`
- `human-input`

### 不推荐

- `start`
- 任意 `trigger-*`
- `datasource`

## tool_parameters 结构

`tool_parameters` 中每个参数的值为对象格式:

```yaml
tool_parameters:
  <param_name>:
    type: mixed         # mixed: 模板引用; variable: 变量选择器引用; constant: 常量
    value: <value>      # mixed 时为模板字符串; variable 时为 [node_id, field]; constant 时为字面值
```

## paramSchemas 结构

`paramSchemas` 描述每个工具参数的 schema（通常从插件定义自动导入）:

```yaml
paramSchemas:
  - auto_generate: null
    default: null
    form: llm                               # llm 或 form
    human_description:
      en_US: <description>
      zh_Hans: <中文描述>
    label:
      en_US: <Label>
      zh_Hans: <中文标签>
    llm_description: <description for LLM>
    max: null
    min: null
    name: <parameter_name>
    options: []                             # select 类型时: [{label: {zh_Hans:..., en_US:...}, value: ...}]
    placeholder: null
    precision: null
    required: true
    scope: null
    template: null
    type: string                            # string, number, file, secret-input, select, model-selector
```

## 节点完整结构

```yaml
- data:
    desc: ''
    is_team_authorization: true
    output_schema: null
    paramSchemas:
      - auto_generate: null
        default: null
        form: llm
        human_description:
          en_US: Input text to process
          zh_Hans: 待处理的输入文本
        label:
          en_US: Input Text
          zh_Hans: 输入文本
        llm_description: The text input to be processed
        max: null
        min: null
        name: text
        options: []
        placeholder: null
        precision: null
        required: true
        scope: null
        template: null
        type: string
    params:
      text: ''
    provider_id: <provider_id>
    provider_name: <provider_name>
    provider_type: builtin                   # builtin 或 api
    selected: false
    title: Tool
    tool_configurations: {}
    tool_description: <tool description>
    tool_label: <Tool Display Name>
    tool_name: <tool_function_name>
    tool_parameters:
      text:
        type: mixed
        value: '{{#source_node.text#}}'
    type: tool
  height: 52
  id: tool_1
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
