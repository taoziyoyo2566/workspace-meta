# Memory Governance 方向审查的独立调查结果

Status: Investigation result；独立调查 `review-direction-memory-governance-2026-08-11.zh-CN.md` 的事实、推理和处置建议。本文件不批准 Protocol、安装运行时、修改 Reality Ops 或执行 Git 发布。

Date: 2026-08-11

## 1. 调查结论

原方向审查**不能整体采纳，也不应整体驳回**。

它发现了三个真实问题：

1. 当前计划没有把未来的可执行载体、参考实现和 Phase 4 的验收关系写清楚；
2. Protocol 的体量、规范细节和多 Agent 恢复设计相对于目前唯一明确的真实失效，存在范围膨胀风险；
3. 新的行为规则需要更明确地记录来源事件、用户需求和采用理由。

但它的核心 P1-1 论据不成立：它把 `projects/reality-ops/` 工作树中未提交、未跟踪的候选实现当成了已落地且由 CI 强制执行的基线。该仓库的 `HEAD=7e93c01` 中没有 `AGENTS.md` 或 `scripts/check-project-memory.sh`；memory gate 也只出现在当前工作树对 workflow 的未提交修改中。

因此，“现有唯一机械实现已被 Protocol 排除”不是已证实事实，而是对一份未发布项目工作树的范围解释。

独立处置结论：

- 不废弃 v0.1.1 文档链；
- 不直接进入运行时安装或 Reality Ops 迁移；
- 将当前 Phase 1 扩展为一次**方向闸门**：修正证据基线、确定 MVP 范围，并为执行载体和 fixture 安排明确位置；
- 之后优先验证 freshness/reconciliation 的最小闭环，再决定是否保留完整的 Claim ID、history、幂等和并发恢复规范；
- 停止继续产生“审查审查结果”的文档层级，下一轮应产出决策记录、参考 harness 或最小 fixture，而不是新的泛化评论。

## 2. 范围和证据边界

### 2.1 目标仓库

- 目标仓库：`/home/saberu/workspace`，workspace-meta 根仓库。
- 比较基线：`a5ce3561a6691501e13ca51872e9d5f8b8589e59`（本地 `main` 与本地 `origin/main` 的跟踪状态一致；本调查未重新 fetch）。
- 主调查对象：
  - `review-direction-memory-governance-2026-08-11.zh-CN.md`；
  - `memory-governance-protocol-v0.1.1-2026-08-09.zh-CN.md`；
  - `plan-memory-governance-v0.1.1-2026-08-09.zh-CN.md`；
  - `.agents/rules/rule-authoring.md`；
  - `feedback-register.md`；
  - `conversation-requirements-2026-08-07.zh-CN.md`。

### 2.2 Supplemental only

`projects/reality-ops/` 是独立 Git 根，只用于核对方向审查引用的工作树/提交边界。未修改、未 stage、未运行其 checker，也未把它的 dirty 工作树当作 workspace-meta 的实现证据。

调查时该仓库有 17 个 dirty/untracked 路径。其 `HEAD` 为 `7e93c011c1a1e7c1ddf424a49a509984de438093`，与方向审查引用的短哈希一致，但工作树并不等于该提交。

## 3. 对原方向审查主要发现的复核

### 3.1 P1-1：Reality Ops checker 被排除在协议外

**判定：原 review 的事实表述不成立；方向性提醒部分成立。严重度：P1（证据/范围判定缺陷），不是 Protocol 已证实的 P1。**

复核结果：

- `git -C projects/reality-ops ls-files` 显示 `AGENTS.md` 未被 HEAD 跟踪；
- `scripts/check-project-memory.sh` 未被 HEAD 跟踪；
- `git show HEAD:.github/workflows/quality.yml` 中没有 memory gate；
- 当前工作树的 `.github/workflows/quality.yml` 修改才加入了该 gate；
- 当前工作树的 `AGENTS.md` 和 checker 是候选实现，不是已发布的 CI 契约。

即使把候选实现作为 supplemental 设计输入，它也只检查“触发路径变更时是否同时改动 `docs/project-memory.md`”，并不实现 Protocol 所要求的语义提取、Claim 身份、history、幂等、并发检查或恢复状态机。因此它不能证明“完整协议已有唯一可行实现”，也不能证明 D05 当前划分必然错误。

应保留的提醒是：Reality Ops 候选 checker 很适合作为**项目适配器样例**，但必须先在它自己的仓库完成独立计划、验证和发布，之后才能作为已发布案例引用。

### 3.2 P1-2：标识符和并发没有可执行载体

**判定：计划缺口成立；“当前方向不可行”不成立。严重度：P1（Phase 2/4 的出口定义缺口）。**

Protocol 是规范草案，不是可执行程序。它已经明确：

- `operation_key` 的规范化输入、排序、固定 JSON 和 SHA-256 规则；
- `claim_id` 的作用域、ULID、碰撞停止和重试复用规则；
- prepared/reconcile/applied 的恢复语义；
- 运行时脚本、hook 或适配器要另行授权。

因此“规则文件本身不能计算 SHA-256/ULID”只证明需要实现层，不证明设计失败。OpenAI 的官方 context-personalization 示例也把长期状态放在结构化 state 中，通过 tool、hook/context injection 和 consolidation 逻辑实现，而不是把全部行为寄托在自然语言规则上。[OpenAI Context Personalization](https://developers.openai.com/cookbook/examples/agents_sdk/context_personalization)

真正的问题是 Active plan 没有明确安排以下内容：

- Phase 2 的参考 harness 如何执行规范 JSON、hash、Claim fixture 和冲突样例；
- Phase 4 的最小垂直切片由哪个脚本/工具/Agent 操作承载；
- 参考 harness 与生产适配器的边界；
- 哪些失败应停在 report-only，哪些才允许写入。

这应作为计划修订项关闭，而不是用它否定 Protocol。最小修订方向是：Phase 2 先提供隔离的 reference harness；Phase 4 再实现一个项目边界内的 adapter。二者都不需要把所有语义判断硬编码成通用脚本。

### 3.3 P1-3：缺少源事件

**判定：来源记录确实不完整；“没有源事件”不准确。严重度：P2。**

原 review 的直接扫描结果只对它扫描的文档快照成立，但当前证据已经存在：

- `feedback-register.md` 的 W-R24 记录了真实的 stale-memory 失效：环境事实发生变化后，旧 memory 没有重验，导致后续计划建立在错误前提上；
- `conversation-requirements-2026-08-07.zh-CN.md` 记录了本 program 的真实起点、用户需求、SessionStart 边界和“由 AI 判断但不由后台静默写入”的方向；
- `.agents/rules/rule-authoring.md` 要求 portable feedback 记录来源事件和理由，但并没有证明每个探索性设计文档在形成前必须已经拥有一个 W-R 编号。

当前缺口是：Protocol 的 `§1.1 设计依据` 没有直接把 W-R24 和对话需求文档纳入来源链，导致读者难以区分“真实失效驱动的最小需求”和“后来扩展出的通用协议设计”。应补 provenance mapping，但不必据此废弃 program。

### 3.4 P2-1：规范重心与已知失效不成比例

**判定：这是最值得采纳的方向性批评。严重度：P2，若继续扩大范围可能升级为计划级 P1。**

当前最明确的真实失效是 stale environment/memory，而不是多 Agent 并发写入冲突。Protocol 已覆盖 `stale`、`contradicted`、TTL 和使用前重验，但正文对 Claim 身份、history、幂等和恢复投入了大量篇幅。

这不代表并发设计错误；它代表 v0.1.1 同时试图解决“第一版 freshness MVP”和“成熟的可恢复审计协议”两个不同规模的问题。

建议把交付分层：

1. MVP：项目 Memory 发现、读取、当前事实重验、stale/contradicted 标记、report-only/reconcile 分离、最小 history 证据；
2. 后续能力：`claim_id`、`operation_key`、两阶段恢复、并发冲突和可重建索引；
3. 只有存在第二个真实并发/恢复案例，或用户明确要求跨 Agent 并发一致性时，才把第 2 层作为第一版的硬门槛。

### 3.5 P2-2：文档体量和加载形态

**判定：体量风险成立；“当前已经造成常驻上下文成本”不成立。严重度：P2。**

当前 Protocol 为 739 行、33,978 字节。Claude 官方文档建议单个 `CLAUDE.md` 目标小于 200 行，并建议用 path-scoped rules 或 skills 拆分大规则；同时明确规则/Memory 是上下文，不是强制配置。[Claude Code memory and instructions](https://code.claude.com/docs/en/memory)

Codex 官方文档说明 `AGENTS.md` 指令链默认有 32 KiB 上限，并按目录链拼接。[Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) 但当前 workspace 的 adapter 明确要求只读取 task-shaped owners，Protocol 也尚未安装到 `AGENTS.md`。所以 review 撤回“always-on”说法是正确的；体量仍然是未来安装和遵循度风险。

合理处置不是立即把规范压缩到几十行，而是拆成：

- 短的可执行 routing/operational rule；
- 较完整的 protocol reference；
- 独立 fixture/schema/reference implementation 文档。

只有短规则进入默认路由，详细协议在 memory 任务触发时读取。

### 3.6 P2-3：Reality Ops 应否提前

**判定：部分成立。严重度：P2。**

Reality Ops 是本 program 的真实起点和潜在适配器案例，但当前可见实现仍是另一仓库的 dirty/untracked 候选状态，不能作为已验证基线。把它直接提前成迁移目标会扩大跨仓库风险；把它完全留到 Phase 6 又浪费了早期设计输入。

建议折中：

- Phase 1/2 只做只读 compatibility mapping：把 Reality Ops 现有项目契约映射到 Protocol 的最小字段和触发边界；
- 使用隔离 fixture 或已冻结的文本快照，不修改 Reality Ops；
- Phase 6 仍保留真正迁移，且在 Reality Ops 自己的计划和 Git 基线下执行。

### 3.7 P2-4：文档数量、决策数和审查层级

**判定：过程风险成立，不是技术阻塞。严重度：P2。**

当前目录已有 23 份 Markdown（方向 review 写作时的 22 份是写入自身前的快照），Protocol 739 行，当前 D01–D12 仍为 11 个 `proposed`、1 个 `deferred`，fixture 尚未执行，运行时也未安装。

这表明分析过程已接近“文档递归审查”拐点。下一步不应再增加泛化 review，而应产生：

- 一份明确的方向决策记录；
- 一个最小 freshness fixture；
- 一个 reference harness 或明确的人工执行协议；
- 一份决定哪些并发规范降级为后续能力的范围记录。

## 4. 外部资料核查后的独立判断

官方资料支持以下边界，但没有替本项目决定协议范围：

1. Codex 官方文档要求团队规则放在 `AGENTS.md` 或 checked-in documentation，Memory 只是 helpful recall layer，不能成为必须始终适用规则的唯一来源。[Codex Memories](https://learn.chatgpt.com/docs/customization/memories)
2. Claude 官方文档区分 `CLAUDE.md` instructions 与 auto memory，并明确两者都以 context 形式提供，强制阻断应由 hook/权限机制承担。[Claude Code memory](https://code.claude.com/docs/en/memory)
3. 两者都支持把共享规则/项目事实放在版本控制的项目文档中；这支持当前“项目 Memory 属于项目 Git、host-local memory 不是权威来源”的边界。
4. 官方资料支持“规则 + 执行工具 + 状态存储”的分层，但没有支持“必须把所有 memory 语义压缩成一个规则文件”或“必须由某个特定脚本完成”。

## 5. 建议的下一轮工作顺序

不改变当前未提交工作边界的前提下，建议按以下顺序继续：

1. **方向决策**：确认 v0.1 的交付目标是 freshness MVP，还是同时承诺并发恢复协议；默认建议选择前者。
2. **证据纠正**：在方向证据中把 Reality Ops checker 标成 dirty/untracked supplemental candidate，而不是已落地 CI 基线；补充 W-R24 和对话需求来源。
3. **Phase 1 闸门**：逐条审查 v0.1.1，但增加“执行载体和验收承载”一项，不重写整个协议。
4. **Phase 2 最小 fixture**：先覆盖 stale、contradicted、report-only、reconcile、跨项目边界和未提交修改保护。
5. **参考 harness 决策**：用隔离、可重复的本地 harness 验证 hash/Claim/history 规则；如果这些能力被降级为后续版本，则明确记录，不制造伪通过。
6. **文档收敛**：把长 Protocol 定位为 reference，另外设计短 operational rule；在确认方向后再编辑 `.agents/` 或 allowlist。
7. **Reality Ops**：只在其独立仓库完成自身计划、基线和验证后，讨论迁移或把 checker 作为已发布样例。

## 6. 验证与未决缺口

已执行：

- workspace-meta Git 状态、基线和未跟踪范围检查；
- Reality Ops HEAD、tracked/untracked 对账和工作树状态检查；
- Protocol、Active plan、rule-authoring、feedback-register 和对话需求交叉读取；
- `make test` 先前已通过 28 项；本调查未修改代码，未重复运行它；
- 2026-08-11 核查 Claude Code、Codex Memories、Codex `AGENTS.md` 与 OpenAI Context Personalization 官方资料。

未执行：

- Reality Ops checker 实跑；它当前处于独立仓库 dirty/untracked 状态，且本调查不授权其运行或修改；
- `make bootstrap`、隔离 HOME 双跑和任何 Memory fixture；
- Codex/Claude UI smoke test；
- Reality Ops 远端 freshness fetch；
- Git stage、commit、push、PR 或任何主机/运行时安装。

## 7. 最终 verdict

**原方向 review 的“冻结并改形态”建议过强；其“执行载体、范围比例、来源记录和过程收敛”提醒应采纳。**

当前最稳妥的路线不是继续无限修订 v0.1.1，也不是立即把全部内容压缩成一个规则文件，而是：

> 先用 W-R24 代表的 stale-memory 真实失效定义一个可执行的 freshness MVP；把 Protocol 的完整并发/恢复部分保留为候选 reference，直到 fixture 或真实案例证明它们属于第一版必需范围。

在该方向决策和最小 fixture 产生前，继续保持 Protocol 未安装、Reality Ops 不迁移、Git 不发布的边界。
