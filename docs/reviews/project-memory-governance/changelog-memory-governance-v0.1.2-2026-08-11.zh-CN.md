# Memory Governance v0.1.2 变更记录

Status: Draft change record；记录文档轮次和决策边界，不等于 Protocol 批准、安装、
迁移或 Git 发布。

Date: 2026-08-11
Protocol ID: `MGP-v0.1.2`
Direct baseline: `MGP-v0.1.1`

## 1. 版本基线说明

本工作区没有可定位的 `v0.0.1` 协议、计划或变更记录文件。检索到的最近版本是
v0.1、v0.1.1 和本轮 v0.1.2。因此本记录采用以下诚实的比较关系：

- `v0.1.1`：直接前版，作为逐项差异基线；
- `v0.1`：历史参考，用于识别设计演进和既有缺口；
- `v0.0.1`：未找到，不虚构内容、不伪造哈希、不把其他版本重命名为 0.0.1。

如果后续提供了外部保存的 v0.0.1 路径或哈希，本记录应追加补充映射，而不是重写
当前差异。

## 2. 本轮变更摘要

v0.1.2 不是把 v0.1.1 的完整并发设计继续扩张，而是把审查中确认的真实失效收敛
为 freshness MVP：Memory 在被用于规划或写入前，必须绑定来源并重验承重事实；结果
必须区分 `verified`、`stale`、`contradicted`、`unverified`、`blocked`、`partial`
和 `unchanged`；默认 report-only，reconcile 需要明确授权和写后复核。

本轮的关键判断是：对方 review 里关于“Reality Ops 已有能力/已发布基线”的部分不能
直接采信。独立调查和后续响应提出了可验证证据，但仍需把 `HEAD`、工作树、index
和 live 查询分开。v0.1.2 因此记录事实，不把 dirty/untracked 候选内容升级为已发布
实现，也不因证据问题直接修改 Reality Ops。

## 3. 逐项差异记录

| 编号 | v0.1.1 基线 | v0.1.2 变更 | 原因/证据 | 影响 |
|---|---|---|---|---|
| C01 | 协议主要描述通用 Memory 生命周期 | 把 freshness 重验提升为 MVP 主线 | W-R24；已发布 Memory 落后 HEAD 13 个提交 | 首版可先验证最常见失效 |
| C02 | 当前事实和历史事实边界已有原则，但来源层级不够细 | 增加 `published`、`indexed`、`worktree-candidate`、`live-observed`、`unverified` 分层 | 调查/响应核验 Reality Ops 的 HEAD 与工作树分离 | 降低把候选实现误报为已发布能力的风险 |
| C03 | 有 `verified`、`stale` 等状态 | 补充 `contradicted`、`blocked`、`partial`、`unchanged` 的使用边界 | response 调查结果；需要表达检查失败和部分完成 | 报告可区分“旧”“冲突”“没查到”“不能继续” |
| C04 | report/reconcile 边界已提出 | 明确默认 report-only、授权条件、最小写入和写后复核 | stale 状态不应自动触发覆盖 | 避免文档轮次或自动入口改变用户文件 |
| C05 | 默认路径和自定义路径规则存在 | 将候选路径冲突、来源记录、读取时间列为发现输出 | 多项目/多路径是实际歧义来源 | 发现阶段不再直接假定单一路径权威 |
| C06 | 当前视图最小五字段 | 增加来源、验证时间、freshness 结论 | 仅有分支/状态不足以判断是否过期 | 当前视图可以携带最小可复核证据 |
| C07 | history、Claim ID、operation key、两阶段和并发设计较完整 | 明确这些是 deferred/reference，不是 MVP 硬门槛 | 当前尚未有 fixture 或第二案例证明其必要性 | 减少未经验证的首版复杂度，同时保留演进路线 |
| C08 | fixture 方向已在前版出现 | 固定 MGP-01–MGP-10 的场景、输入、预期和停止条件 | 需要把设计争议转为可复核检查 | 后续可独立实现 reference harness |
| C09 | Reality Ops 作为真实案例被讨论 | 改为 supplemental、只读、独立适配器映射 | Reality Ops 当前 HEAD 与工作树不一致，且有 dirty/untracked 路径 | 不把跨仓库候选变更带入 workspace-meta |
| C10 | v0.1.1 是当前 Active working source | v0.1.2 成为唯一 Active working source，v0.1.1 保留 reference-only | 新轮次需要明确路由，避免并行规范 | 降低从旧稿直接实施的风险 |
| C11 | 版本材料以 v0.1.1 为当前轮次 | 明确当前不存在 v0.0.1；记录版本来源缺口 | 防止“参考 0.0.1”被误写成伪造基线 | 后续补证据时可追加而不破坏审计轨迹 |
| C12 | 已有安装边界和未授权声明 | 在新协议、计划、变更记录中重复并细化未执行项 | 文件存在不代表运行时启用 | 防止把文档完成误报为实现完成 |

## 4. 决策 ID 映射

| 决策 | 处理 | 状态 |
|---|---|---|
| D01–D04 | 默认路径、Markdown history、最小创建和自定义路径规则保留 | proposed |
| D05–D07 | Reality Ops 独立适配器、workspace 手动刷新、无数据库 MVP 保留 | proposed |
| D08–D10 | 当前视图扩展证据字段；写后验证保留；confidence/TTL 仅辅助 | proposed |
| D11 | 中文作为本轮工作语言，最终规范语言不在本轮强行决定 | deferred |
| D12 | `~/workspace` 项目边界保留 | proposed |
| D13 | freshness 重验成为本轮中心目标 | proposed |
| D14 | reference harness 和 fixture 成为独立证据层 | proposed |
| D15 | published/worktree/live 证据分层正式加入 | proposed |

这些状态是工作候选状态，不是操作者批准记录。批准、安装和项目迁移需要另外的
授权与验证记录。

## 5. 证据与调查结论

### 5.1 已核实的关键事实

- 当前 workspace-meta 根目录 HEAD 为 `a5ce3561a6691501e13ca51872e9d5f8b8589e59`；
- Reality Ops 的已发布 HEAD 为 `7e93c011c1a1e7c1ddf424a49a509984de438093`；
- Reality Ops `docs/project-memory.md` 在其 HEAD 中的更新时间为 2026-06-23 JST，
  且声明的活动分支为 `fix/monitor-integrity`；
- 最后一次修改该 Memory 的提交为 `3a598092edcb0ddc3d3edfbb99abcaf2760831c4`，
  其后有 13 个提交；
- 当前 Reality Ops 工作树为 `feat/roadmap-2026-08`，存在 17 个 dirty/untracked
  路径；
- 当前工作树中的 `AGENTS.md`、`scripts/check-project-memory.sh` 和 freshness gate
  不能自动视为已经进入其 HEAD。

### 5.2 这些事实支持什么、不支持什么

它们支持“发布的 Memory 可能 stale，必须有使用前 freshness 检查”和“证据来源必须
分层”。它们不支持以下更强结论：Reality Ops 已完成 v0.1.2 迁移、checker 已在发布
基线通过、所有高级并发机制已经必要，或可以直接覆盖其工作树。

### 5.3 网络参考的使用边界

此前查阅的 OpenAI/Codex、Claude Code 官方资料支持以下一般原则：受控项目文件承载
团队规则，本地 Memory 辅助召回；规则文件和 Memory 的职责不同；较长的上下文会带来
遵循成本；结构化状态、工具和 hook 可以作为后续执行层。它们不能替本项目证明某个
路径、状态机或 Reality Ops 实现已经存在，因此只作为设计参考，不作为项目事实来源。

## 6. 文档变更清单

本轮新增：

- `plan-memory-governance-v0.1.2-2026-08-11.zh-CN.md`：唯一 Active plan；
- `memory-governance-protocol-v0.1.2-2026-08-11.zh-CN.md`：唯一 Active Protocol Draft；
- `changelog-memory-governance-v0.1.2-2026-08-11.zh-CN.md`：本文件。

本轮导航调整：

- `README.md` 的“首先阅读”和“当前工作来源”切换到 v0.1.2；
- v0.1.1 计划和协议移动到历史/reference-only 路由；
- README 保留调查、响应和旧版本文档的追溯入口；
- v0.0.1 的缺失被明确记录，不创建虚假占位文件。

本轮不修改历史正文的语义；如果更新 v0.1.1 的状态横幅，仅用于标明它已被 v0.1.2
取代，不改变其原有设计内容。

## 7. 未执行、未授权和延期项

以下事项在本轮明确没有完成，也不能在交付时写成“通过”：

- 没有安装 `.agents/rules/memory-protocol.md`；
- 没有修改 `.agents/`、hook、SessionStart、Codex/Claude 主机配置；
- 没有创建、刷新或迁移真实项目 Memory；
- 没有修改、运行或发布 Reality Ops 当前工作树；
- 没有实际运行 MGP-01–MGP-10 fixture 或 reference harness；
- 没有证明 Claim ID、operation key、两阶段恢复、并发锁或数据库在 MVP 中必要；
- 没有 stage、commit、push、merge、rebase、reset、clean 或创建 PR；
- 没有把未运行的 bootstrap 双跑、UI smoke test 或跨仓库 checker 写成通过。

这些不是遗漏，而是本轮的安全边界和后续阶段入口。

## 8. 后续工作顺序

1. 先审阅本轮 v0.1.2 Protocol、plan 和本 changelog，确认 freshness MVP 的范围；
2. 在隔离目录实现并运行 MGP-01–MGP-10 reference harness；
3. 根据 fixture 结果决定是否需要提升高级一致性能力为下一版本硬门槛；
4. 另行设计短 operational rule、完整 reference 和 adapter 文档分层；
5. 取得独立授权后再选择一个项目做垂直切片；
6. Reality Ops 只有在其自身仓库建立独立计划和干净/冻结基线后才考虑迁移。

若任何一步重新发现来源歧义、用户修改覆盖风险或需要跨仓库/主机写入，应停止并
回到 report-only，而不是把阻塞状态改写为成功。

## 9. 本轮验证记录

本轮文档生成阶段已完成：版本来源核对、Reality Ops HEAD/工作树证据核对，以及新
文件与 README 路由的计划化记录。

以下验证在文档完成后执行并回填：

- Markdown 相对链接存在性；
- `git diff --check`；
- 版本横幅和 README Active 路由一致性；
- 仓库要求的 `make test`、shell/Python 语法检查（若运行）；
- 任何未运行检查都必须保留为未执行，不得借用旧结果冒充本轮通过。

### 9.1 当前文件指纹

以下 SHA-256 是本轮文档完成后工作树文件的指纹，不是 Git 发布对象，也不代表这些
文件已进入提交历史：

| 文件 | SHA-256 |
|---|---|
| `memory-governance-protocol-v0.1.1-2026-08-09.zh-CN.md`（reference-only） | `42adc578fcfe842c771cffae1a1c1d6b859402cdc6ff41ac230a861ec7f021eb` |
| `plan-memory-governance-v0.1.1-2026-08-09.zh-CN.md`（reference-only） | `c3fbb3293e964a9e7cba8d47465ea505a76973be95cd2661e4528917e2082c83` |
| `memory-governance-protocol-v0.1.2-2026-08-11.zh-CN.md` | `9a6b04b9bbd6a9c5052eff32f3919fdd33811853fbc183ff7a3d399dd77f1e0e` |
| `plan-memory-governance-v0.1.2-2026-08-11.zh-CN.md` | `4b88ec9f6a53f00080187fed2b35adefe29f7f47c4bb07bccda87544a35cd3b3` |

如果这四个文件在后续审阅中发生修改，应重新计算并在变更记录中追加新的指纹，
不要把当前指纹误当成远端或提交基线。

## 10. 交付状态

本记录与 v0.1.2 plan/protocol 共同构成当前文档轮次的可审阅资料。它们仍处于
未发布、未安装、未迁移的 Draft 状态；工作树中相关文件保持可 review，后续是否
进入 Git 发布流程由操作者另行决定。
