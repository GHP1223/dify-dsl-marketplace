# Dify DSL Skill for Claude Code

Design, generate, review, refactor, and validate **Dify Workflow**, **Chatflow**, and **RAG Pipeline** DSL — all from within Claude Code.

## What It Does

This skill converts the entire [Dify DSL Skill Pack](https://github.com/anthropics/skills) into a single Claude Code plugin. It provides structured workflows for:

| Workflow | When to Use |
|----------|-------------|
| **Brainstorm** | Requirements unclear, need to clarify unknowns before building |
| **Author** | Create new DSL from clear requirements |
| **Review** | Read-only analysis of existing DSL (risk grading, import judgment) |
| **Refactor** | Fix, optimize, or restructure existing DSL |
| **Template** | Pick a template/skeleton as starting point |
| **Governance** | Delivery/release judgment — "can this be shipped?" |
| **Subagent Review** | Multi-party independent review with conflict resolution |
| **Forward Testing** | Validate the skill itself using real fixtures |

## What's Included

```
dify-dsl-skill/
├── .claude-plugin/
│   └── plugin.json                     # Plugin manifest
└── skills/
    └── dify-dsl/
        ├── SKILL.md                     # Main skill (routing + 8 workflows)
        ├── references/                  # 80 reference docs
        │   ├── dify-dsl-foundations---*.md    # Shared base (modes, selectors, contracts)
        │   ├── dify-dsl-nodes---*.md          # 21 node type docs
        │   ├── dify-dsl-templates---*.md      # Template library & variants
        │   ├── dify-dsl-quality---*.md        # Review rules, anti-patterns, fix strategies
        │   ├── dify-dsl-governance---*.md     # Delivery gates, coverage, observability
        │   ├── dify-dsl-subagent-review---*.md # Multi-review orchestration
        │   ├── dify-dsl-forward-testing---*.md # Skill validation playbook
        │   └── dify-dsl-brainstorming---*.md   # Design doc templates
        ├── scripts/                     # 12 validation scripts
        │   ├── lint_dsl.py              # Deterministic DSL lint (50+ error codes)
        │   ├── fast_test_dsl.py         # Quick DSL structure analysis
        │   └── ...                      # Test suite, report comparison, etc.
        └── fixtures/                    # 31 DSL samples
            ├── min-workflow.yml         # Minimal examples
            ├── broken-*.yml             # Intentionally broken for testing
            └── ghp_*.yml                # Real multi-agent system DSL
```

## Installation

### Option 1: Install from this Marketplace (Recommended)

In Claude Code CLI or VSCode extension, run:

```
/plugin marketplace add 1094184321/dify-dsl-marketplace
```

Then:

```
/plugin install dify-dsl@ghp-local-plugins
```

### Option 2: Manual Installation

1. Clone this repository:

```bash
git clone https://github.com/1094184321/dify-dsl-marketplace.git
```

2. Copy the plugin to Claude Code's cache:

```bash
# Windows
mkdir -p "%USERPROFILE%\.claude\plugins\cache\dify-dsl-marketplace\dify-dsl\1.0.0"
xcopy /E /I dify-dsl-marketplace\plugins\dify-dsl "%USERPROFILE%\.claude\plugins\cache\dify-dsl-marketplace\dify-dsl\1.0.0"

# Linux / macOS
mkdir -p ~/.claude/plugins/cache/dify-dsl-marketplace/dify-dsl/1.0.0
cp -r dify-dsl-marketplace/plugins/dify-dsl/* ~/.claude/plugins/cache/dify-dsl-marketplace/dify-dsl/1.0.0/
cp -r dify-dsl-marketplace/plugins/dify-dsl/.claude-plugin ~/.claude/plugins/cache/dify-dsl-marketplace/dify-dsl/1.0.0/
```

3. Register in `~/.claude/plugins/installed_plugins.json` — add this entry to the `"plugins"` object:

```json
"dify-dsl@ghp-local-plugins": [
  {
    "scope": "user",
    "installPath": "<your-home>/.claude/plugins/cache/dify-dsl-marketplace/dify-dsl/1.0.0",
    "version": "1.0.0",
    "installedAt": "2026-05-29T12:00:00.000Z",
    "lastUpdated": "2026-05-29T12:00:00.000Z"
  }
]
```

4. Enable in `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "dify-dsl@ghp-local-plugins": true
  }
}
```

5. **Restart Claude Code**.

## Usage

After installation, the skill auto-triggers when you mention Dify-related keywords:

### Example Prompts

| What You Say | What Happens |
|-------------|--------------|
| "帮我设计一个 Dify workflow 处理 Landsat 数据" | Enters **Authoring** workflow |
| "审查一下这个 Dify DSL 文件" | Enters **Review** workflow |
| "这个 Dify Chatflow 有个 bug，帮我修" | Enters **Refactor** workflow |
| "我想建一个 Dify 工作流但不确定怎么做" | Enters **Brainstorming** workflow |
| "这个 DSL 能上线吗？" | Enters **Governance** workflow |
| "Dify DSL 模板有哪些？" | Enters **Template Selection** |

### Quick Start: Create a New DSL

```
你: 帮我创建一个 Dify advanced-chat DSL，用于遥感数据处理的多智能体系统

Claude Code:
→ 加载 dify-dsl skill
→ 执行 Brainstorming（如果需求不清）
→ 执行 Authoring workflow:
   1. 模式判断 (workflow / advanced-chat / rag_pipeline)
   2. 节点选择与配置
   3. 边连接
   4. 字段检查
   5. 输出完整 DSL YAML 草稿
```

### Validation Scripts

```bash
# Lint a DSL file (deterministic checks)
python3 scripts/lint_dsl.py my-workflow.yml

# Quick structure analysis
python3 scripts/fast_test_dsl.py my-workflow.yml

# Full validation suite
python3 scripts/run_validation_suite.py
```

## Supported Dify DSL Modes

| Mode | `app.mode` | Description |
|------|-----------|-------------|
| Workflow | `workflow` | Linear workflow with conditional branching |
| Advanced Chat | `advanced-chat` | Chat-based with loops, agents, and tools |
| RAG Pipeline | `rag_pipeline` | Retrieval-augmented generation pipeline |

## Architecture

The skill follows a routing pattern:

```
User request
    ↓
Intent Recognition & Routing (SKILL.md)
    ↓
Load Foundations (mode, selectors, contracts)
    ↓
Execute Targeted Workflow
    ├── Brainstorming → clarify requirements
    ├── Authoring → generate DSL draft
    ├── Review → read-only analysis
    ├── Refactor → fix & optimize
    ├── Template → select skeleton
    ├── Governance → delivery judgment
    ├── Subagent Review → multi-party review
    └── Forward Testing → validate skill itself
```

## Conversion Notes

This plugin was converted from the original 12-skill Dify DSL architecture:

| Original Skill | Merged Into |
|---------------|-------------|
| `using-dify-dsl` | SKILL.md routing logic |
| `dify-dsl-brainstorming` | Brainstorming workflow |
| `dify-dsl-authoring` | Authoring workflow |
| `dify-dsl-review` | Review workflow |
| `dify-dsl-refactor` | Refactor workflow |
| `dify-dsl-foundations` | `references/dify-dsl-foundations---*.md` |
| `dify-dsl-nodes` | `references/dify-dsl-nodes---*.md` |
| `dify-dsl-templates` | `references/dify-dsl-templates---*.md` |
| `dify-dsl-quality` | `references/dify-dsl-quality---*.md` |
| `dify-dsl-governance` | `references/dify-dsl-governance---*.md` |
| `dify-dsl-subagent-review` | `references/dify-dsl-subagent-review---*.md` |
| `dify-dsl-forward-testing` | `references/dify-dsl-forward-testing---*.md` |

All cross-references have been updated. 162 internal links verified valid.

## License

See the original project for license information.
