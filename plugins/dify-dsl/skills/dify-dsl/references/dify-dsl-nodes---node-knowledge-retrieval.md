# knowledge-retrieval 节点

## 作用

从知识库检索片段供下游模型或流程使用。

## 必填字段

- `type: knowledge-retrieval`: 指定当前节点是知识检索节点。
- `dataset_ids`: 指定要检索的知识库集合。
- `retrieval_mode`: 指定检索模式，例如单路或多路检索。

常见还需要:

- `query_variable_selector`: 指定查询文本来源，通常应显式填写。

## 按模式的额外字段

- `retrieval_mode: multiple`
  需要 `multiple_retrieval_config`，用于定义 `top_k`、阈值和 rerank 行为。

- `retrieval_mode: single`
  需要 `single_retrieval_config.model`，用于指定单路检索模型。

取值说明:

- `multiple`: 适合常规知识检索，通常可直接调 `top_k`、阈值和 rerank。
- `single`: 适合单模型单路径检索，配置更集中，但灵活性更低。

## 选填字段

- `query_attachment_selector`: 查询依赖附件时填写。
- `metadata_filtering_mode`: 需要按元数据过滤时填写。
- `metadata_model_config`: 元数据过滤依赖模型时填写。
- `metadata_filtering_conditions`: 需要手工指定过滤条件时填写。
- `vision`: 需要处理图像相关检索输入时填写。

## 贯通性分析

- 上游通常接 `sys.query`、`start` 输入、附件变量。
- 下游常接 `llm`、`answer`、`end`、`if-else`。
- 关键是确认查询字段、数据集、检索模式和下游对检索结果的消费方式一致。

## 可承接上游节点

### 推荐

- `start`
- `assigner`

### 可用但需人工确认

- `template-transform`
- `human-input`
- 其他能提供查询文本或附件变量的节点

### 不推荐

- `end`
- `answer`
- `knowledge-index`

## 可衔接下游节点

### 推荐

- `llm`
- `answer`
- `end`
- `if-else`
- `template-transform`

### 可用但需人工确认

- `code`
- `tool`
- `question-classifier`

### 不推荐

- `start`
- 任意 `trigger-*`
- `datasource`

## 编排约束

- `dataset_ids` 不能为空。
- 查询变量要指向文本或可转成文本的输入。
- 开启 metadata filtering 时，必须同步补过滤配置。

## 最小骨架

```yaml
data:
  desc: ''
  dataset_ids:
    - <dataset_uuid>
  multiple_retrieval_config:
    reranking_enable: true
    reranking_mode: reranking_model
    reranking_model:
      model: <reranking_model_name>
      provider: <provider>
    top_k: 4
  query_variable_selector:
    - <node_id>
    - sys.query
  retrieval_mode: multiple
  selected: false
  title: 知识检索
  type: knowledge-retrieval
```

输出变量通过 `{{#知识检索节点id.result#}}` 引用。

## 节点完整结构

```yaml
- data:
    desc: ''
    dataset_ids:
      - <dataset_uuid>
    multiple_retrieval_config:
      reranking_enable: true
      reranking_mode: reranking_model           # 或 weighting_schema
      reranking_model:                          # reranking_mode=reranking_model 时填写
        model: bce-reranker-base_v1
        provider: siliconflow
      top_k: 4                                  # 检索返回条数
    query_variable_selector:
      - <source_node_id>
      - sys.query
    retrieval_mode: multiple                    # multiple 或 single
    selected: false
    title: 知识检索
    type: knowledge-retrieval
  height: 90
  id: kr
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

`retrieval_mode: single` 时，用 `single_retrieval_config` 替代 `multiple_retrieval_config`:
```yaml
  single_retrieval_config:
    model:
      provider: openai
      name: gpt-4o-mini
      mode: chat
      completion_params: {}
```
