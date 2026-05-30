# Import/Export Rules

Rules extracted from Dify source code (`api/services/app_dsl_service.py`, `api/services/dsl_version.py`, `api/services/workflow_service.py`).

## Version Rules

### Current Version
Current Dify DSL version is `"0.6.0"` (string constant in `api/constants/dsl_version.py`).

### Version Must Be String
`version: "0.6.0"` — **must be quoted**. If `version: 0.6.0` (unquoted), YAML parses it as float `0.6`, and import **FAILS** with "Invalid version type".

If version is missing entirely, Dify defaults to `"0.1.0"` (legacy fallback).

### Compatibility Matrix

| Imported vs Current | Status | Behavior |
|---|---|---|
| Exact match (`0.6.0` vs `0.6.0`) | `COMPLETED` | Direct import |
| Same major.minor, older micro | `COMPLETED` | Direct import |
| Same major, older minor (e.g. `0.5.x`) | `COMPLETED_WITH_WARNINGS` | Import succeeds with warnings |
| Older major (e.g. `0.x` vs `1.0`) | `PENDING` | User must confirm |
| Newer than current (e.g. `99.0.0`) | `PENDING` | User must confirm |
| Invalid version string | `FAILED` | Import rejected |

## Import Validation Checklist

Run through these checks before importing. Violations cause FAILED or 500 errors.

### CRITICAL (will fail)

1. **`version` is quoted string** — `"0.6.0"` not `0.6.0`
2. **`conversation_variables[].id` is valid UUID** — `d4e1f2a3-b4c5-46d7-8e9f-0a1b2c3d4e5f`, not `cv_phase`
3. **`start` and `trigger-*` cannot coexist** — choose one entry type; Dify throws `ValueError`
4. **All edge `source`/`target` IDs must reference existing nodes**
5. **Every edge must have `isInIteration` AND `isInLoop` in `data`**
6. **Loop edges (`isInLoop: true`) must have `loop_id`**
7. **Iteration edges (`isInIteration: true`) must have `iteration_id`**
8. **App overwrite** only works for `workflow` or `advanced-chat` mode

### HIGH (will cause 500 or broken behavior)

9. **`workflow` mode needs `end` node** — otherwise execution hangs
10. **`advanced-chat` mode needs `answer` node**
11. **`rag_pipeline` must have `knowledge-index` node**
12. **Conversation variables** only valid in `advanced-chat` mode
13. **All selectors `[node_id, field]` must match real node IDs and their output fields**

### MEDIUM (imports but may break at runtime)

14. **LLM `completion_params`** — keep only `temperature`; extra params may cause issues
15. **LLM `context.variable_selector`** — must be present (can be `[]`)
16. **Assigner `version: "2"`** — preferred over old format
17. **Tool `tool_node_version: "2"`** — for agent nodes
18. **`break_conditions` items need `id` field** (UUID)

## Import Flow

1. Client uploads YAML → Dify parses and validates version
2. If version PENDING → stores data in Redis (TTL 600s), returns `202`
3. Client calls confirm endpoint → proceeds with import
4. Creates/updates App record, syncs workflow graph
5. `sync_draft_workflow` validates: start/trigger coexistence, human_input schema
6. Deletes draft variables, returns COMPLETED
7. Client can check plugin dependencies

## Export Sanitization

During export, the following fields are NEVER exported as-is:

| Node Type | Field | Sanitization |
|-----------|-------|-------------|
| `knowledge-retrieval` | `dataset_ids` | **Encrypted** via AES-CBC (SHA-256 of tenant_id). Configurable via `DSL_EXPORT_ENCRYPT_DATASET_ID`. On import, decrypted; if invalid UUID, filtered out. |
| `tool` | `credential_id` | **Stripped** (unless `include_secret=True`) |
| `agent` | `agent_parameters.tools[].credential_id` | **Stripped** |
| `trigger-schedule` | `config` | **Reset to defaults** |
| `trigger-webhook` | `webhook_url`, `webhook_debug_url` | **Cleared to `""`** |
| `trigger-plugin` | `subscription_id` | **Cleared to `""`** |
| `environment_variables` (secret) | `value` | **Cleared** |
| `code` node | — | Passes through Cloudflare WAF; sandbox: no filesystem, no network, no OS commands |

## Graph-Level Constraints

### Entry Node Rules
Valid entry points (`_START_NODE_TYPES`): `start`, `datasource`, `trigger-webhook`, `trigger-schedule`, `trigger-plugin`.

**start vs trigger mutual exclusion:** If `start` node exists, no `trigger-*` node may exist (and vice versa).

### Mode Requirements
| Mode | Required Terminal |
|------|------------------|
| `workflow` | At least one `end` |
| `advanced-chat` | At least one `answer` |
| `rag_pipeline` | At least one `knowledge-index` |

### Billing Limits
Sandbox plan: maximum **2 trigger nodes**.

## Container Rules

### Container Membership
Dify uses `parentId` (on node envelope) to determine container membership. Not `isInLoop` in data.

### Edge Data
Every edge in `data` must have both `isInIteration: false` AND `isInLoop: false/true`. Container-internal edges need the corresponding `loop_id` or `iteration_id`.

### Container Start Nodes
- `loop-start`: wrapper `type: custom-loop-start`, `draggable: false`, `selectable: false`, `width: 44`, `height: 48`
- `loop-end`: wrapper `type: custom-simple`, `width: 243`, `height: 52` — do NOT add `draggable`/`selectable`
- `iteration-start`: wrapper `type: custom-iteration-start`
- Container nodes reference start via `data.start_node_id`

## Variable Reference Syntax

| Context | Syntax | Example |
|---------|--------|---------|
| Prompt/text interpolation | `{{#node_id.field#}}` | `{{#llm.text#}}` |
| Selector arrays (YAML) | `[node_id, field]` | `[llm, text]` |
| Code node params | Direct name | `arg1` in `main(arg1: str)` |
| Jinja2 templates | `{{ var }}` | `{{ text \| upper }}` |
| System variables | `{{#sys.xxx#}}` | `{{#sys.query#}}`, `{{#sys.user_id#}}` |
| Environment | `{{#env.xxx#}}` | `{{#env.API_KEY#}}` |
| Conversation | `[conversation, name]` | `[conversation, phase]` |

## Sandbox Constraints (Code Node)

- No filesystem access
- No network capabilities
- No OS command execution
- Code passes through Cloudflare WAF
- Max call depth, execution steps, and execution time configured via environment variables

## Dependencies

### Format
```yaml
dependencies:
  - current_identifier: null
    type: marketplace           # marketplace | package | github
    value:
      marketplace_plugin_unique_identifier: <provider/plugin:version@hash>
      version: null
```

### Auto-Extraction
For DSL versions <= `0.1.5`, dependencies are auto-extracted from workflow nodes (tool providers, model providers). For `0.6.0`, the `dependencies` field is used directly.
