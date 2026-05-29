# Dify DSL 公共结构

## 顶层骨架

需要同时区分三层口径:

- 当前导出标准: 以当前 Dify 导出实现为准。
- 历史 fixture 形状: 本地样例中仍可能保留旧版本结构。
- 编辑器字段: 为画布和导入体验服务，不等于运行时硬约束。

建议区分两套顶层 DSL:

- `kind: app`
- `kind: rag_pipeline`

### App DSL

```yaml
app:
  description: ''
  icon: "🤖"
  icon_background: '#FFEAD5'
  mode: workflow           # or advanced-chat, agent-chat
  name: your_app_name
  use_icon_as_answer_icon: false
dependencies: []            # see "依赖声明" section below
kind: app
version: 0.3.0              # current Dify export version; also seen: 0.1.2, 0.1.5
workflow:
  conversation_variables: []    # see "对话变量" section
  environment_variables: []     # see "环境变量" section
  features:                     # see "features 块" section
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
    nodes: []
    edges: []
    viewport:               # 画布视口，导入时保持布局
      x: 0
      y: 0
      zoom: 1
```

### 对话变量 (conversation_variables)

仅在 `advanced-chat` 模式下有效。用于跨多轮对话持久化状态。

```yaml
conversation_variables:
  - description: ''
    id: <uuid>
    name: <variable_name>
    selector:
      - conversation
      - <variable_name>
    value: ''               # 默认值
    value_type: string      # string, number, object, array[string]
```

在模板中的引用: `{{#conversation.<variable_name>#}}`

### 环境变量 (environment_variables)

用于存储密钥、API key 等不应硬编码在 DSL 中的变量。

```yaml
environment_variables:
  - description: ''
    id: <uuid>
    name: <variable_name>
    selector:
      - env
      - <variable_name>
    value: <secret_value>   # 导入后需手动填写
    value_type: string
```

在模板中的引用: `{{#env.<variable_name>#}}`

### 依赖声明 (dependencies)

声明应用依赖的 marketplace 插件或 package。

```yaml
dependencies:
  # marketplace 插件
  - current_identifier: null
    type: marketplace
    value:
      marketplace_plugin_unique_identifier: <provider/plugin:version@hash>
  # package 插件
  - current_identifier: null
    type: package
    value:
      plugin_unique_identifier: <provider/plugin:version@hash>
```

### RAG Pipeline DSL

```yaml
dependencies: []
kind: rag_pipeline
rag_pipeline:
  description: ""
  icon: "📙"
  icon_background: ""
  icon_type: emoji
  name: your_pipeline_name
version: 0.1.0
workflow:
  conversation_variables: []
  environment_variables: []
  features: {}
  graph:
    nodes: []
    edges: []
```

## 节点公共字段

所有节点 `data` 共享这些字段:

- `type`: 节点类型，必填。
- `title`: 标题，建议始终显式写。
- `desc`: 描述，可空。
- `version`: 默认 `"1"`，仅在特殊节点需要版本切换时显式设置。
- `error_strategy`: 可选，典型值是 `fail-branch` 或 `default-value`。
- `default_value`: 可选，失败兜底值。
- `retry_config`: 可选，常见字段是 `max_retries`、`retry_interval`、`retry_enabled`。

## 节点外层包装

每个节点在 `graph.nodes[]` 中的完整外层结构:

```yaml
- data:
    # 节点类型特定字段在这里
    desc: ''
    selected: false
    title: <节点标题>
    type: <节点类型>
    variables: []         # 大多节点有此字段
  height: <number>        # 典型值: start 88, llm 96, answer 103, tool 52, standard 88
  id: '<node_id>'         # 字符串，通常是时间戳或标签
  position:
    x: <number>
    y: <number>
  positionAbsolute:
    x: <number>
    y: <number>
  selected: false
  sourcePosition: right
  targetPosition: left
  type: custom            # 普通节点固定 custom；特殊: custom-iteration-start, custom-note
  width: <number>         # 典型值: 243, 244; iteration 容器 688-996
```

**特殊容器/迭代内节点额外字段:**

```yaml
  parentId: '<container_node_id>'    # 当节点在 iteration/loop 内部时
  zIndex: 1002                       # iteration 内部节点
  draggable: false                    # iteration-start 节点
  selectable: false                   # iteration-start 节点
```

**节点 `data` 中常见的公共字段:**

| 字段 | 说明 | 典型值 |
|------|------|--------|
| `desc` | 节点描述 | `''` |
| `selected` | 选中状态 | `false` |
| `title` | 节点标题 | 各节点不同 |
| `type` | 节点类型标识 | 见各节点文档 |
| `variables` | 输入变量映射 | `[]` 或数组 |

**当节点在 iteration 内部时，`data` 需额外包含:**

```yaml
    isInIteration: true
    iteration_id: '<container_node_id>'
```

## 边结构

每条边在 `graph.edges[]` 中的完整结构:

```yaml
- data:
    isInIteration: false       # true 时需同时写 iteration_id
    isInLoop: false
    sourceType: <source_node_type>
    targetType: <target_node_type>
  id: <source_id>-source-<target_id>-target    # 命名惯例
  source: '<source_node_id>'
  sourceHandle: source         # if-else 用 'true'/'false'/case_id; question-classifier 用 class_id
  target: '<target_node_id>'
  targetHandle: target
  type: custom
  zIndex: 0                    # iteration 内为 1002
```

**迭代内部边额外字段:**

```yaml
  data:
    isInIteration: true
    iteration_id: '<container_node_id>'
    isInLoop: false
    sourceType: <source_node_type>
    targetType: <target_node_type>
```

## 生成原则

1. 先定 `kind` 与模式，再定节点。
2. 先定节点 `id`，再写变量选择器。
3. 所有 `value_selector` / `variable_selector` / `query_variable_selector` 都必须引用已存在节点或变量域。
4. 容器节点必须先定义 `start_node_id`，再放内部起点节点。
5. `workflow` 模式优先收敛到 `end`；`advanced-chat` 优先收敛到 `answer`。
6. `rag-pipeline` 要额外检查 `rag_pipeline_variables` 与 `knowledge-index` 的衔接。
7. `start` 与 `trigger-*` 不要共存。

## 字段书写要求

每个节点文档都要同时给出:

- 必填字段
- 选填字段
- 贯通性分析

这里的“选填字段”不是装饰性罗列，而是要说明哪些字段在特定场景下建议补齐。

## 兼容性提醒

不同导出形态并不总是完全一致，常见差异:

- `version` 字段: 当前 Dify 导出版本一般为 `0.3.0`。旧版 `0.1.2`、`0.1.5` 仍可导入。新生成 DSL 优先用 `0.3.0`。
- `retry_config` 常见 `enabled` 与 `retry_enabled` 两种写法。
- `tool_parameters`、`datasource_parameters` 有时会出现简写字符串写法，也有对象写法。新生成优先使用显式 `{ type: ..., value: ... }` 对象形式。
- 节点 `data` 允许 `extra=allow`，所以导出 DSL 常混入历史字段。
- `provider` 字符串有两种格式: 简单格式 `openai`、`siliconflow`；全限定格式 `langgenius/siliconflow/siliconflow`。生成 DSL 时根据实际情况选用。

结论:

- 新生成 DSL 优先写稳定、清晰的字段结构。
- 如果生成与现有 DSL 不同版本的格式，必须在报告里标记版本差异。
- 所有节点 `data` 中必须包含 `desc: ''`、`selected: false`、`variables: []`（当节点需要输入变量映射时）。
