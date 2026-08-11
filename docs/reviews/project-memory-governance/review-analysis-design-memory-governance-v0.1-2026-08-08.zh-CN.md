# 二次审查结果：Memory Governance Protocol v0.1 设计分析

Status: 已审查；分析报告大部分建议可采纳，但设计仍未达到实施批准状态。

Date: 2026-08-08

本报告作为后续设计和决策的备忘录，不替代被审查的设计文档，也不授权实施、
跨仓库迁移或 Git 发布。

## 1. 审查对象与范围

### 目标仓库

- `/home/saberu/workspace`
- 当前分支：`main`
- 当前比较基线：`a5ce356`

### 主要审查对象

- [`design-memory-governance-v0.1-2026-08-08.zh-CN.md`](design-memory-governance-v0.1-2026-08-08.zh-CN.md)
- [`analysis-design-memory-governance-v0.1-2026-08-08.zh-CN.md`](analysis-design-memory-governance-v0.1-2026-08-08.zh-CN.md)

### 对照资料

- [`memory-plan.md`](memory-plan.md)
- [`conversation-requirements-2026-08-07.md`](conversation-requirements-2026-08-07.md)
- [`solution-project-workspace-memory.md`](solution-project-workspace-memory.md)
- [`plan-project-workspace-memory-2026-08-07.md`](plan-project-workspace-memory-2026-08-07.md)
- [`review-project-workspace-memory-2026-08-08.md`](review-project-workspace-memory-2026-08-08.md)

### 补充核验范围

Reality Ops 是独立 Git 仓库，仅作为分析报告证据的补充范围：

- 根目录：`/home/saberu/workspace/projects/reality-ops`
- HEAD：`7e93c01`
- 当前工作树：存在大量已修改和未跟踪内容

未纳入本次审查：Git 提交、推送、部署、生产状态变更、主机配置写入和真实
运行时 UI 验证。

## 2. 总体结论

这份分析报告是目前文档链中最有价值的一份审查材料，建议作为新协议设计的
主要修订依据。但不能将它的 12 项“批准”直接视为已批准决策，因为 AI 分析
报告只能提出建议，不能替代操作者对路径、写入边界、自动初始化和规范语言的
最终确认。

结论分为三层：

1. **核心方向采纳**：生命周期、轻量当前视图、写入安全、评测闭环、并发和
   跨仓库边界等建议应进入下一版协议。
2. **带条件采纳**：会话暂存、`confidence`、TTL、自动初始化、双语规范和
   适配器适用范围需要转化为明确的项目决策，不能直接照搬。
3. **暂不作为硬规则**：固定行数上限、纯上下文暂存作为唯一安全机制、英文
   作为唯一规范语言等内容需要进一步验证或确认。

因此，当前状态仍然是：

```text
设计基线有效
→ 分析建议大部分采纳
→ 修订正式协议
→ 场景评测
→ 再写实施计划
→ 实施前重新审查
```

## 3. 对分析报告事实的独立核验

### 3.1 `.gitignore` 阻塞实施路径：确认，必须采纳

已独立执行 `git check-ignore --no-index`，确认以下计划路径仍被根目录的 `*`
规则忽略：

- `.agents/rules/memory-protocol.md`；
- `.agents/templates/project-memory.md`；
- `docs/architecture/memory-governance.md`；
- `docs/workspace-memory.md`。

同时确认 `.agents/templates/` 当前不存在。分析报告关于 P1-4 的判断成立。

**决定：强制采纳。** 后续协议实施计划必须把精确 allowlist 和 pre-commit
验证放在同一个变更范围内；没有这一步，协议无法成为可追踪的仓库资产。

### 3.2 Reality Ops 独立 Git 边界：确认，必须采纳

已独立核验 Reality Ops 的 Git 根目录、HEAD 和工作树状态。其
`docs/project-memory.md` 为 279 行，`AGENTS.md` 为 57 行，且存在已修改和
未跟踪文件。分析报告关于独立仓库和当前视图膨胀的事实判断成立。

**决定：强制采纳。** workspace-meta 协议实施与 Reality Ops Memory 重分类
必须拆成两个计划；不得在 workspace-meta 变更中直接改写或清理 Reality Ops
工作树。

### 3.3 Reality Ops Memory 内容混杂：基本确认，采纳重分类方向

Reality Ops 当前 Memory 同时包含工具链事实、运行命令、一次性 rollout 结果、
生产状态、分支快照和历史结果。它确实展示了“当前视图过度膨胀”的实际失败
模式。

**决定：采纳方向，不立即清理。** 后续独立迁移时进行分类：

- 长期项目事实留在当前 Memory；
- 一次性审计或 rollout 结果进入 history；
- 可重复执行的运维命令回到 runbook；
- Git 状态只作为审计快照，不作为长期事实。

任何迁移都必须保留现有未提交工作，不得用“重写 Memory”掩盖用户改动。

### 3.4 官方依据：方向成立，但不能过度扩展

OpenAI 官方 Cookbook 确实给出了结构化状态、会话候选记忆、长期合并、去重、
冲突、过期、安全检查和端到端评测模式：

- [Context Engineering for Personalization - State Management with Long-Term Memory Notes](https://developers.openai.com/cookbook/examples/agents_sdk/context_personalization)

Codex 官方也明确要求把必须长期遵守的团队规则放在 `AGENTS.md` 或已提交文档
中，而不是依赖 Memory：

- [Codex Memories](https://learn.chatgpt.com/docs/customization/memories)

**决定：采纳其原则，不把 Cookbook 当成通用标准。** 分析报告没有发现明显
的官方依据误读，但“固定行数”“英文规范”等属于本项目设计选择，不是官方
规定。

## 4. 分析报告建议的采纳矩阵

| 建议 | 结论 | 处理方式 |
|---|---|---|
| 项目事实归项目仓库，workspace-meta 只管协议和项目地图 | 采纳 | 作为核心所有权原则 |
| 会话暂存、合并、注入和遗忘形成完整生命周期 | 采纳 | 写入正式协议 |
| 当前 Memory 必须保持轻量 | 采纳 | 增加“不得复制 runbook/history”的硬约束 |
| 只给承重声明分配 claim ID | 采纳 | 当前视图轻量，完整元数据放 history |
| 14 字段每次全部落地 | 不采纳 | 拆分最小当前视图字段和完整事件字段 |
| 当前视图设置固定行数上限 | 部分采纳 | 先做尺寸基线和冷启动评测，再确定预算 |
| 会话暂存不建立默认文件 | 部分采纳 | v0.1 不建文件，但必须明确中断时允许丢失候选，不得丢失已确认事实 |
| 只依靠 reconciliation 作为会话恢复安全网 | 不足 | 增加中断恢复规则；长任务未来可引入可选 task journal |
| 删除数值型 `confidence` | 部分采纳 | v0.1 使用状态和证据作为主信号，数值 confidence 仅可选，不能决定权威性 |
| TTL 表示承重使用前重新验证 | 采纳 | 不自动删除，不因时间流逝自动改写事实 |
| 只注入相关 Memory | 部分采纳 | 作为协议目标；不能声称 Codex/Claude 自动完成相关性过滤，先依靠轻量视图和范围路由 |
| 自定义路径由项目声明，AI 发现兜底 | 采纳 | 多候选时停止并报告，不静默合并 |
| report-only / reconcile 双模式 | 采纳 | report-only 不因审计自动改 Memory；用户明确要求保存报告时，报告写入属于独立授权的文档动作 |
| workspace 刷新 v0.1 纯手动 | 采纳 | SessionStart 只报告，不写 Memory |
| Reality Ops checker 保留为项目专用门禁 | 采纳 | 独立仓库内单独维护和验证 |
| Markdown history 作为第一版存储 | 采纳 | 数据库只做未来可重建索引 |
| 并发和多 Agent 写入规则 | 采纳 | 写前重读、冲突检测、事件 ID、禁止静默覆盖 |
| 增加冷启动问答评测 | 采纳 | 作为效用侧北极星指标 |
| 英文作为唯一规范文本 | 部分采纳 | 必须只有一个规范来源；具体语言待操作者确认，中文译文必须标注版本和非规范属性 |
| v0.1 适配器只覆盖 `~/workspace` 项目 | 建议采纳 | 限定范围降低外溢风险，主机全局推广另行决策 |
| 立即删除 Reality Ops 重复草稿 | 不直接采纳 | 先在独立迁移计划中标记废稿，再经项目仓库授权处理 |

## 5. 必须补回设计的关键内容

### 5.1 最小当前视图

下一版协议不应要求每次更新都填写全部字段。当前项目 Memory 的最小承重单元
建议是：

```text
claim_id
claim/content
status
last_verified_at
evidence_reference
```

只有会影响后续行为、工具链选择、权限边界或安全判断的声明才需要稳定
`claim_id`。完整来源、冲突、修订原因、执行者和脱敏状态放进 history 事件。

当前视图应遵循：

- 记录项目事实，不复制操作手册；
- 记录入口和验证方法，但命令细节链接到 runbook；
- 记录当前风险和未决问题；
- 记录最近真正有持久价值的变化；
- 不保存每次任务的过程噪音。

行数预算应通过冷启动评测确定，不能先凭经验规定一个看似精确的数字。

### 5.2 会话暂存的损失语义

v0.1 可以不创建默认的 session 文件，但协议必须明确：

- 候选记忆可以只存在于当前上下文；
- 上下文压缩、中断或会话结束前崩溃可能导致候选记忆丢失；
- 候选记忆丢失不等于已确认项目事实丢失；
- 任务恢复时必须重新读取项目 Memory、Git 工作树和未完成证据；
- 长时间或高价值任务可以选择创建项目专用 task journal，但不作为全局默认。

这比笼统地说“reconciliation 会保证安全”更准确。

### 5.3 初始化和写入边界

建议把“首次实质性任务”定义为：

- 项目范围内的变更、构建、修复；或
- 明确的 Memory 初始化、审计或同步操作。

解释、计划、只读报告和 report-only 审计不自动写入。

自动初始化只能创建一个最小项目 Memory，并且必须满足：

1. 当前项目范围已经确认；
2. 当前任务已有项目文档写入权限；
3. 没有发现等价 Memory；
4. 没有多个候选 Memory；
5. 初始化动作在最终结果中明确报告。

这保留了原始“新项目第一次实质性工作自动建立 Memory”的想法，同时避免把
普通代码任务静默扩大成任意文档写入。

### 5.4 历史事件和并发

正式协议还必须补充：

- `event_id` 的生成规则；
- 文件命名和排序规则；
- 写前重新读取和冲突检测；
- 当前视图更新与 history 追加的原子性边界；
- 多 Agent 同时修改时是停止、重试还是要求人工合并；
- 重复刷新如何保持当前视图幂等；
- history 事件如何避免重复事实而保留审计事件。

在没有这些规则前，不能声称“可追溯历史”已经是可实施能力。

### 5.5 评测必须有执行证据

分析报告正确指出现有设计只有场景名称，还没有可复现验收。下一版必须为每个
fixture 固定：

- 初始仓库状态；
- 完整提示词或操作描述；
- 预期读取范围；
- 允许和禁止的写入；
- 预期 Memory 变化；
- 预期 history 事件；
- 通过/失败判据；
- 实际结果和审查人；
- 脱敏后的证据存放位置。

第一版没有自动 harness 也可以人工执行，但人工评测必须落盘，不能只在聊天中
声称“已测试”。

## 6. 对分析报告中“批准”内容的纠正

分析报告第 7 节使用了“批准”措辞。这里应改读为“建议采纳”或“候选决策”：

- 默认路径仍需要操作者确认；
- 首次自动初始化仍需要确认写入边界；
- 规范语言仍需要确认；
- 适配器是否只覆盖 `~/workspace` 仍需要确认；
- Reality Ops checker 的长期保留仍由独立项目决定。

本次审查可以确认“建议是否合理”，不能替操作者完成这些语义批准。

## 7. 推荐的后续工作顺序

### Phase 0：记录决策，不改实现

建立一份决策记录，将本报告第 4 节矩阵转为：

- accepted；
- accepted with condition；
- deferred；
- rejected。

同时给每个决定分配稳定 ID，避免后续文档再次混合“建议”和“已确认方向”。

### Phase 1：重写唯一规范来源

创建 `.agents/rules/memory-protocol.md`，并补充项目和 workspace 范围规则。
规范应包含本报告第 5 节的最小视图、初始化、会话损失语义、历史并发、评测和
安全边界。

同一变更中补充 `.gitignore` 精确 allowlist，并运行 pre-commit 路径验证。

### Phase 2：建立场景评测材料

先不接入复杂脚本，建立人工可执行 fixture 和结果记录格式。冷启动问答、
Memory 写入、冲突处理、敏感内容阻断和跨范围写入必须有独立结果。

### Phase 3：项目级最小垂直切片

只实现项目 Memory 的发现、最小初始化、候选判断、reconcile、history 和
report-only。先不做 workspace 全量刷新，也不迁移 Reality Ops。

### Phase 4：Workspace Memory

在项目级流程稳定后，实现手动 workspace 刷新，验证其只维护项目地图，不修改
项目 Memory。

### Phase 5：Reality Ops 独立迁移

单独建立 Reality Ops 迁移计划，冻结其 Git 状态和纳入范围；完成当前 Memory
重分类、重复草稿处置和现有 checker 的兼容验证。

### Phase 6：目标性复审

复审只检查本报告列出的 P1/P2 和新增决策，不重新扩大到所有 workspace 或生产
系统。确认协议、适配器、模板、fixture 和项目迁移边界一致后，才进入实施批准。

## 8. 最终采纳结论

应采纳分析报告的核心判断：

1. 最新设计已经是正确的方向，但仍是设计骨架；
2. 当前视图轻量化和 Reality Ops 重分类是关键工程问题；
3. `.gitignore`、跨 Git 边界、路径发现、历史并发和评测证据必须在实施前解决；
4. Memory 的实用效果要用冷启动问答和端到端场景衡量；
5. 旧 `memory-plan.md` 只能作为历史底稿；
6. 不能把 AI 分析报告里的“批准”当作真正的操作者批准。

不应直接采纳的部分：

1. 把纯上下文暂存当成充分的恢复保障；
2. 在没有测量前规定固定行数上限；
3. 未经确认就把英文定为唯一规范语言；
4. 未经独立项目授权就删除 Reality Ops 重复草稿；
5. 把项目设计选择表述成官方最佳实践。

最终状态：

```text
分析报告：建议采纳，带条件
设计 v0.1：作为研究基线保留
正式协议：尚未形成
实施计划：暂缓重写和执行
Reality Ops 迁移：另立计划
Git 发布：未授权、未执行
```
