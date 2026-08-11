# Memory Governance Protocol v0.1.1 后续实施与文档治理计划（Superseded / reference-only）

Status: Superseded / reference-only；本文曾是 v0.1.1 Active plan，现由
`MGP-v0.1.2` 计划取代当前工作来源。本文仍用于追溯历史阶段和出口证据，不等于
运行时实施批准，也不授权 Git 发布、跨仓库迁移、主机修改或项目 Memory 写入。

Superseding source: [v0.1.2 实施与文档治理计划](plan-memory-governance-v0.1.2-2026-08-11.zh-CN.md)

Protocol ID: `MGP-v0.1.1`
Date: 2026-08-09

本文 supersede [v0.1 计划历史稿](plan-memory-governance-v0.1-2026-08-09.zh-CN.md)。
旧计划保留用于追溯，不再作为当前阶段入口。实施阶段编号只在本文维护；Protocol
Draft 不再另行定义一套数字 Phase。

## 1. 目标和范围

### 1.1 本轮目标

1. 形成一个可识别、可复核的 `Memory Governance Protocol v0.1.1` 修订候选稿；
2. 关闭原复审确认的三个 P1：阶段编号冲突、D09 状态语义冲突、`operation_key` 不可推导；
3. 同步关闭直接关联的 `claim_id`、D 表映射、D11 决策边界、时间戳和 fixture 缺口；
4. 保持 Protocol、计划、审查证据和历史文档之间的来源关系清楚；
5. 通过定向复审确认文本已经可作为下一阶段 fixture 设计输入。

### 1.2 范围内

- `project-memory-governance` 目录内的 v0.1.1 Protocol Draft、Active plan、README 和变更记录；
- Protocol 的规范文本、标识符规则、history 规则、D01–D12 映射和最小 fixture 清单；
- 原审查结果中 P1、P2、P3 和报告层问题的文字处置；
- 文档链接、状态横幅、哈希/检查证据和本地验证。

### 1.3 明确排除

- 不安装到 `.agents/rules/memory-protocol.md`；
- 不修改 `.agents/`、hook、SessionStart、主机配置或运行时注入链；
- 不创建、迁移或刷新任何项目/Workspace Memory；
- 不修改 Reality Ops 独立仓库；
- 不自动 stage、commit、push、merge、rebase、reset、clean 或创建 PR；
- 不把 fixture 清单或 Protocol Draft 写成已经执行、通过或生产验证。

## 2. 当前基线和版本关系

### 2.1 当前来源

| 状态 | 文件 | 用途 |
|---|---|---|
| Active working source | `memory-governance-protocol-v0.1.1-2026-08-09.zh-CN.md` | 当前修订候选规范 |
| Active plan | 本文 | 当前阶段、出口、风险和未授权边界 |
| Active navigation | `README.md` | 来源路由和文档索引 |
| Evidence | `review-result-review-protocol-and-plan-memory-governance-v0.1-2026-08-09.zh-CN.md` | 对上一轮审查的独立复审结果 |
| Superseded | `memory-governance-protocol-v0.1-2026-08-08.zh-CN.md` | v0.1 历史候选稿，只作对照 |
| Superseded | `plan-memory-governance-v0.1-2026-08-09.zh-CN.md` | v0.1 历史计划，只作对照 |

### 2.2 当前状态

- v0.1.1 已完成文档级修订，但仍是 Draft；
- 三个 P1 已写入 v0.1.1 候选稿，必须经定向复审后才可关闭；
- D01–D12 尚无操作者签署的正式批准记录，D11 仍为 deferred；
- MGP-01 至 MGP-14 只定义场景，尚未形成实际执行结果；
- Protocol 尚未安装，`.gitignore`、`.agents/`、主机和跨仓库边界未授权改变；
- 工作区保留既有 `.gitignore` 修改和未跟踪文档，不做清理或发布。

### 2.3 版本策略

v0.1.1 是 v0.1 的纠错版本，不是架构扩展版。只要 Protocol 的规范语义、阶段
引用或可执行标识符发生修订，关联计划就同步升为 v0.1.1；旧计划通过状态横幅
降为历史稿，不覆盖、不删除。后续仅有计划排程变化而没有协议语义变化时，可以
在本文记录 dated deviation，不再无条件产生新的协议版本。

## 3. 问题关闭矩阵

| 问题 | v0.1.1 处理 | 关闭条件 |
|---|---|---|
| P1-1 阶段编号冲突 | Protocol §14 只保留生命周期门槛；数字 Phase 由本文 §4 唯一维护 | Protocol 和计划不再出现同名不同义的 Phase |
| P1-2 D09 语义冲突 | 改为「应尽早持久化；写入并验证成功后方可提升为已确认」 | D 表、正文、事件和 fixture 期望状态顺序一致 |
| P1-3 `operation_key` 缺推导 | 固定规范化输入、SHA-256 格式、排除运行实例字段和冲突处理 | 崩溃恢复可重建同键，载荷不一致会停止 |
| P2-1 `claim_id` 不完整 | 固定作用域、ULID、碰撞检查、导入和重试复用规则 | 创建、更新、替代和恢复均能保留身份 |
| P2-2 D 表漂移 | 增加 v0.1→v0.1.1 映射；D11 保持 deferred | 每个变化有来源、处理和状态 |
| P2-3 官方引文定位不足 | 增加定位和 2026-08-08 访问核验日期 | 事实、参考模式和本项目选择可区分 |
| P2-4 历史改写不可验证 | 后续改写记录 SHA-256 和允许变更范围 | 不依赖未经授权的 Git commit 制造基线 |
| P2-5 README 易失效 | 同轮登记新增审查、计划和变更记录 | 目录链接全部可达 |
| P3 时间戳/词汇/符号链接 | 统一时间格式，移除未定义「推荐」，新增 MGP-14 | 文档用词和场景清单一致 |
| R-01 F-01–F-08 汇总失真 | 以明细表为准，不再使用「六项已落实」 | 复审摘要与逐项状态一致 |
| R-02 索引快照过时 | 复核时间点并同步 README | 新增文件不会留下未索引状态 |

## 4. 分阶段执行计划

本节的 Phase 编号是当前唯一实施编号。Protocol §14 只引用本文，不另行重定义。

### Phase 0：版本路由和历史保护

状态：本轮文档修订中完成。

目标：建立 v0.1.1 新来源，保留 v0.1 文件和计划的历史身份。

出口：

- v0.1.1 Protocol、计划和变更记录存在；
- v0.1 Protocol 和旧计划有 superseded 横幅；
- README 的 Active source/plan 指向 v0.1.1；
- 原审查、复审结果和历史方案不被静默改写。

### Phase 1：v0.1.1 Protocol 定向复审

状态：待定向复审。

目标：确认三个 P1 及直接关联问题已经在协议正文、摘要表和场景清单中闭合。

操作：

1. 对照原审查和复审结果逐条核对 P1、P2、P3、R-01、R-02；
2. 验证 Protocol §14 与本文 Phase 编号只有单一解释；
3. 复核 D09 的候选、持久化、验证和确认状态转移；
4. 用固定输入重算 `operation_key`，检查运行 ID、时间戳和基线不进入键；
5. 检查 `claim_id` 的生成、更新、替代、碰撞和崩溃重试语义；
6. 核对 D01–D12 映射、D11 deferred 状态和官方引文定位；
7. 核对统一时间格式、MGP-14、规范词汇和 README 链接；
8. 形成一份只针对 v0.1.1 的定向复审结果。

出口证据：

- 没有未记录的 P1；
- `operation_key` 和 `claim_id` 能由文本实现，不依赖口头约定；
- D11 未被误写成操作者已批准；
- Protocol 仍明确为 Draft，未声称安装或 fixture 通过。

### Phase 2：正式决策记录和 Fixture 修订

目标：把候选规则转化为可审查的 D01–D12 决策记录和 MGP-01 至 MGP-14 fixture。

操作：

- 为每个 D ID 记录 proposed、accepted、rejected 或 deferred、理由、范围、责任人和验收标准；
- 对 D11 单独取得操作者关于规范语言的决定，或保持 deferred；
- 固定 `operation_key` 的规范 JSON 示例和同键冲突样例；
- 固定 `claim_id` 创建、替代和碰撞 fixture；
- 为 MGP-14 补齐符号链接越界的初始仓库、允许写入和停止条件；
- 不把本阶段的定义写成已经执行。

出口证据：

- 每个 D ID 有可追溯状态；
- fixture 有完整输入、预期、判定和脱敏证据格式；
- 失败、blocked 和未执行状态可区分。

### Phase 3：Canonical Protocol 安装准备

前置条件：

- Phase 1 定向复审无开放 P1；
- Phase 2 最小决策记录和场景集已经完成；
- 操作者单独授权安装和 allowlist 变更；
- 没有需要先解决的未提交工作冲突。

本阶段只准备安装方案和检查，不执行 `.agents/`、hook、主机或 `.gitignore` 修改。

出口证据包括：`make bootstrap`、`make agent-sync-check`、隔离临时 HOME 双跑和
托管文件哈希稳定性；无法执行的项目必须标为未执行或 blocked。

### Phase 4：单项目最小垂直切片

获得独立实施授权后，验证一个项目范围内的发现、读取、候选、reconcile、history
和恢复闭环。使用隔离 fixture 优先；不得顺手修改 Reality Ops 或其他 Git 根目录。

### Phase 5：Workspace Memory 适配器

验证手动 workspace 刷新、项目地图边界和 SessionStart 只报告行为。Workspace
Memory 不复制项目详细事实，跨项目范围必须显式声明。

### Phase 6：Reality Ops 独立迁移

在 Reality Ops 自己的 Git 根目录内建立独立计划和基线，单独处理 checker、项目
事实和旧内容重分类，不把其变更混入 workspace-meta。

### Phase 7：索引和数据库评估

只有 history 查询、跨项目检索或规模压力达到触发条件时，才评估可重建索引；
数据库不得成为唯一事实来源。

## 5. 文档处置矩阵

| 文件 | 本轮处置 | 当前状态 |
|---|---|---|
| `memory-governance-protocol-v0.1.1-2026-08-09.zh-CN.md` | 新建并作为唯一候选规范 | Active working source |
| `plan-memory-governance-v0.1.1-2026-08-09.zh-CN.md` | 新建并维护 Phase 编号 | Active plan |
| `memory-governance-protocol-v0.1-2026-08-08.zh-CN.md` | 只增加 superseded 横幅 | Superseded / reference-only |
| `plan-memory-governance-v0.1-2026-08-09.zh-CN.md` | 只增加 superseded 横幅 | Superseded / reference-only |
| `review-protocol-and-plan-memory-governance-v0.1-2026-08-09.zh-CN.md` | 保留原审查，不静默改写 | Evidence / historical |
| `review-result-review-protocol-and-plan-memory-governance-v0.1-2026-08-09.zh-CN.md` | 保留复审结论 | Evidence / historical |
| `README.md` | 更新 Active source、plan 和链接 | Active navigation |
| `changelog-memory-governance-v0.1.1-2026-08-09.zh-CN.md` | 记录本轮变更和验证 | Evidence / historical |

## 6. 验收与验证

### 6.1 文档验收

- 只有 v0.1.1 Protocol 被 README 指向为 Active working source；
- 只有 v0.1.1 plan 被 README 指向为 Active plan；
- 所有相对链接指向现有文件；
- v0.1 历史文件顶部状态清楚，正文未被静默重写；
- Protocol 不再把旧 D09 表述作为规范语义；该表述如保留，只能出现在历史变更映射中；
- `operation_key`、`claim_id`、D11 和 MGP-14 有明确规则或状态；
- 文档没有尾随空白或明显 Markdown 结构错误。

### 6.2 仓库级验证

按 workspace 项目要求执行：

~~~bash
make test
bash -n scripts/*.sh .githooks/pre-commit
python3 -m py_compile scripts/*.py tests/*.py
git diff --check
~~~

本轮不执行 `make bootstrap`、隔离 HOME 双跑或 fixture；它们属于后续 Phase 2/3
出口证据。未执行项不得写成通过。

### 6.3 版本完成定义

v0.1.1 可以被称为「定向复审通过的 Draft」的最低条件：

1. Phase 1 定向复审没有开放 P1；
2. D01–D12 的未决状态和操作者决定边界已落盘；
3. 关联的 P2/P3 和报告层问题已经分类；
4. 文档索引和变更记录完整；
5. 仍明确未安装、未迁移、未执行 fixture 的边界。

只有在后续 fixture、安装审查和独立授权都完成后，才能讨论正式启用，不得把
「v0.1.1 Draft 通过」等同于「运行时已启用」。

## 7. 风险、停止条件和回滚

| 风险 | 处理 |
|---|---|
| v0.1 与 v0.1.1 被混读 | README 路由、旧文件横幅、唯一 Active source |
| Phase 编号再次漂移 | Protocol 不定义数字 Phase，本文是唯一阶段来源 |
| 幂等键因实现差异分叉 | 固定规范化输入、编码、哈希和冲突处理 |
| Claim ID 被重新生成 | 在 prepared/reconcile_attempt 中持久化并在重试复用 |
| D11 被误认为已批准 | 保持 deferred，单独记录操作者决定 |
| 历史证据被覆盖 | 只增加状态横幅，不删除或静默改写正文 |
| 未提交工作被覆盖 | 不清理工作树；写前检查并停止于边界冲突 |

必须停止并记录问题的情况：

- 用户新决定与 v0.1.1 方向冲突；
- 发现需要修改另一个 Git 根目录、主机或 live 目标；
- 规范输入不足以重建同一个 `operation_key`；
- 同一 `claim_id` 或 `operation_key` 出现不可解释碰撞；
- fixture 与协议要求矛盾；
- 需要 Git 发布或新的外部/主机授权。

回滚只针对本地文档：删除新候选稿并恢复 README 路由前，必须先记录原因和精确
文件清单；不得使用 destructive Git 命令，不得删除历史证据作为便利措施。

## 8. 本轮出口

本轮完成：

1. 创建 v0.1.1 Protocol Draft；
2. 创建本文作为对应 Active plan；
3. 将 v0.1 Protocol 和旧计划降级为历史参考；
4. 记录 P1、P2、P3 和报告层问题的处理方式；
5. 更新 README 和本轮 changelog；
6. 完成本地文档和仓库级安全检查，不做 Git 发布。

本轮出口后的下一步是 Phase 1 定向复审；在该复审完成前，v0.1.1 仍是 Draft。
