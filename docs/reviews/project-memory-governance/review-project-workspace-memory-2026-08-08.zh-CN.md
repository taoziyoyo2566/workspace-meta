# 项目与工作区 Memory 治理审查报告

状态：已审查；尚未达到实施批准条件。

日期：2026-08-08

审查文档：

- conversation-requirements-2026-08-07.md
- solution-project-workspace-memory.md
- plan-project-workspace-memory-2026-08-07.md
- 相关 .gitignore 变更

## 1. 范围快照

- 目标仓库：/home/saberu/workspace
- 分支和比较基线：main，a5ce3561a6691501e13ca51872e9d5f8b8589e59
- 范围内：3 份未跟踪 review 文档，以及使该 review 目录可被跟踪所需的 allowlist 变更。
- 仅作补充范围：/home/saberu/workspace/projects/reality-ops，因为计划明确包含其迁移。它是独立 Git 仓库，没有与 workspace-meta 的状态合并审查。
- 排除范围：主机本地 Codex/Claude 配置、凭据、hook 信任状态、远程状态、Git 发布，以及 live/生产验证。

## 2. 总体结果

“两种范围”的模型是合理的：详细项目事实留在各自项目中，workspace-meta 拥有可复用协议和高层项目地图。将 AI 语义工作与 SessionStart 及机械脚本分开，也符合现有工作区架构。

这些文档目前不应批准实施或发布。以下 P1 问题涉及目标所有权、写入权限、核心行为、可跟踪性、安全性或验收证据。

## 3. 审查发现

### P1-1 — Reality Ops 迁移跨越独立 Git 边界

计划把 Reality Ops 迁移纳入范围，并将 projects/reality-ops/* 列为实施文件，但工作区规则明确该目录是独立 Git 根目录。当前补充检查发现 Reality Ops 有已修改和未跟踪文件，包括 AGENTS.md、docs/project-memory.md、setup 和 scripts/check-project-memory.sh。

证据：

- plan-project-workspace-memory-2026-08-07.md:24-33,144-172
- ../../../AGENTS.md:7-9（工作区根规则）
- ../../../projects/reality-ops/AGENTS.md:1

需要改进：将 workspace-meta 协议变更与单独的 Reality Ops 迁移计划拆开。记录项目 Git 根目录、基线 HEAD 和脏状态、哪些现有改动属于本次范围，以及交接/验收边界。

### P1-2 — 自动初始化没有定义写入边界

方案和验收标准要求在第一次“实质性可写项目任务”中初始化，但没有定义“实质性”或“可写”的含义，也没有说明纯代码任务是否授权额外的文档变更。全局 Codex 适配器也需要明确适用边界：设计描述的是 ~/workspace/projects 下的项目，而计划说 make bootstrap 后任何新项目都获得该协议。

证据：

- solution-project-workspace-memory.md:20-28,144-158
- plan-project-workspace-memory-2026-08-07.md:127-142,335-353

需要改进：定义精确的初始化触发条件、任务授权与 memory 写入之间的关系，以及路由是只适用于工作区范围内的项目，还是适用于主机上的所有项目。

### P1-3 — 只读审计与写入审计历史互相冲突

计划定义了不得修改项目文件的“只读审计”，但同一阶段又要求更新当前 memory 并追加历史。验收标准分别要求只读任务不修改文件，以及快速审计写入历史。

证据：

- plan-project-workspace-memory-2026-08-07.md:192-214
- plan-project-workspace-memory-2026-08-07.md:335-353

需要改进：定义独立的 report-only 和 reconcile 模式。report-only 审计不得写入当前 memory 或历史；reconcile 审计只能写入声明的范围。

### P1-4 — 计划中的实施路径目前仍会被忽略

当前反向白名单允许这个 review 目录，但不允许计划列出的实施路径，包括新的规则文件、.agents/templates/、docs/architecture/memory-governance.md 和 docs/workspace-memory*。git check-ignore --no-index 已确认这些路径仍被总规则 * 匹配。

证据：

- .gitignore:1,8-23,34-45
- plan-project-workspace-memory-2026-08-07.md:101-111,236-243

需要改进：先确定模板目录，并在实施计划中加入精确的 allowlist 条目，同时把 pre-commit 验证列为明确阶段检查。

### P1-5 — AI 行为验收目前不可复现

fixture 部分列出了有价值的场景，但没有规定执行驱动、预期文件变化、通过/失败规则、审查者或持久证据格式。现有 make test 覆盖工作区配置/状态行为，不覆盖提议中的 memory 生命周期。

证据：

- plan-project-workspace-memory-2026-08-07.md:222-234,382-394

需要改进：将自动机械检查与人工 AI 行为检查分开。对每个 fixture 记录提示词、仓库状态、预期范围、实际变化、缺口和审查结果，并写入 round changelog 或批准的测试产物。

### P1-6 — 现有 memory 的身份识别和重复处理仍未解决

对话记录把自定义 memory 路径处理列为开放决定，而方案只要求查找“等价”的持久文档。计划包含非默认路径 fixture，却没有定义如何判定通过，也没有定义存在多个候选文件时的处理方式。

证据：

- conversation-requirements-2026-08-07.md:585-599
- solution-project-workspace-memory.md:144-158
- plan-project-workspace-memory-2026-08-07.md:224-234

需要改进：在实施前定义规范路径的声明/发现优先级、多候选文件处理方式和防止重复创建的规则。

### P1-7 — “明显 secret 模式”不能证明声明的安全标准

计划禁止 secrets 和原始敏感输出，但只提出检查明显模式。扫描器出现漏报时，不能证明更强的验收要求，即 memory/history 不包含敏感材料。

证据：

- solution-project-workspace-memory.md:227-248,263-274
- plan-project-workspace-memory-2026-08-07.md:275-296,335-353

需要改进：明确原始命令输出默认永不持久化；当证据可能含敏感信息时必须脱敏或标记为 blocked；扫描器只能作为纵深防御，不能作为“没有敏感信息”的证明。

## 4. P2 改进项

- 定义历史 ID、文件名、排序、并发行为，以及幂等的当前项目地图与新增审计事件之间的区别。当前“每次刷新都追加”和“不产生重复历史事实”的表述有歧义（solution-project-workspace-memory.md:227-248；计划第 6 节）。
- 工作区快照不仅记录项目 HEAD，也记录分支和 dirty 状态，避免把脏项目表示为完全最新。
- 标记对话文档是由 assistant 维护的转述，并补充来源信息；它不是逐字记录，也不能独立验证为用户原话。
- 删除 conversation-requirements-2026-08-07.md:607 的文件末尾多余空行；未跟踪文件的 diff 检查会报告该问题。

## 5. 已执行的验证

- make test：28 个测试通过。
- bash -n scripts/*.sh .githooks/pre-commit：通过。
- Reality Ops 补充 shell 语法检查：通过。
- 3 份 review 文档之间的相对链接：通过。
- review 目录 allowlist 检查：通过。
- 已跟踪文件的 git diff --check：通过。
- 将未跟踪的 conversation 文档纳入 no-index diff 检查：因第 607 行多余空行而失败。

未执行：bootstrap、主机 UI smoke test、实施专用 memory fixture、Reality Ops Ansible 检查、Git stage/commit/push 以及 live 验证。这些不是本文档审查的证据，仍是后续获得授权的实施阶段缺口。

## 6. 收尾

本次审查没有修改 3 份源文档或 .gitignore；本次新增的只有审查报告。工作树仍是本地、未发布状态。下一轮实施前应解决所有 P1 问题，更新方案和计划，然后进行定向复审，再开展任何跨仓库迁移或 Git 发布。
