# Memory Governance Protocol v0.1.2（Draft）

Status: Draft；freshness MVP 候选规范。本文是 v0.1.2 的唯一工作来源，尚未安装到
`.agents/rules/memory-protocol.md`，不构成已启用的运行规则，也不授权项目迁移、
主机配置、hook 修改或 Git 发布。

Protocol ID: `MGP-v0.1.2`
Date: 2026-08-11
Direct predecessor: `MGP-v0.1.1`

当前工作区没有可定位的 v0.0.1 资料。因此本文以 v0.1.1 作为直接基线，以 v0.1
作为历史参考，不伪造一个不存在的版本。完整的差异、证据和未执行项见
[v0.1.2 变更记录](changelog-memory-governance-v0.1.2-2026-08-11.zh-CN.md)。

## 0. 文档定位和规范语言

### 0.1 本轮要解决的问题

W-R24 暴露了一个具体失效：环境事实发生变化后，旧 Memory 没有在使用前重验，
后续计划继续依赖过期事实。2026-08-11 对 Reality Ops 的只读核验又确认，已发布
的 `docs/project-memory.md@HEAD` 仍记录旧分支和旧更新时间，落后当前仓库 HEAD
13 个提交；当前工作树中的候选 checker 和规则不能被描述为已发布能力。

因此 v0.1.2 先解决“能否发现、读取、重验并明确报告 freshness”，而不是把完整的
历史合并、并发恢复和数据库索引一次性写成 MVP 的必要条件。

### 0.2 规范词汇

- **必须**：MVP 合规实现不得省略；
- **不得**：MVP 明确禁止；
- **应**：默认要求，偏离时必须在结果中说明理由；
- **可以**：允许但不是要求；
- **候选**：本文中的设计输入，不等于操作者批准或已安装能力；
- **已发布证据**：来自 Git `HEAD`、明确的 index 或其他可复核的正式来源；
- **工作树证据**：来自未提交、未跟踪或本地修改内容；只能标记为候选/工作树；
- **live 证据**：来自当前环境、远端服务或运行时查询；必须记录查询时间和范围。

### 0.3 权威和安全边界

Memory 是辅助上下文，不是系统规则、权限凭证、项目事实的唯一来源或强制执行层。
Memory 不得：

- 授予 AI 原本没有的文件、网络、主机或 Git 权限；
- 覆盖安全规则、操作者授权、项目 `AGENTS.md` 规则或当前用户意图；
- 把历史推断、工作树候选内容或未验证的 live 结果伪装成当前事实；
- 作为执行高风险操作的唯一依据。

真正需要无条件阻断的行为必须由权限系统、hook、脚本或其他机械门禁负责。本协议
只规定 Memory 的发现、freshness 判断、报告和受控写入边界。

### 0.4 与运行时的关系

本稿保存于审查目录，不会因为文件存在就自动加载到 Codex、Claude Code 或其他
运行时。host-local Memory 可以帮助召回上下文，但团队必须把承重规则放在项目
Git 中的 `AGENTS.md`、项目文档或其他受控来源；不能以本地 Memory 代替它们。

## 1. 设计依据和版本范围

### 1.1 本轮来源

- [v0.1.2 实施与文档治理计划](plan-memory-governance-v0.1.2-2026-08-11.zh-CN.md)；
- [v0.1.2 变更记录](changelog-memory-governance-v0.1.2-2026-08-11.zh-CN.md)；
- [对独立调查的响应](response-investigation-direction-memory-governance-2026-08-11.zh-CN.md)；
- [方向审查的独立调查](investigation-direction-memory-governance-2026-08-11.zh-CN.md)；
- [W-R24 和历史决策记录](conversation-requirements-2026-08-07.zh-CN.md)；
- [v0.1.1 协议草案](memory-governance-protocol-v0.1.1-2026-08-09.zh-CN.md)。

官方文档只提供参考模式，不自动批准本项目的实现。此前核查过的参考包括
[Codex Memories](https://learn.chatgpt.com/docs/customization/memories)、
[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、
[Claude Code Memory](https://code.claude.com/docs/en/memory) 和
[OpenAI Agents SDK context personalization](https://developers.openai.com/cookbook/examples/agents_sdk/context_personalization)。

### 1.2 版本关系

| 版本 | 关系 | 处理方式 |
|---|---|---|
| v0.0.1 | 当前工作区未找到 | 不伪造；如未来提供路径和哈希，再补做映射 |
| v0.1 | 历史候选 | 仅用于理解早期模型和被发现的缺口 |
| v0.1.1 | 直接前版 | 作为本轮差异基线，保留为 reference-only |
| v0.1.2 | 当前轮次 | freshness MVP Draft，等待独立评审和批准 |

### 1.3 MVP 的承诺

v0.1.2 只承诺一个可验证的最小闭环：

`发现 → 读取 → 绑定来源 → 使用前重验 → 分类 → report-only 或受控 reconcile → 写后复核`

它不承诺自动刷新所有项目、自动纠正所有历史、跨 Agent 并发安全、无冲突合并或
数据库查询性能。

## 2. 对象、来源和状态

### 2.1 Memory 对象

默认项目 Memory 路径为 `docs/project-memory.md`，workspace Memory 路径为
`docs/workspace-memory.md`。项目可以在受控项目规则中声明自定义路径；发现多个
候选且无法确定权威对象时，必须停止写入并报告。

Memory 至少应能表达以下当前视图字段：

1. 当前分支或工作上下文；
2. 最近一次可验证的更新时间或提交锚点；
3. 当前项目/任务状态；
4. 下一步或阻塞项；
5. 来源、验证时间和 freshness 结论。

完整事件、旧事实和替代关系可以保留在同一 Markdown 文件的 history 区域或独立
的 Git 可读 history 文件中。数据库和不可重建索引不属于 MVP 要求。

### 2.2 证据来源分层

每条承重事实都必须能够回答“从哪里来、何时查到、是否已发布”：

| 来源 | 允许的默认结论 | 说明 |
|---|---|---|
| `HEAD` 或明确 commit | published | 可进入报告的已发布基线 |
| Git index | indexed | 只有明确知道 index 状态时使用 |
| 工作树/未跟踪文件 | worktree-candidate | 不得升级为 published |
| 外部/live 查询 | live-observed | 记录时间、范围和查询失败情况 |
| 口述、旧 Memory、未定位引用 | unverified | 只能作为待核验线索 |

来源不清时，状态至少为 `unverified`，不得作为高风险操作的唯一依据。

### 2.3 MVP 状态

- `verified`：当前证据与 Memory 声明相符，且来源和检查时间可复核；
- `stale`：声明曾经可信，但超过 freshness 条件或锚点已经落后；
- `contradicted`：当前证据直接否定声明；
- `unverified`：找不到足够来源或无法完成检查；
- `blocked`：因权限、歧义、脏工作树、来源冲突或安全边界而不能继续；
- `partial`：部分对象完成检查，部分对象失败或未覆盖；
- `unchanged`：reconcile 后没有实际变化，仍需记录复核结果；
- `superseded`：该声明被新的、可追溯声明替代，不等于被物理删除。

`stale` 不等同于 `contradicted`：前者表示需要重新确认，后者表示已有证据冲突。
不能区分两者时使用 `unverified` 或 `blocked`，并说明缺口。

## 3. Freshness MVP 生命周期

### 3.1 发现和读取

实现必须先确定项目边界、候选 Memory 路径和读取来源，再读取正文。不得因为某个
路径惯例存在，就跳过自定义路径、多个候选或项目规则的检查。

发现结果至少记录：项目根、候选路径、来源层级、读取时间、文件是否存在、是否有
未提交修改，以及是否存在冲突候选。

### 3.2 使用前重验

在 Memory 被用于任务规划、环境判断、写入决策或高风险操作前，必须重新检查承重
事实的最小证据集。最小证据集由适配器声明，但不得少于：

- 当前项目根和目标路径；
- 当前 Git 分支/HEAD（适用时）；
- Memory 中声称的时间或提交锚点（适用时）；
- 影响当前任务的工作树/索引状态；
- 声明的直接来源是否仍可读取。

对非 Git 项目，应使用项目自身可复核的版本、状态或 live 查询锚点，并把缺失项记为
`unverified`，不能虚构 Git 证据。

### 3.3 分类规则

1. 证据与声明相符：`verified`；
2. 声明有明确历史锚点但锚点落后：`stale`；
3. 当前证据与声明互斥：`contradicted`；
4. 来源缺失、检查失败或范围不明：`unverified`；
5. 发现必须停止的权限/歧义/用户修改冲突：`blocked`；
6. 多对象结果不一致：整体报告 `partial`，逐对象保留原状态。

只要出现 `contradicted`、`blocked` 或未解决的多个候选，默认停止 reconcile；允许
完成 report-only，但不得把报告写成已修复。

### 3.4 报告与 reconcile

默认操作是 `report-only`：读取并报告，不修改 Memory、项目代码、规则、hook 或
主机配置。报告至少包括：

- 检查对象和范围；
- 声明值、当前证据、来源和检查时间；
- 状态及置信边界；
- 是否存在用户未提交修改；
- 建议动作、停止原因和未检查项。

只有操作者明确授权 `reconcile`，且满足以下条件时，才允许最小写入：

- 目标路径唯一且属于授权项目；
- 当前 Memory 可读，或已明确授权创建最小文件；
- 没有未解决的 `contradicted`、候选路径冲突或用户修改覆盖风险；
- 写入内容仅修正已确认事实，不擅自改写历史或扩展范围；
- 写入后立即重新读取并复核；
- 失败时报告 `partial`/`blocked`，不声称成功。

### 3.5 写后复核

所有 reconcile 都必须产生“写前状态、写入范围、写后读取、最终状态”的记录。写入
并不自动使声明变为 `verified`；只有写后证据与声明相符，才可标记 `verified`。
若只完成部分文件，使用 `partial`，并列出剩余对象。

## 4. 历史、遗忘和安全边界

### 4.1 历史最小要求

MVP 只要求历史可在 Git 中读取、可追溯且不伪造来源。每次 reconcile 至少记录：

- 发生时间；
- 操作类型（create/update/report-only）；
- 变更对象；
- 旧状态和新状态；
- 证据来源/锚点；
- 结果（verified、unchanged、partial 或 blocked）；
- 失败或停止原因。

历史可以是 Markdown 表格、事件段落或项目现有的等价格式。不得要求数据库才能
通过 MVP。

### 4.2 遗忘和替代

旧声明不得因“看起来过时”而静默删除。应标记 `stale` 或 `superseded`，保留替代
关系和来源。删除、压缩或重写历史需要独立授权和可恢复证据。

### 4.3 敏感信息

Memory 和报告不得保存密码、私钥、访问令牌、cookie、完整授权头或可恢复秘密。需要
引用秘密时只记录安全存储位置或脱敏标识。发现疑似秘密时停止扩散并走项目既有的
秘密处置流程。

## 5. Reference harness 和适配器边界

### 5.1 Harness 契约

reference harness 应在隔离目录运行，输入至少包括：

- fixture 项目根和 Memory 文件；
- 声明的来源锚点；
- 当前模拟 Git/文件状态；
- 操作模式（`report-only` 或明确授权的 `reconcile`）；
- 预期结果和允许的写入范围。

输出至少包括：状态、证据摘要、来源层级、变更摘要、停止原因、检查未覆盖项和
可复核的脱敏日志。Harness 通过失败不应修改真实项目、workspace-meta、主机配置
或运行时安装目录。

### 5.2 最小 fixture

| ID | 场景 | 预期 |
|---|---|---|
| MGP-01 | 发现并读取唯一项目 Memory | 读取成功，来源明确 |
| MGP-02 | Memory 缺失 | 报告初始化边界，不擅自创建 |
| MGP-03 | 证据与声明相符 | `verified` |
| MGP-04 | 声明锚点落后 | `stale` |
| MGP-05 | 当前证据否定声明 | `contradicted`，停止危险写入 |
| MGP-06 | `report-only` | 不产生文件变化 |
| MGP-07 | 授权 `reconcile` | 只写允许范围，写后复核 |
| MGP-08 | 用户未提交修改/多候选 | `blocked`，不覆盖 |
| MGP-09 | HEAD 与工作树不一致 | 分层报告，不混写为 published |
| MGP-10 | 高级 Claim/history 规则 | 仅 reference 检查，不成为 MVP 门槛 |

MGP-10 是边界测试，不要求实现 Claim ID、operation key、两阶段恢复或并发协调器。

## 6. 项目适配和 Reality Ops 映射

### 6.1 通用协议和项目适配器

通用协议负责对象、状态、证据层级、report/reconcile 契约和写后复核。项目适配器
负责路径、项目特有检查、状态字段映射和项目内验证命令。适配器不得改变通用安全
边界，也不得把工作树候选实现提升为已发布能力。

### 6.2 Reality Ops 当前只读映射

Reality Ops 可作为独立项目适配器的验证对象，但当前证据必须标注：

- `docs/project-memory.md@HEAD` 是已发布快照；
- 当前 `feat/roadmap-2026-08` 和 17 个 dirty/untracked 路径是工作树状态；
- `AGENTS.md`、`scripts/check-project-memory.sh` 和 freshness gate 若未在 HEAD，
  只能称为候选工作树实现；
- 不得在本仓库的 v0.1.2 文档轮次直接修改或发布 Reality Ops。

这项映射用于防止证据混淆，不等同于 Reality Ops 已完成迁移或 checker 已通过。

## 7. 高级能力：明确延期而非 MVP 硬要求

以下内容保留在 v0.1.1 及后续设计中，v0.1.2 不将其作为第一版通过条件：

- 稳定 `claim_id` 及其生命周期；
- `operation_key` 去重和幂等写入；
- history 两阶段提交、恢复和崩溃窗口处理；
- 多 Agent 并发锁、冲突合并和租约；
- 数据库/索引、查询性能和大规模压缩；
- 全自动 SessionStart 注入、hook 强制门禁和跨项目批量迁移。

如果 fixture 或第二个真实项目证明 freshness MVP 无法在这些能力缺失时保持安全，
应新增决策记录并提升到下一版本；不能在 v0.1.2 轮次中无证据扩大硬要求。

## 8. 工作决策映射

| ID | v0.1.2 处理 | 状态 |
|---|---|---|
| D01 | 保留默认项目/workspace 路径和多候选停止规则 | proposed |
| D02 | 保留 Git 可读 Markdown history 的 MVP 约束 | proposed |
| D03 | 保留“授权且满足前提后才可创建最小 Memory” | proposed |
| D04 | 保留自定义路径声明和歧义停止 | proposed |
| D05 | Reality Ops checker 继续属于独立适配器 | proposed |
| D06 | workspace Memory 继续手动刷新；自动入口只报告 | proposed |
| D07 | 继续不引入数据库/不可重建索引 | proposed |
| D08 | 扩展当前视图最小字段，加入来源/验证时间/freshness | proposed |
| D09 | 保留写入后重新读取并验证 | proposed |
| D10 | `confidence`/TTL 继续只能辅助触发重验，不能替代证据 | proposed |
| D11 | 中文继续作为本轮工作语言，最终规范语言仍 deferred | deferred |
| D12 | workspace 适配器继续限于 `~/workspace` 边界 | proposed |
| D13 | 将 freshness 重验提升为本轮 MVP 主目标 | proposed |
| D14 | 增加 reference harness 和 fixture 作为独立证据层 | proposed |
| D15 | 增加 published/worktree/live 证据分层，修正当前 review 的证据混淆风险 | proposed |

上述状态仍是候选状态，不表示操作者已经批准安装或实施。

## 9. 安装、迁移和完成条件

### 9.1 安装前提

至少完成 v0.1.2 计划中的 Phase 1 和 Phase 2，并由操作者单独授权，才可设计安装
材料。安装时应把短 operational rule、完整 protocol reference 和 fixture/harness
文档分层；不得把整份审查文档直接注入运行时。

### 9.2 迁移前提

项目迁移必须有项目自己的计划、干净或明确冻结的基线、授权范围和独立验证。任何
项目当前的未提交/未跟踪内容必须先被识别，不能被 v0.1.2 文档轮次覆盖。

### 9.3 v0.1.2 Draft 完成定义

本轮文档可以称为完整的 freshness MVP Draft，当且仅当：

1. 目标、非目标、状态和证据层级已写清；
2. W-R24、调查响应和 stale-memory 证据关系可追溯；
3. MGP-01–MGP-10 的输入、预期和停止条件已定义；
4. reference harness、项目适配器和 Reality Ops 的边界已写清；
5. 变更记录列出新增、保留、延期、未执行和未授权项；
6. README 唯一路由到 v0.1.2，Git 状态仍明确未发布。

截至本文创建时，v0.1.2 仍是 Draft；fixture 实际执行、运行时安装、项目迁移、
bootstrap 双跑和 Git 发布均不因本文存在而视为完成。
