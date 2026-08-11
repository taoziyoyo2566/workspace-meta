# Memory Governance Protocol v0.1.2 实施与文档治理计划

Status: Active plan；供操作者审阅。本文是 v0.1.2 文档轮次的唯一阶段来源，
不等于 Protocol 批准，不授权运行时安装、跨仓库迁移、主机修改或 Git 发布。

Protocol ID: `MGP-v0.1.2`
Date: 2026-08-11

## 1. 版本来源和本轮目的

仓库中没有可定位的 `v0.0.1` 文件。本轮的直接前身是：

- `memory-governance-protocol-v0.1.1-2026-08-09.zh-CN.md`：上一份候选规范；
- `plan-memory-governance-v0.1.1-2026-08-09.zh-CN.md`：上一份 Active plan；
- `memory-governance-protocol-v0.1-2026-08-08.zh-CN.md`：更早的历史候选稿。

本轮不伪造 `v0.0.1` 作为基线。若操作者指的是其他未进入当前工作区的文件，
应在后续补充其路径和哈希；在此之前，v0.1.1 是唯一直接版本基线。

v0.1.2 的目的不是继续堆叠完整并发协议，而是把真实发现的 stale-memory 失效
收敛为一个可验证的 freshness MVP，同时保留高级 Claim/history/recovery 设计作为
候选 reference，不提前声称它们已被第一版实现证明必要。

## 2. 目标、范围和非目标

### 2.1 目标

1. 定义项目 Memory 的发现、读取、当前事实重验和 freshness 状态转换；
2. 清楚区分 `report-only` 与 `reconcile`；
3. 规定 stale、contradicted、blocked、partial 和 unchanged 的可见结果；
4. 规定项目 Memory 属于项目 Git，host-local Memory 只能辅助回忆；
5. 形成可执行的 reference harness 和最小 fixture 入口；
6. 记录 W-R24 及项目对话需求作为来源事件和需求证据；
7. 为未来 adapter、SessionStart、hook 和项目迁移保留清晰边界。

### 2.2 本轮范围

- v0.1.2 Protocol Draft；
- v0.1.2 Active plan；
- 完整的 v0.1.1→v0.1.2 变更记录；
- freshness MVP 的决策矩阵、fixture 定义和 reference harness 契约；
- 文档索引、来源映射、版本状态和验证证据。

### 2.3 本轮明确排除

- 不安装 `.agents/rules/memory-protocol.md`；
- 不修改 `.agents/`、CLAUDE/Codex 模板、hook、SessionStart 或主机配置；
- 不创建、迁移或刷新任何真实项目 Memory；
- 不修改、运行或发布 Reality Ops 当前 dirty/untracked 工作树；
- 不把 `claim_id`、`operation_key`、两阶段恢复、多 Agent 并发或数据库作为 MVP 的实现前提；
- 不 stage、commit、push、merge、rebase、reset、clean 或创建 PR。

## 3. 当前证据基线

### 3.1 真实失效

W-R24 记录的失效是：环境事实发生变化后，旧 Memory 没有重验，后续计划继续依赖
过期事实。2026-08-11 的只读核验进一步发现，Reality Ops 已发布的
`docs/project-memory.md@HEAD` 仍记录旧分支和旧时间，落后当前仓库 HEAD 13 个提交。

该事实用于定义 MVP 的 RED 基线；它不授权修改 Reality Ops。

### 3.2 工作树和已发布状态必须分离

Reality Ops 当前的 memory、AGENTS、checker 和 workflow freshness gate 中有未提交或
未跟踪内容。后续所有 compatibility mapping 必须显式标记来源是 `HEAD`、index、
工作树还是外部/live 查询，不能把工作树候选实现描述为已发布能力。

### 3.3 当前 workspace 状态

workspace-meta 当前保留 `.gitignore` 修改和未跟踪的审查资料目录。它们是受保护的
用户工作，不得为制造基线而清理、隐藏或发布。

## 4. v0.1.2 交付阶段

本节的 Phase 编号是本轮唯一实施编号。

### Phase 0：版本路由和证据冻结

状态：已完成（文档层）；fixture、harness 和实施授权仍待后续阶段。

出口：

- v0.1.2 Protocol、plan、changelog 存在；
- v0.1.1 仍保留为历史候选，不被静默改写；
- README 将唯一 Active source/plan 路由到 v0.1.2；
- 变更记录明确 v0.0.1 不存在于当前工作区；
- 已发布、过期、未发布候选三类证据不混写。

### Phase 1：MVP 方向和决策矩阵

状态：已完成（定义层）；实际 fixture 结果尚未执行。

目标：把 freshness MVP 与后续高级能力的边界落盘。

操作：

1. 为 D01–D15 标记 proposed、deferred、superseded 或 future；
2. 把 stale-memory 真实失效、W-R24 和对话需求加入 provenance mapping；
3. 把 Reality Ops 只读 compatibility mapping 设为 supplemental；
4. 定义 MVP fixture 的输入、预期结果、允许写入和停止条件；
5. 明确 reference harness 与未来项目 adapter 的边界。

出口：方向无未记录 P1；MVP 的成功和 blocked 条件可以独立复核。

### Phase 2：Reference harness 和 MVP fixture

状态：待开始。

目标：在隔离目录中执行 freshness MVP，不安装运行时、不触碰真实项目。

最低场景：

- MGP-01：发现并读取项目 Memory；
- MGP-02：Memory 缺失时报告初始化边界；
- MGP-03：当前证据使声明保持 verified；
- MGP-04：当前证据使声明变为 stale；
- MGP-05：当前证据与声明冲突，标记 contradicted 并停止危险写入；
- MGP-06：report-only 不写入；
- MGP-07：reconcile 只写入任务授权范围内的最小变更；
- MGP-08：未提交用户修改、跨项目路径或来源不明时停止；
- MGP-09：Reality Ops HEAD 快照与工作树快照不得混淆；
- MGP-10：高级 Claim/operation/history 规则只作为 reference 检查，不作为 MVP 通过条件。

出口：fixture 有实际结果；失败、blocked、partial、unchanged 和通过可区分；
reference harness 的输入输出契约已记录。

### Phase 3：文档分层和安装准备

前置条件：Phase 1/2 出口完成，且操作者另行授权安装准备。

本阶段只设计：

- 短 operational rule；
- 完整 protocol reference；
- fixture/schema/reference harness 文档。

本阶段不修改 `.agents/`、hook、SessionStart、`.gitignore` 或主机文件。

### Phase 4：单项目 MVP 垂直切片

获得独立实施授权后，选择一个项目边界验证发现、读取、freshness 判断、report-only
和 reconcile。Reality Ops 仍然不是默认写入目标；如作为样例，必须在其自身仓库
冻结基线并独立授权。

### Phase 5：Workspace adapter

仅在项目 MVP 稳定后验证手动 workspace 刷新、项目地图边界和 SessionStart 只报告。

### Phase 6：高级一致性能力评估

只有 fixture 或第二个真实案例证明需要时，才决定是否把 Claim ID、operation key、
两阶段恢复和并发冲突提升为下一版本的硬门槛。

### Phase 7：Reality Ops 独立迁移

在 Reality Ops 自己的仓库内建立独立计划、干净基线和验证证据后，单独处理 checker、
项目事实和历史内容重分类。不得把该仓库的变更混入 workspace-meta。

## 5. v0.1.2 版本完成定义

v0.1.2 可以被称为“freshness MVP Draft”而不是“已启用协议”的最低条件：

1. MVP 目标、非目标和高级能力降级边界已记录；
2. W-R24、对话需求和已发布 stale memory 的证据关系可追溯；
3. MGP-01–MGP-09 有输入、预期、实际结果和脱敏证据格式；
4. reference harness 的执行载体和适配器边界已明确；
5. 文档链接和 changelog 完整；
6. 未安装、未迁移、未发布和未执行项仍明确披露。

## 6. 风险、停止条件和恢复

必须停止并记录：

- 发现用户方向仍要求第一版包含完整并发恢复；
- fixture 与 freshness MVP 语义冲突；
- 需要修改 Reality Ops 或其他 Git 根目录；
- 把工作树候选内容误写成已发布事实；
- 需要 Git 发布、主机安装、外部写入或 live 变更；
- 当前证据不足以区分 stale、contradicted 或 unverified。

文档恢复只允许在保留精确文件清单、原因和哈希证据后进行；不得用 destructive Git
命令制造干净状态。

## 7. 本轮验证

计划要求：

- `git diff --check`；
- 新增 Markdown 相对链接存在性检查；
- 版本/状态横幅一致性检查；
- `make test`（若本轮修改仅为文档，可复用最近结果但必须标明运行日期）；
- 不把 `make bootstrap`、隔离 HOME 双跑、fixture、Reality Ops checker 或 UI smoke
  test 的未执行状态写成通过。
