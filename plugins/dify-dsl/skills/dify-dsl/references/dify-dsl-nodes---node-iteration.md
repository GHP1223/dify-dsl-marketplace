# iteration / iteration-start 节点

## 作用

对数组逐项迭代执行子图。

## iteration 必填字段

- `type: iteration`: 指定当前节点是迭代容器。
- `iterator_selector`: 指向被遍历的数组来源。
- `output_selector`: 指向容器内部最终汇总出的结果。
- `start_node_id`: 指向容器内部起点节点。

## 选填字段

- `is_parallel`: 需要并行处理数组元素时填写。
- `parallel_nums`: 需要控制并发数量时填写。
- `error_handle_mode`: 需要控制单项失败后的行为时填写。
- `flatten_output`: 需要把嵌套数组拍平时填写。
- `output_type`: 需要显式声明容器输出类型时填写。

`error_handle_mode` 常见值说明:

- `terminated`: 任一项失败就终止整个迭代。
- `continue-on-error`: 单项失败时继续处理其他项。
- `remove-abnormal-output`: 失败项不保留输出，仅保留正常结果。

## iteration-start

内部起点节点使用:

- `type: iteration-start`: 指定容器内部起点。

通常只需要存在，不需要复杂业务字段。

## 贯通性分析

- 上游通常提供数组型输出，例如 `code.result` 或检索结果列表。
- 容器内节点负责逐项处理，最终由 `output_selector` 汇总回容器外。
- 关键是数组输入、内部起点、内部输出节点和容器外下游是否真正闭环。

## 可承接上游节点

### 推荐

- `code`
- `tool`
- `knowledge-retrieval`
- `list-operator`

### 可用但需人工确认

- `variable-aggregator`
- `assigner`
- 其他能输出数组的节点

### 不推荐

- `start`
- 任意 `trigger-*`
- `answer`

## 可衔接下游节点

### 推荐

- `end`
- `template-transform`
- `llm`
- `code`
- `variable-aggregator`

### 可用但需人工确认

- `answer`
- `tool`
- `list-operator`

### 不推荐

- `start`
- 任意 `trigger-*`

## 编排约束

- `start_node_id` 必须指向容器内真实存在的 `iteration-start` 节点。
- `iterator_selector` 必须引用数组。
- `output_selector` 必须指向容器内某个可输出节点。
- `output_type` 必须显式声明，如 `array[string]`、`array[object]`。
- 容器内节点 `data` 中必须含 `isInIteration: true` 和 `iteration_id`。
- 容器内节点外层必须含 `parentId` 指向 iteration 容器 `id`，`zIndex: 1002`。
- iteration-start 节点外层 `type: custom-iteration-start`（非 `custom`）、`draggable: false`、`selectable: false`。

## 容器完整结构

```yaml
# === 迭代容器节点 ===
- data:
    desc: ''
    error_handle_mode: terminated             # terminated, continue-on-error, remove-abnormal-output
    height: 285
    is_parallel: false
    iterator_selector:
      - <source_node_id>
      - <source_field>
    output_selector:
      - <child_llm_node_id>
      - text
    output_type: array[string]
    parallel_nums: 10
    selected: false
    start_node_id: <iteration_start_node_id>
    title: 迭代
    type: iteration
    width: 688                               # 迭代容器比普通节点宽
  height: 285
  id: '<iteration_id>'
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
  width: 688
  zIndex: 1

# === 迭代内部起点节点 ===
- data:
    desc: ''
    isInIteration: true
    selected: false
    title: ''
    type: iteration-start
  draggable: false
  height: 48
  id: '<iteration_start_node_id>'
  parentId: '<iteration_id>'
  position:
    x: 24
    y: 68
  positionAbsolute: ...
  selectable: false
  sourcePosition: right
  targetPosition: left
  type: custom-iteration-start
  width: 44
  zIndex: 1002

# === 迭代内普通节点 (如 LLM) ===
- data:
    desc: ''
    isInIteration: true
    iteration_id: '<iteration_id>'
    model:
      completion_params:
        temperature: 0.7
      mode: chat
      name: gpt-4o-mini
      provider: openai
    prompt_template:
      - id: <uuid>
        role: system
        text: '处理: {{#<iteration_start_node_id>.item#}}'
    selected: false
    title: 内部LLM
    type: llm
    variables: []
    vision:
      enabled: false
  height: 96
  id: '<child_llm_node_id>'
  parentId: '<iteration_id>'
  position:
    x: 80
    y: 60
  positionAbsolute: ...
  selected: false
  sourcePosition: right
  targetPosition: left
  type: custom
  width: 244
  zIndex: 1002
```

## 最小骨架

```yaml
data:
  desc: ''
  error_handle_mode: terminated
  is_parallel: false
  iterator_selector: [code, result]
  output_selector: [code_in_iter, result]
  output_type: array[string]
  parallel_nums: 10
  selected: false
  start_node_id: iter_start
  title: 迭代
  type: iteration
```
