# Field Dictionary

Enum values and type names used in Dify DSL. Never invent values — use only from this list.

## CRITICAL: version field

`version: "0.6.0"` — **MUST be a quoted string** in YAML. If written as `version: 0.6.0` (unquoted), YAML parses it as a float, and Dify import **FAILS** with "Invalid version type" error.

## CRITICAL: conversation_variables id

`conversation_variables[].id` — **MUST be a valid UUID** (e.g., `d4e1f2a3-b4c5-46d7-8e9f-0a1b2c3d4e5f`). Dify stores this in a PostgreSQL UUID column. Non-UUID values like `cv_phase` cause **500 Internal Server Error**.

## completion_params (llm model)

Best practice: only include `temperature`. Extra params (`frequency_penalty`, `max_tokens`, `presence_penalty`, `top_p`) may cause issues on some Dify configurations.

```yaml
model:
  completion_params:
    temperature: 0.7
```

## edge id format

`{source_id}-{sourceHandle}-{target_id}-target`

Examples:
- `1780164189283-source-1780164194792-target`
- `1780164346416-dp-1780164383571-target`
- `1780164346416-false-17801659503280-target`

## comparison_operator (if-else, loop break_conditions)

`contains`, `not contains`, `start with`, `end with`, `is`, `not empty`, `empty`, `=`, `>`, `<`, `>=`, `<=`, `in`, `not in`

## varType (if-else conditions)

`string`, `number`

## error_handle_mode (iteration, loop)

`terminated`, `continue-on-error`, `remove-abnormal-output`

## operation (assigner items)

`over-write`, `clear`, `append`, `extend`, `set`, `+=`, `-=`, `*=`, `/=`, `remove-first`, `remove-last`

## input_type (assigner items)

`variable`, `constant`

## write_mode (assigner items)

Same as `operation`: `over-write`, `clear`, `append`, `extend`, `set`

## start variable types

`text-input`, `paragraph`, `select`, `number`, `file`, `file-list`

## code_language

`python3`, `javascript`

## code output types

`string`, `number`, `array[string]`, `array[object]`

## retrieval_mode (knowledge-retrieval)

`multiple`, `single`

## reasoning_mode (parameter-extractor)

`function_call`, `prompt`

## http method (http-request, trigger-webhook)

`get`, `post`, `put`, `patch`, `delete`

## http content_type (trigger-webhook)

`application/json`, `multipart/form-data`, `application/x-www-form-urlencoded`, `text/plain`, `application/octet-stream`

## authorization.type (http-request)

`no-auth`, `api-key`

## authorization.config.type (http-request)

`basic`, `bearer`, `custom`

## trigger-schedule mode

`visual`, `cron`

## conversation_variables value_type

`string`, `integer` (for numeric counters, NOT `number`)

## variable_selector root domains

`sys`, `env`, `conversation`

## model mode

Always `chat` for LLM nodes.

## tool_parameters value type

`mixed` — template string value (e.g., `'{{#llm.text#}}'`)
`variable` — selector array value (e.g., `[start, my_file]`)
`constant` — literal string value (e.g., `'hello'`)

## iteration / loop output_type

`array[string]`, `array[number]`, `array[object]`

## variable-aggregator output_type

`string`, `array[string]`, `array[object]`

## parameter-extractor parameter types

`string`, `number`, `boolean`, `array[string]`, `array[number]`, `array[object]`

## knowledge-index chunk_structure

`text_model`, `hierarchical_model`, `qa_model`

## provider strings (fully qualified)

- `langgenius/openai/openai`
- `langgenius/siliconflow/siliconflow`
- `langgenius/google/google`
- `langgenius/anthropic/anthropic`
- `langgenius/azure_openai/azure_openai`
- `langgenius/tongyi/tongyi`

## model names (common)

OpenAI: `gpt-4o`, `gpt-4o-mini`, `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
Anthropic: `claude-sonnet-4-6`, `claude-opus-4-7`, `claude-haiku-4-5`
Google: `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.0-flash`
SiliconFlow: `deepseek-ai/DeepSeek-V3`, `Qwen/Qwen3-235B`, `internlm/internlm2_5-7b-chat`

## dependency types

`marketplace` — with `marketplace_plugin_unique_identifier` field
`package` — with `plugin_unique_identifier` field
