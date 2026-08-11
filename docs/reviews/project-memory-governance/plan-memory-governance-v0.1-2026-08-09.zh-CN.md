# Memory Governance Protocol v0.1 后续实施与文档治理计划

Status: Superseded / reference-only；本文是 v0.1 计划历史稿，已由 [v0.1.1 Active plan](plan-memory-governance-v0.1.1-2026-08-09.zh-CN.md) 替代。保留本文用于历史追溯，不得作为当前阶段或实施入口。

Date: 2026-08-09

## 1. 目标和范围

### 1.1 主要目标

1. 形成一个唯一、可识别的 Memory Governance Protocol v0.1 工作来源；
2. 防止后续 AI 把历史方案、旧计划或早期协议草稿误读为当前规则；
3. 把协议草案转化为可审查、可验证、可分阶段实施的工作包；
4. 用 fixture 验证 report-only、reconcile、路径、状态、并发、安全和跨范围边界；
5. 在协议和 fixture 通过后，再决定是否安装到 .agents/rules/memory-protocol.md；
6. 保持 Project、Workspace、Reality Ops 三个所有权边界独立。

### 1.2 本计划范围

包括：

- workspace-meta 内的通用 Memory Governance Protocol v0.1；
- project-memory-governance 目录下的方案、审查、需求和历史文档；
- 后续 fixture、协议安装和适配器工作的边界与验收。

明确排除：

- 不直接修改 Reality Ops 独立仓库；
- 不自动修改 Codex/Claude 主机配置；
- 不自动 stage、commit、push、merge 或创建 PR；
- 不物理删除具有历史证据价值的文档；
- 不把旧方案或旧计划继续当作当前规范执行。

## 2. 当前基线

### 2.1 当前工作来源

当前唯一的协议工作来源是：

- memory-governance-protocol-v0.1-2026-08-08.zh-CN.md

它仍然是 Draft，不是已安装规则。它已经覆盖：

- 作用域和所有权；
- 默认路径和自定义路径处理；
- report-only / reconcile；
- 当前视图最小 Claim 字段；
- session candidate、初始化、合并、TTL 和注入；
- history、operation_key、并发和部分失败；
- 安全和敏感内容处理；
- Project、Workspace、Reality Ops 适配器边界；
- fixture 格式和验收门槛。

### 2.2 当前仓库事实

- workspace-meta 根目录是当前工作区 Git 根；
- workspace/projects 下的项目保持独立 Git 根；
- .gitignore 使用反向白名单；
- project-memory-governance 下的 Markdown 已属于审查产物范围；
- .agents/rules/memory-protocol.md、模板目录和架构目标路径尚未安装；
- 当前工作树包含 .gitignore 修改和多份未跟踪 Memory 文档；
- 本计划和相关文档均为本地、未发布状态。

### 2.3 重要约束

- 历史文档虽然不再适合作为当前规范，仍包含需求、决策和审查溯源；
- 旧文档之间存在相互引用，直接删除会降低复审可追溯性；
- Reality Ops 有独立仓库和已有未提交工作，不能在 workspace-meta 文档整理中顺手修改；
- 真实 AI 行为评测尚未执行，不能把协议中的场景列表写成已通过。

## 3. 文档治理和处置矩阵

### 3.1 状态定义

| 状态 | 含义 | 后续使用方式 |
|---|---|---|
| Active working source | 当前工作优先读取的来源 | 可以作为后续起草和实施输入 |
| Evidence / historical | 历史需求、审查或决策证据 | 仅用于溯源、复核和解释演进 |
| Superseded / reference-only | 已被新协议或新计划替代 | 可查阅背景，不得直接执行 |
| Deprecated / do-not-use | 内容混杂、互相冲突或无当前实施价值 | 只用于历史考证，不得作为设计依据 |

### 3.2 逐文件判定

| 文档 | 判定 | 处理 |
|---|---|---|
| memory-governance-protocol-v0.1-2026-08-08.zh-CN.md | Active working source | 保留为当前 Protocol Draft |
| 本计划 | Active plan | 作为后续阶段和文档处置来源 |
| README.md（本目录索引） | Active navigation | 指向当前来源，阻止误读历史文档 |
| conversation-requirements 英文/中文 | Evidence / historical | 保留用户意图和决策溯源 |
| review-project-workspace-memory 英文/中文 | Evidence / historical | 保留初始阻塞审查证据 |
| analysis-design-memory-governance | Evidence / historical | 保留设计深度分析，不作为协议来源 |
| review-analysis-design-memory-governance | Evidence / historical | 保留对分析报告的复审结果 |
| response-review-analysis-design-memory-governance | Evidence / historical | 保留对复审的响应记录 |
| review-response-review-analysis-design-memory-governance | Evidence / historical | 保留最新独立复审备忘录 |
| design-memory-governance | Superseded / reference-only | 标记已被 Protocol Draft 替代 |
| solution-project-workspace-memory 英文/中文 | Superseded / reference-only | 标记架构前身，不再直接执行 |
| plan-project-workspace-memory 英文/中文 | Superseded / reference-only | 标记已被本计划替代，不再执行旧阶段 |
| memory-plan.md | Deprecated / do-not-use | 标记历史底稿和禁止执行，不删除 |

### 3.3 “没有参考价值”的处理原则

本轮没有哪一份文档可以安全认定为完全没有历史参考价值：

- memory-plan.md 不能作为规范，但保留早期字段、事件和生命周期想法；
- 旧 solution/plan 解释两级所有权模型和最初实施假设；
- 需求和审查文档能解释为什么后续方向发生变化。

因此本轮采用可恢复处理：标记、索引、降级，不物理删除。它们的当前参考价值
很低，但历史证据价值仍然存在。未来若要物理删除，必须单独确认精确文件清单
和溯源替代方案。

## 4. 分阶段执行计划

### Phase 0：文档收敛和来源声明

目标：先解决“读哪一份”，不改变运行时行为。

操作：

1. 创建本目录 README.md 索引；
2. 创建并保留本计划；
3. 为旧 design、solution、plan 和 memory-plan.md 增加状态横幅；
4. 在索引中明确阅读顺序和禁止执行的文档；
5. 检查当前协议、计划和历史文档链接；
6. 保留英文/中文历史配对，不继续扩展双语规范副本。

出口证据：

- 索引存在并列出全部文档；
- 历史/废止文档顶部有明确状态；
- 当前协议和当前计划可从索引直接定位；
- 旧计划不再像当前实施入口。

### Phase 1：Protocol v0.1 定向复审

目标：确认协议内部规则一致，闭合规范层问题。

操作：

1. 逐条复核 D01–D12；
2. 检查当前视图五字段与 history 字段是否一致；
3. 检查初始化五前提与 report-only / reconcile 是否冲突；
4. 检查 operation_key、run_id、event_id、部分失败和恢复流程；
5. 检查自定义路径、多候选、符号链接和 Git 边界；
6. 检查 Memory 的建议性与项目规则、权限、当前用户意图的优先级；
7. 将官方参考、本项目选择、事实和推断分开；
8. 形成 D01–D12 正式决策记录。

出口证据：

- 每个 D ID 有 proposed、accepted、rejected 或 deferred 状态；
- 每项有理由、范围、责任人和验收标准；
- 没有未记录的关键歧义；
- 协议仍标记 Draft，未被误读为已安装规则。

### Phase 2：Fixture 设计和人工评测

目标：把场景变成可重复证据，而不是只保留场景名称。

操作：

1. 为 MGP-01 至 MGP-13 建立隔离 fixture 定义；
2. 固定初始仓库、完整提示词/操作和预期读取范围；
3. 固定允许写入、禁止写入、预期当前视图和 history；
4. 固定 pass、fail、blocked 判据；
5. 记录实际结果、审查人和脱敏证据路径；
6. 优先执行路径歧义、report-only、敏感内容、并发和恢复场景；
7. 不把人工执行结果写成自动化通过；
8. 将失败分类为协议、实现、环境或 fixture 问题。

出口证据：

- 至少一轮人工评测结果落盘；
- 失败场景有修正建议和责任阶段；
- report-only 没有写入目标；
- 并发和部分失败没有静默覆盖；
- 敏感内容没有进入证据或 Memory。

### Phase 3：Canonical Protocol 安装准备

目标：在协议和 fixture 通过后，准备安装到工作区治理层。

前置条件：

- Phase 1 决策状态已明确；
- Phase 2 完成最小场景集；
- 操作者单独授权安装和 allowlist 变更；
- 没有需要先解决的未提交工作冲突。

候选产物：

~~~text
.agents/rules/memory-protocol.md
.agents/templates/project-memory.md
.agents/templates/workspace-memory.md
docs/architecture/memory-governance.md
~~~

操作：

1. 将审查目录中的 Protocol Draft 整理为唯一核心规则；
2. 模板只保留最小当前视图结构，不复制完整协议；
3. 架构文档解释设计，不重复规范全文；
4. 增加精确 .gitignore allowlist；
5. 更新必要 adapter 路由，不覆盖未托管内容；
6. 运行静态解析和现有工作区测试；
7. 将变更与决策记录、fixture 结果关联。

出口证据：

- 目标路径可被 Git 识别并通过 allowlist；
- 核心规则只有一个来源；
- 模板、架构说明和 adapter 没有语义重复；
- make test、脚本语法、Python 编译和 git diff --check 通过；
- 隔离临时 HOME 的 bootstrap 两次结果稳定；
- 未进行 Git 发布。

### Phase 4：单项目最小垂直切片

目标：验证一个项目范围内的发现、读取、候选、reconcile、history 和恢复闭环。

顺序：

1. 先使用隔离 fixture 或临时测试项目；
2. 再选择明确授权的真实项目；
3. 不把 Reality Ops 作为 workspace-meta 本轮自动副作用；
4. 如选择 Reality Ops，必须在其独立 Git 仓库建立独立计划和基线；
5. 只验证项目级 Memory，不刷新 workspace Memory；
6. 保留项目已有未提交修改，不做清理或重写。

出口证据：

- 冷启动发现正确 Memory；
- 普通只读任务不写入；
- reconcile 只写项目范围；
- 当前视图和 history 可恢复；
- 失败时有可见 partial/blocked 结果。

### Phase 5：Workspace Memory 适配器

目标：验证 workspace 项目地图，不复制详细项目事实。

操作：

- 默认手动刷新；
- SessionStart 只报告，不写入；
- workspace 任务声明项目范围；
- Project Memory 由项目仓库拥有；
- workspace history 只记录地图变化和证据摘要；
- 普通项目任务不隐式刷新 workspace。

出口证据：

- workspace 刷新不修改项目详细 Memory；
- 多项目范围必须显式声明；
- 路径和所有权冲突会停止；
- 项目地图与项目事实不重复膨胀。

### Phase 6：Reality Ops 独立迁移

目标：单独处理 Reality Ops Memory 原型、checker 和内容重分类。

前置条件：

- workspace-meta Protocol 已稳定；
- Reality Ops 的 branch、HEAD、dirty state 和未跟踪文件已记录；
- Reality Ops 项目操作者授权其仓库变更；
- 已明确旧内容属于 runbook、项目规则、当前视图或 history 的哪一类。

操作：

1. 在 Reality Ops 仓库内建立独立 migration plan；
2. 保留 Ansible 和项目专用事实；
3. 删除或重分类重复的通用协议文本；
4. 保留 checker 作为项目专用次级门禁；
5. 对 docs/conventions/memory-plan.md 做独立判断；
6. 在项目 history 记录迁移原因、基线和结果；
7. 不把该仓库变更混入 workspace-meta Git 事务。

出口证据：

- 两个 Git 仓库状态分开报告；
- Reality Ops 项目事实未丢失；
- 通用协议只有 workspace-meta 一个来源；
- checker 的责任边界清楚；
- 项目自身测试和脚本检查通过。

### Phase 7：索引和数据库评估

只有在 history 查询、跨项目检索或数据规模产生实际压力时，才评估索引。

触发条件：

- history 规模使人工查找明显困难；
- 跨项目检索成为稳定需求；
- 重复查询成本高于维护索引成本；
- 有明确的重建、失效和验证方案。

在触发前不引入数据库。任何索引必须可从 Markdown current view/history 重建，
不能成为唯一事实源。

## 5. 验收标准

### 5.1 文档治理验收

- 有且只有一个当前 Protocol Draft 入口；
- 当前计划说明下一步、依赖、出口和未授权边界；
- 旧文档顶部状态清楚；
- 旧计划不会被索引为实施入口；
- 历史需求和审查证据仍可追溯；
- 相对链接指向存在文件；
- 没有尾随空白或明显 Markdown 结构错误。

### 5.2 协议验收

- scope、owner、mode、target 和 write permission 可报告；
- report-only 不写 Memory/history；
- reconcile 不越出声明范围；
- 多候选路径和并发冲突会停止；
- Claim 状态和证据等级不会静默升级；
- TTL 不会自动删除或伪造事实；
- history 事件可唯一识别并支持幂等重试；
- partial、failed、recovery 状态可见；
- Memory 不覆盖安全、权限和当前用户意图；
- 秘密和完整 transcript 不进入 Memory/history。

### 5.3 仓库验证

文档或规则变更完成后，按项目要求执行：

~~~bash
make test
bash -n scripts/*.sh .githooks/pre-commit
python3 -m py_compile scripts/*.py tests/*.py
git diff --check
~~~

进入配置安装阶段还必须执行 make bootstrap 和 make agent-sync-check，并在隔离
临时 HOME 中运行 bootstrap 两次，检查第二次托管文件哈希不变。无法执行的检查
必须报告为未执行或 blocked，不能写成通过。

## 6. 风险、回滚和停止条件

| 风险 | 处理 |
|---|---|
| 历史文档继续被当作当前规范 | 目录索引、状态横幅、唯一来源声明 |
| 过早修改运行时规则 | Protocol Draft 与安装阶段分离 |
| 旧方案跨仓库假设进入实现 | Phase 4/6 分离、独立 Git 边界 |
| 删除历史导致无法解释决策 | 本轮只标记和索引，不物理删除 |
| fixture 只测试理想路径 | 优先覆盖歧义、失败、并发、敏感和恢复 |
| 双语文本漂移 | 一个工作来源，译文只作阅读材料 |
| 未提交修改被覆盖 | 写前基线、停止规则、禁止清理命令 |

必须停止并记录问题的情况：

- 当前协议与用户新决策冲突；
- 目标路径越过 Git 所有者边界；
- 多份规范来源无法确定 canonical；
- fixture 结果与协议要求矛盾；
- 需要修改另一个 Git 根目录但没有独立计划；
- 需要新的 Git、主机、外部或 live 授权；
- 需要删除文件但不能证明历史替代链完整。

回滚原则：

- 文档标记错误：恢复原状态并保留处置记录；
- 新计划错误：更新计划并记录 dated deviation；
- Protocol Draft 错误：修订 Draft，不改写旧历史内容；
- 安装错误：只在单独授权下回退安装产物；
- 跨仓库迁移错误：在对应仓库按其恢复流程处理。

## 7. 本轮执行顺序和出口

本轮执行：

1. 创建本目录 README.md 索引；
2. 创建本计划；
3. 为旧 design、solution、plan 和 memory-plan.md 增加历史/废止状态；
4. 验证链接、Markdown 空白和处置清单；
5. 不安装 Protocol、不修改 .agents/、不修改 Reality Ops、不发布 Git。

本轮出口后，下一项工作是 Phase 1 的 Protocol 定向复审和 D01–D12 正式决策记录。
