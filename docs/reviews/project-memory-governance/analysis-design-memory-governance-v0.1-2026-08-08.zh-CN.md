# 设计文档深度分析：Memory Governance Protocol v0.1

状态：分析产物；由 AI 会话产出，供操作者审阅。本文不修改被分析文档，
不是审批记录，也不授权实施。

日期：2026-08-08

分析对象：

- [design-memory-governance-v0.1-2026-08-08.zh-CN.md](design-memory-governance-v0.1-2026-08-08.zh-CN.md)

对照资料：

- [conversation-requirements-2026-08-07.zh-CN.md](conversation-requirements-2026-08-07.zh-CN.md)
- [memory-plan.md](memory-plan.md)
- [solution-project-workspace-memory.zh-CN.md](solution-project-workspace-memory.zh-CN.md)
- [plan-project-workspace-memory-2026-08-07.zh-CN.md](plan-project-workspace-memory-2026-08-07.zh-CN.md)
- [review-project-workspace-memory-2026-08-08.md](review-project-workspace-memory-2026-08-08.md)
- 工作区现状实地核验（见第 9 节）

## 1. 总体结论

这份 v0.1 设计是整个文档链中质量最高的一份：它正确回应了 2026-08-08
审查报告的大部分 P1 阻塞项，把早期草稿缺失的生命周期环节（会话暂存、
合并、冲突优先级、注入防护、评测闭环）补齐了，方向可以确认。但它目前
是一份**设计骨架而非可实施协议**——有 5 个 P1 只解决了一半，还有若干
设计内部未做的关键决定。

真正决定这套机制成败的不是治理条款，而是三个现实问题：

1. **写入摩擦**：记录模型（§5 的 14 字段）如果全量落地，AI 每次更新
   memory 的成本会高到要么跳过更新、要么产生噪音——两者都会杀死这套
   机制。
2. **当前视图膨胀**：唯一真实案例 Reality Ops 的 `project-memory.md`
   已经约 280 行，混入了本应属于 runbook 和 history 的内容，恰好演示了
   设计 §11「当前视图应保持简洁」在没有硬约束时守不住。
3. **实施路径今天仍被 `.gitignore` 忽略**（已用 `git check-ignore`
   复核确认），协议一个字都还写不进仓库。

## 2. 文档脉络与本文档的位置

六份文档构成一条清晰的演化链：

| 文档 | 角色 |
|---|---|
| `conversation-requirements-2026-08-07` | 需求溯源：R1–R12 稳定需求、6 条被否决解释、7 个未决问题 |
| `memory-plan.md` | 历史底稿，混杂需求/方案/多个互相冲突的协议草稿，已被明确降级为「不作为当前规范」 |
| `solution-project-workspace-memory` | 架构方案草案（两级所有权模型首次成形） |
| `plan-project-workspace-memory-2026-08-07` | 7 阶段实施计划草案 |
| `review-project-workspace-memory-2026-08-08` | 阻塞审查：P1-1 至 P1-7，结论是不可批准实施 |
| `design-memory-governance-v0.1`（被分析文档） | 对审查的回应 + 泛化重构：从「项目/工作区 memory 治理」升级为「通用 Memory 管理协议，Ansible 只是案例」 |

被分析文档的自我定位准确：研究基线，下一步派生正式
`Memory Protocol v0.1`，再重写 solution 和 plan。「先协议后实施」的
顺序判断是对的——旧 `memory-plan.md` 确实不能再修补：它内部就有两版
互相矛盾的协议（一版说「判断项目是否值得建立 memory」，另一版说
「第一次实质性写入任务默认初始化」，后者才是用户确认的方向）。

## 3. 设计做对了什么

- **两级所有权模型**（项目事实归项目仓库，workspace-meta 只拥有协议、
  模板和项目地图）解决了「中央数据库」反模式：新机器
  `clone + bootstrap` 即可继承协议，项目 memory 随项目仓库自然迁移，
  且 memory 随分支走——分支上验证的事实留在分支上，这是把 memory 放进
  Git 工作树的隐性优点。
- **生命周期完整**：发现 → 选择性读取 → 候选提取 → 会话暂存 → 合并 →
  注入 → 纠错遗忘，对齐 OpenAI Cookbook 的参考模式（结构化状态、
  会话级候选、长期合并、相关注入），且尊重其「没有普适方案」的警告。
- **Memory 是建议性上下文而非权威**：当前观察可以推翻旧 memory，
  memory 永远不能覆盖安全/权限规则——与 Codex（AGENTS.md 管规则、
  memory 只是回忆辅助）和 Claude Code（持久规则文件与自动记忆分离）的
  官方边界一致，也与需求 3.2「带日期的交接证据，不是事实源」一致。
- **Report-only / Reconcile 双模式**直接消解了审查 P1-3（只读审计与
  写历史自相矛盾）。
- **三阶段安全（写入/合并/注入）**明确把 memory 当作 prompt-injection
  面处理；「拒绝指令形态内容」「不把推断标为已验证」两条尤其关键。
- **评测闭环**（§13 的 10 个场景 + 9 项指标）是早期草稿完全没有的，
  且正确定位为「协议的可理解说明和回归材料」。

## 4. 与审查 P1 的对账

| 审查发现 | 设计 v0.1 的回应 | 状态 |
|---|---|---|
| P1-1 Reality Ops 跨 Git 边界 | Phase 5 独立迁移计划 | 已回应 |
| P1-2 初始化写入边界未定义 | §9 给出「实质性任务」定义框架 | 半开：**适配器适用范围**（仅 `~/workspace/projects` 还是主机全部项目）仍未决 |
| P1-3 只读审计 vs 写历史矛盾 | §8 双模式 | 已解决 |
| P1-4 实施路径被 gitignore 忽略 | 设计文档只字未提 | **仍开放**：经复核，`memory-protocol.md`、`.agents/templates/`、`docs/workspace-memory.md` 等今天仍被 `*` 规则匹配 |
| P1-5 AI 行为验收不可复现 | §13 定义场景记录字段和指标 | 半开：无执行驱动、通过/失败判据、审查人、证据落盘格式 |
| P1-6 已有 memory 身份识别与去重 | §6.1 列了「是否存在多个候选文件」 | 半开：没有规范路径的声明/发现优先级，没有多候选处理规则 |
| P1-7 secret 扫描不能证明安全 | §11–12：历史只存脱敏摘要，不存原始输出 | 基本解决（前提是把「扫描器仅为纵深防御」写进协议正文） |

另外审查的 P2-1（历史事件 ID 方案、文件命名、排序、并发行为）在设计中
仍只有 `event_id` 字段名，没有方案。

## 5. 设计内部的未决张力（审查报告未覆盖）

### 5.1 记录模型的重量是最关键的未做决定

§5 定义了 14 个字段，而唯一真实案例是自由散文 Markdown。设计自己留了
口子（「人类可读视图用 Markdown，稳定元数据用 frontmatter」）但没拍板。
全字段落地 = 写入摩擦过高；纯散文 = `supersedes/conflicts` 链接和状态机
全部落空。建议折中：**当前视图保持轻量**（章节 + 行内状态标签 + 日期 +
证据链接），只给承载关键行为的声明分配 claim ID（`memory-plan.md` 的
历史示例已用 `PM-ANSIBLE-001` 这种形态），完整结构化字段只出现在
history 事件里。

### 5.2 会话暂存层没有载体

§6.4 的候选记忆放在「任务/会话级暂存区」——但它存在哪里？纯上下文内，
会话中断或上下文压缩就丢；落文件，则需要路径、gitignore 处理和清理
规则，设计都没写。建议 v0.1 **接受纯上下文暂存 + 依靠 R6 的收尾
reconciliation（updated/unchanged/blocked）作为安全网**，不引入暂存
文件——候选记忆本该廉价可丢弃，为它建持久化状态管理得不偿失。

### 5.3 `confidence` 数值字段是个陷阱

没有校准方法的数值置信度只会产生伪精确。状态枚举
（verified/inferred/unverified/stale）已经承载了全部可行动的信号。
建议 v0.1 直接删掉或降为可选枚举。

### 5.4 TTL 语义未定义

需求 3.5 明确说过「时间流逝本身不能让 AI 发明事实或改写时间戳」。所以
`valid_until/ttl` 的正确语义应该是「**承载关键行为前必须重新验证**」的
触发器，而不是自动删除/自动改写。这一句需要写进协议，否则 TTL 会被
实现成自动过期清理。

### 5.5 「只注入相关 Memory」靠文件纪律实现，不靠运行时检索

实际注入路径是 AGENTS.md/CLAUDE.md 路由「任务开始先读 memory 文件」
（Reality Ops 现在就是这么做的）。Claude Code/Codex 没有相关性过滤
引擎——§6.6 能否成立，完全取决于当前视图是否够小。这使「当前视图简洁」
从风格建议升级为**协议的承重结构**，建议给出硬约束（当前视图行数预算 +
「memory 指向 runbook，不复制 runbook」的边界规则）。

### 5.6 Reality Ops 原型恰好演示了这个失败模式

其约 280 行 `project-memory.md` 混着四类内容：

- (a) 持久工具链事实（venv、版本、调用规则）——真正的 memory；
- (b) 一次性 rollout 结果（用户订阅缓存清单、DB 删除行数）——应属
  history 事件；
- (c) 运维命令——应属 `docs/operations.md`；该项目 CLAUDE.md 明文要求
  「运维命令见 docs/operations.md，不要在别处重复」，但 memory 在重复；
- (d) 分支/HEAD 快照——价值有限：`git status` 永远比它新，唯一价值是
  「上次会话认为自己留下了什么」的交接对账。

Phase 5 迁移时的内容重分类，工作量和价值都比表面看起来大。

### 5.7 协议草稿已在两个仓库间分叉

Reality Ops 工作树里有一份未跟踪的 `docs/conventions/memory-plan.md`。
两个仓库各有一版协议底稿是漂移隐患，迁移计划里应明确一份为废稿。

### 5.8 双语维护成本

本目录文档均为英中成对。规范性协议若也双语，漂移风险翻倍。现有
`.agents/rules/*.md` 全部是英文——建议协议以英文为唯一规范文本，中文
明确标注为非规范翻译。

### 5.9 并发与多 agent

旧 plan 的风险表里有「多 agent 改同一 memory → 写前重读、历史只追加」，
设计 v0.1 没有继承这条。Codex 和 Claude 同时在一个仓库工作是这个工作区
的真实场景，这条要捡回来。

## 6. 对「用 AI 时更好把握项目情况」目标的评估

设计的重心在治理侧（写入权限、审计、溯源），符合本工作区的严谨文化，
但原始目标在**效用**侧。判断这套机制是否成功的北极星应该是：

> 一个冷启动的 AI 会话，读完当前视图后能否回答——这个项目是什么、
> 怎么跑起来和验证、上次做到哪了、哪里会咬人？

溯源和审计机制的意义是让这四个答案可信，而不是反过来。需要防的失败
模式恰好是治理压倒效用：更新流程太重导致 memory 长期不更新，或更新
出来的是 git 本来就知道的东西。§13 把「Token/context 使用量」列入评测
指标说明设计者意识到了这一点；建议再加一条评测：冷启动问答测试。

## 7. 走向 Protocol v0.1 的决策清单

需求记录遗留 7 问 + 本次分析新增 5 项，共 12 个决定（附建议）：

1. 默认路径 `docs/project-memory.md` / `docs/workspace-memory.md` →
   **批准**（与原型一致）。
2. 第一版 Markdown 历史 → **批准**。
3. 首次可写实质性任务自动初始化 → **批准**，并采用 §9 的定义
   （实质性 = 项目范围内变更/构建/修复或明确 memory 操作；初始化属于
   已授权的最小文档副作用；report-only 永不写）。
4. 自定义路径 → **项目在 AGENTS.md 声明，AI 发现作为兜底**；多候选
   文件时只报告、不静默合并（了结 P1-6）。
5. Reality Ops checker → **保留为项目专用次级门禁**。
6. Workspace 刷新 → **v0.1 纯手动**，SessionStart 报告过期延后。
7. 索引/数据库 → **延后**（Phase 6 触发条件够用）。
8. 记录模型重量 → **轻量当前视图 + 仅承重声明有 ID + 完整结构只在
   history**（见 5.1）。
9. 会话暂存 → **纯上下文 + 收尾 reconciliation 兜底**，不建暂存文件
   （见 5.2）。
10. 删除数值 `confidence`；TTL 语义定为「承重使用前重验」（见 5.3、
    5.4）。
11. 协议规范文本 → **英文单语规范**，中文为非规范翻译（见 5.8）。
12. 适配器适用边界 → 建议**仅 `~/workspace` 边界内项目**（与工作区
    CLAUDE.md 的适用范围声明一致），主机全局推广另行决定（了结 P1-2
    剩余部分）。

## 8. 落地顺序建议

设计的 Phase 0–6 路线合理，具体化为：

1. 把第 7 节 12 项决定记录成本目录的决策记录（decision note）；
2. Phase 1 写 `.agents/rules/memory-protocol.md` + 两个范围补充 +
   模板，**同一变更中必须包含 `.gitignore` 白名单条目**（否则 P1-4
   会在提交时爆发）；协议行文遵循 `rule-authoring.md`（先定所有者、
   适配器只做精简路由），并在 CLAUDE.md/AGENTS.md 路由表加 memory 行；
3. Phase 2 场景评测在没有自动化 harness 的现实下，诚实定义为「人工
   执行 fixture + 逐场景记录提示词/预期/实际/判定，落盘到 round
   changelog」（满足 P1-5）；
4. Reality Ops 迁移严格走独立仓库的独立计划（P1-1），迁移中同步完成
   5.6 的内容重分类和 5.7 的重复草稿清理。

## 9. 已执行的核验

本分析于 2026-08-08 在本机实地核验了以下事实（均为快照）：

- `git check-ignore --no-index -v` 确认 `.agents/rules/memory-protocol.md`、
  `.agents/templates/project-memory.md`、
  `docs/architecture/memory-governance.md`、`docs/workspace-memory.md`
  仍被 `.gitignore:1` 的 `*` 规则匹配；本 review 目录的 `*.md` 已被
  allowlist 覆盖。
- `.agents/` 下现有 `env/`、`host-templates/`、`rules/` 三个目录；
  `templates/` 尚不存在。
- Reality Ops 仓库（独立 Git 根，HEAD `7e93c01`）工作树含已修改的
  `docs/project-memory.md` 及未跟踪的 `AGENTS.md`、`setup`、
  `setup.conf`、`scripts/`、`docs/conventions/memory-plan.md` 等原型
  文件，与审查 P1-1 的描述一致。
- 读取了 Reality Ops 的 `docs/project-memory.md`（约 280 行）与
  `AGENTS.md` 原型全文，作为 5.5、5.6 的证据。

未执行：`make test`、bootstrap、任何 Git 发布或对被分析文档的修改。
本文是本次会话在该目录下唯一新增的文件。
