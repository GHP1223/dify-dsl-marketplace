# http-request 节点

## 作用

发起 HTTP 请求并把响应暴露给下游节点。

## 必填字段

- `type: http-request`: 指定当前节点是 HTTP 请求节点。
- `method`: 请求方法，`get`、`post`、`put`、`patch`、`delete`。
- `url`: 请求地址，支持 `{{#变量#}}` 模板。
- `authorization`: 鉴权配置，两层结构:
  - 外层 `authorization.type`: `no-auth` 或 `api-key`。**不要**写成 `basic` 或 `bearer`。
  - 若是 `api-key`，内层 `authorization.config`: `{ type: basic|bearer|custom, api_key: ..., header: ... }`
- `headers`: HTTP 请求头，字符串格式，每行一个 `Key:Value`。
- `params`: URL 查询参数，字符串格式。
- `body`: 请求体配置，含 `type`(none/json/form-data/x-www-form-urlencoded) 和 `data` 数组。
- `timeout`: 超时配置:
  - `max_connect_timeout: 0` — 0 表示无限制
  - `max_read_timeout: 0`
  - `max_write_timeout: 0`
  - 可选精确定时: `connect`、`read`、`write` (单位秒)

## 选填字段

- `retry_config`: 重试配置。含 `retry_enabled`、`max_retries`、`retry_interval`(毫秒)。
- `ssl_verify`: 证书校验控制。

## 贯通性分析

- 上游常接 `start`、`template-transform`、`assigner`，为 URL、headers、body 提供变量。
- 下游常接 `tool`、`code`、`end`、`if-else`。
- 关键是请求体类型和下游消费字段一致，例如下游到底需要 `body`、`text`、`status_code` 还是文件响应。

## 可承接上游节点

### 推荐

- `start`
- `template-transform`
- `assigner`

### 可用但需人工确认

- `code`
- `llm`
- `tool`
- `parameter-extractor`
- 其他能提供请求参数的节点

### 不推荐

- `end`
- `answer`
- 任意 `trigger-*`

## 可衔接下游节点

### 推荐

- `tool`
- `code`
- `end`
- `if-else`
- `template-transform`

### 可用但需人工确认

- `llm`
- `assigner`
- `answer`

### 不推荐

- `start`
- 任意 `trigger-*`
- `datasource`

## 兼容性提醒

- `headers`、`params` 常见为字符串字段。
- `body.data` 有时会出现空字符串，这属于兼容写法。
- `retry_config.enabled` 与 `retry_enabled` 可能混用，生成新 DSL 时不要无脑照抄。

## 节点完整结构

```yaml
- data:
    authorization:
      type: no-auth                        # 或 api-key
      config: null                          # api-key 时填写: { type: bearer, api_key: '...', header: 'Authorization' }
    body:
      type: json                            # none, json, form-data, x-www-form-urlencoded
      data:
        - id: key-value-1
          key: ''
          type: text
          value: '{"key": "{{#nodeId.var#}}"}'
    desc: ''
    headers: |                              # 字符串格式，一行一个 Header
      Content-Type:application/json
      Authorization:Bearer {{#env.apikey#}}
    method: post
    params: ''
    retry_config:                           # 可选
      max_retries: 3
      retry_enabled: true
      retry_interval: 100
    selected: false
    timeout:
      max_connect_timeout: 0                # 0 = 无限制
      max_read_timeout: 0
      max_write_timeout: 0
    title: HTTP Request
    type: http-request
    url: 'https://api.example.com/endpoint'
    variables: []
  height: 106
  id: http
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
