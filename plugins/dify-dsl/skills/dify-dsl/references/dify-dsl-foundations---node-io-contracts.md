# 节点输入输出约定

生成或调整编排时，不只看字段是否齐全，还要看节点的输入输出约定是否匹配。

## 变量引用语法速查

### 模板字符串引用（用于 `prompt_template.text`、`answer.answer`、`template` 等）

| 语法 | 含义 | 示例 |
|------|------|------|
| `{{#node_id.field#}}` | 引用某节点的输出字段 | `{{#llm.text#}}` |
| `{{#sys.query#}}` | 用户输入查询 | `{{#sys.query#}}` |
| `{{#sys.files#}}` | 用户上传的文件 | `{{#sys.files#}}` |
| `{{#env.var_name#}}` | 环境变量 | `{{#env.API_KEY#}}` |
| `{{#conversation.var_name#}}` | 对话变量 | `{{#conversation.counter#}}` |
| `{{#context#}}` | 知识检索上下文文本 | `{{#context#}}` |
| `{{#node_id.output#}}` | 变量聚合器/模板转换输出 | `{{#agg_1.output#}}` |
| `{{#node_id.param_name#}}` | 参数提取器的提取参数 | `{{#pe_1.city#}}` |
| `{{#node_id.result#}}` | 知识检索结果 | `{{#kr_1.result#}}` |
| `{{#node_id.text#}}` | LLM/tool/document-extractor文本输出 | `{{#llm_1.text#}}` |
| `{{#node_id.files#}}` | 文件输出（如工具产生的文件） | `{{#tool_1.files#}}` |
| `{{#node_id.body#}}` / `{{#node_id.status_code#}}` | HTTP 响应字段 | `{{#http_1.body#}}` |

### 变量选择器（用于 `value_selector`、`variable_selector`、`query_variable_selector`、`iterator_selector` 等数组格式）

所有 selector 使用二元素或三元素数组: `[node_id, field_name]` 或 `[node_id, field_name, index]`

| 写法 | 含义 |
|------|------|
| `[start, query]` | start 节点的 query 变量 |
| `[llm, text]` | llm 节点的 text 输出 |
| `[http_node, status_code]` | HTTP 节点的状态码 |
| `[aggregator_node, output]` | 聚合器节点的 output |
| `[sys, query]` | 系统变量 sys.query |
| `[sys, files]` | 系统文件变量 |
| `[conversation, var_name]` | 对话变量 |
| `[env, var_name]` | 环境变量 |

### tool_parameters 中的值引用

```yaml
# mixed 类型 — 模板字符串
tool_parameters:
  text_input:
    type: mixed
    value: '{{#llm.text#}}'

# variable 类型 — 变量选择器数组
tool_parameters:
  file_input:
    type: variable
    value:
      - start
      - my_file
```

### 迭代内部变量引用

在迭代内部节点的模板中，通过 `{{#iteration_start_node_id.item#}}` 引用当前迭代项:

## 1. 文本生成节点

常见节点:

- `llm`
- `answer`
- `template-transform`

输入约定:

- 接受文本、模板文本、对话变量、检索结果摘要。

输出约定:

- 主要输出文本，或可直接被模板消费的文本片段。

常见问题:

- 上游传入对象或数组，下游却按纯文本消费。
- `answer` 直接引用了并不存在的文本字段。

## 2. 模型路由与结构化抽取节点

常见节点:

- `parameter-extractor`
- `question-classifier`

输入约定:

- 接受文本、模板文本或可转成文本的上游结果。

输出约定:

- `parameter-extractor` 主要输出结构化参数字段，以及成功/失败辅助字段。
- `question-classifier` 主要输出分类结果字段，例如类别 ID、类别名或对应路由信息。

常见问题:

- 把这两类节点误当成“文本输出节点”来设计下游。
- 下游只按 `text` 消费，忽略真实结构化字段。

## 3. 结构化结果节点

常见节点:

- `code`
- `tool`
- `end`
- `assigner`
- `variable-aggregator`

输入约定:

- 接受变量、对象、数组、工具参数或显式选择器。

输出约定:

- 输出对象、数组或稳定字段集合。

常见问题:

- `code.outputs` 与真实返回值不一致。
- `end.outputs.value_selector` 指向了不存在的字段。

## 4. 检索与知识节点

常见节点:

- `knowledge-retrieval`
- `document-extractor`
- `knowledge-index`
- `datasource`

输入约定:

- 接受查询文本、文件、文档、分块结果。

输出约定:

- 检索片段、抽取文本、分块结果、索引写入输入。

常见问题:

- 文档还没抽取就直接索引。
- `knowledge-index.chunk_structure` 与上游结果结构不匹配。

## 5. 条件与控制节点

常见节点:

- `if-else`
- `question-classifier`
- `iteration`
- `loop`
- `list-operator`

输入约定:

- 需要可判断、可迭代、可比较的数据。

输出约定:

- 输出分支路径、汇总结果、过滤后的列表或容器结果。

常见问题:

- `iteration` 输入不是数组。
- `loop` 无法收敛。
- `if-else` 条件值与变量类型不一致。

## 6. 外部触发与交互节点

常见节点:

- `trigger-webhook`
- `trigger-schedule`
- `trigger-plugin`
- `human-input`
- `http-request`

输入约定:

- 接受事件参数、表单输入、请求参数、外部响应。

输出约定:

- 输出事件载荷、人工表单结果、HTTP 响应字段。

常见问题:

- 入口字段定义与下游消费字段不一致。
- `human-input` 动作恢复路径不完整。

## 约定检查顺序

1. 先判断上游输出类型。
2. 再判断当前节点是否能消费该类型。
3. 再判断当前节点输出是否被下游正确消费。
4. 最后检查空值、失败值、默认值是否会破坏链路。
