# 任务路由

先用本页决定应该进入哪个入口 skill，不要一上来把所有底座资料都读满。

## 总入口

如果当前平台把本仓库作为一个技能包安装，优先先进入 [../SKILL.md](../SKILL.md)，由它完成第一层意图识别和主路由判断。

1. 先读 [common-dsl.md](dify-dsl-foundations---common-dsl.md)。
2. 读 [orchestration-modes.md](dify-dsl-foundations---orchestration-modes.md)，先判模式。
3. 判断任务类型：新建、模板起手、只读审核、修复 / 优化 / 重构、多方独立复核 / 冲突归并。
4. 根据任务类型切到对应入口 skill。

## 快速路由表

<!-- BEGIN ROUTE_MATRIX -->
| 用户目标 | 推荐入口 | 常见下一步 |
| --- | --- | --- |
| 需求还没收敛 | [using-dify-dsl](../SKILL.md) 或 [dify-dsl-brainstorming](../SKILL.md) | `dify-dsl-authoring / review / refactor` |
| 新建 DSL | [using-dify-dsl](../SKILL.md) 或 [dify-dsl-authoring](../SKILL.md) | 高复杂度时进入 `dify-dsl-subagent-review` |
| 只读审查已有 DSL | [using-dify-dsl](../SKILL.md) 或 [dify-dsl-review](../SKILL.md) | 需要多方复核时进入 `dify-dsl-subagent-review` |
| 修改已有 DSL | [using-dify-dsl](../SKILL.md) 或 [dify-dsl-refactor](../SKILL.md) | 修改后需要独立复核时进入 `dify-dsl-subagent-review` |
| 只想选模板 | [using-dify-dsl](../SKILL.md) 或 [dify-dsl-templates](../SKILL.md) | 如需正文再进入 `dify-dsl-authoring` |
| 只想判断能不能交付 | [using-dify-dsl](../SKILL.md) 或 [dify-dsl-governance](../SKILL.md) | 如果用户同时明确要求多方独立复核或冲突归并，再进入 `dify-dsl-subagent-review` |
| 明确要组织多方复核 | [using-dify-dsl](../SKILL.md) 或 [dify-dsl-subagent-review](../SKILL.md) | 按并行 / 串行 / 单子代理 / 无子代理退化 |
<!-- END ROUTE_MATRIX -->

## 新建 DSL

适用于从零生成 `workflow`、`advanced-chat` 或 `rag_pipeline`。

- 入口 skill：
  [../SKILL.md](../SKILL.md)
- 需要补读的底座文档：
  [selector-templates.md](dify-dsl-foundations---selector-templates.md)、[output-fields-catalog.md](dify-dsl-foundations---output-fields-catalog.md)、[node-io-contracts.md](dify-dsl-foundations---node-io-contracts.md)
- 需要节点知识时：
  [../SKILL.md](../SKILL.md)

## 模板起手

适用于“先挑模板，再做裁剪、补字段或重排”。

- 入口 skill：
  [../SKILL.md](../SKILL.md)
- 模板底座：
  [../SKILL.md](../SKILL.md)

## 只读审核

适用于不直接改 DSL，只做结构分析、问题分级和只读审查结论。

- 入口 skill：
  [../SKILL.md](../SKILL.md)
- 审查与问题分级：
  [../SKILL.md](../SKILL.md)

## 发布判断或上线前检查

适用于用户已经明确在问“能不能交付 / 上线 / 放行”，而不是普通结构排查。

- 入口 skill：
  [../SKILL.md](../SKILL.md)
- 如果用户同时明确要求多方独立复核或冲突归并：
  [../SKILL.md](../SKILL.md)
- 发布结论、覆盖率与观测字段：
  [../SKILL.md](../SKILL.md)

## 修复、优化或重构

适用于最小修复、结构优化、成本优化、能力块重构或模板重排。

- 入口 skill：
  [../SKILL.md](../SKILL.md)
- 修复与优化策略：
  [../SKILL.md](../SKILL.md)
- 节点细节：
  [../SKILL.md](../SKILL.md)
- 模板重排：
  [../SKILL.md](../SKILL.md)
- 变更影响与上线前检查：
  [../SKILL.md](../SKILL.md)

## 多方独立复核或冲突归并

适用于已经有 DSL 草稿或已有 DSL，且当前目标是正式组织多方独立复核、子代理退化或冲突仲裁。

- 入口 skill：
  [../SKILL.md](../SKILL.md)
- 模式与编排手册：
  [dify-dsl-subagent-review---mode-selection-matrix.md](dify-dsl-subagent-review---mode-selection-matrix.md),
  [dify-dsl-subagent-review---orchestration-playbook.md](dify-dsl-subagent-review---orchestration-playbook.md)
- 角色定义：
  [dify-dsl-quality---index.md](dify-dsl-quality---index.md)

## 任务切换规则

- 如果任务目标仍模糊，先回 [../SKILL.md](../SKILL.md)。
- 同时出现“先生成再审查”时，先完成 authoring，再进入 review。
- 同时出现“先修复再优化”时，先消除阻塞问题，再讨论结构优化。
- 如果已经完成 authoring 或 refactor，但当前样本进入高复杂度、高风险或明确需要多方独立复核，先转去 [../SKILL.md](../SKILL.md)，不要直接跳到 governance 下最终结论。
- 如果问题本质上是模式判断错误，不要在错误模式上继续修字段，先回到 [orchestration-modes.md](dify-dsl-foundations---orchestration-modes.md) 重判。
