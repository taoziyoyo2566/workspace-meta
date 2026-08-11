# Historical Memory Plan — Deprecated

Status: Deprecated / do-not-use；历史底稿，仅用于追溯早期需求、字段、事件和生命周期想法。
Current source: memory-governance-protocol-v0.1-2026-08-08.zh-CN.md
Do not execute this document as a protocol or implementation plan.

## 当前应采用的最终模型

  workspace-meta
    ├── 全局 AI 工作协议
    ├── project-memory 规则
    ├── workspace-memory 规则
    ├── 两种模板
    └── SessionStart 状态提醒

  项目仓库
    ├── project-memory.md
    └── project-memory/history/

  workspace-meta 仓库
    ├── workspace-memory.md
    └── workspace-memory/history/

  对应操作：

   操作                      默认作用范围            默认写入
  ━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   普通项目任务              当前项目                当前项目 memory
  ────────────────────────  ──────────────────────  ──────────────────────────────────
   当前项目快速审计          当前项目指定范围        当前项目 memory/history
  ────────────────────────  ──────────────────────  ──────────────────────────────────
   当前项目完整审计          当前项目                当前项目 memory/history
  ────────────────────────  ──────────────────────  ──────────────────────────────────
   刷新 workspace memory     所有项目的概要          workspace memory/history
  ────────────────────────  ──────────────────────  ──────────────────────────────────
   workspace 全量项目审计    多个项目，需明确请求    各项目 memory + workspace memory




• 现状核对完成：workspace-meta 已有全局 Codex 适配器和 SessionStart 状态评估器；Reality Ops 已有项目级 AGENTS.md、docs/project-memory.md 和一个
  按路径触发的门禁脚本。下面的计划会保留这些现有边界，同时把“AI 语义判断”和“workspace 项目总览”拆清楚。

• 下面是一份审查版方案，暂不修改仓库。方案重点是保持两个范围严格分离：

  - 项目级 memory：默认只服务当前项目；
  - workspace 级 memory：只记录 workspace 中有哪些项目及其总体状态。

  ## 一、目标与边界

  ### 目标

  实现一个由 AI 主导的 memory 生命周期：

  1. 新设备使用 workspace-meta 后，AI 能继承统一的 memory 工作协议；
  2. 新建或 clone 项目后，第一次进行实质性 AI 工作时，自动初始化项目 memory；
  3. AI 能对当前项目进行快速或完整审计；
  4. AI 能记录事实、证据、修改原因、时间和结果；
  5. 可以手动刷新 workspace 级项目总览；
  6. 项目 memory 和 workspace memory 都有可追溯历史；
  7. 不通过固定脚本决定项目语义，也不把所有项目事实集中到 workspace-meta。
  ### 非目标

  暂不做：

  - 自动 commit、push 或创建 PR；
  - SessionStart 自动修改项目文件；
  - 一个中心数据库替代各项目 Git 仓库；
  - 自动把所有项目的详细 memory 合并到 workspace-meta；
  - 保存完整聊天记录或原始命令输出；
  - 通过固定脚本推断项目架构或判断 memory 内容是否正确。

  ## 二、整体结构

  建议最终结构如下：

  ~/workspace/
  ├── .agents/
  │   ├── rules/
  │   │   ├── project-memory.md
  │   │   └── workspace-memory.md
  │   └── templates/
  │       ├── project-memory.md
  │       └── workspace-memory.md
  ├── docs/
  │   ├── architecture/
  │   │   └── memory-governance.md
  │   ├── workspace-memory.md
  │   └── workspace-memory/
  │       └── history/
  └── projects/
      └── reality-ops/
          ├── AGENTS.md
          └── docs/
              ├── project-memory.md
              └── project-memory/
                  └── history/

  ### 所有权

   内容                       所有者
  ━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━
   memory 工作协议            workspace-meta
  ─────────────────────────  ─────────────────────
   memory 模板                workspace-meta
  ─────────────────────────  ─────────────────────
   当前 workspace 项目总览    workspace-meta
  ─────────────────────────  ─────────────────────
   当前项目的详细事实         项目自己的 Git 仓库
  ─────────────────────────  ─────────────────────
   项目 memory 历史           项目自己的 Git 仓库
  ─────────────────────────  ─────────────────────
   Codex/Claude 本机配置      当前主机
  ─────────────────────────  ─────────────────────
   项目环境和生产状态         项目自身的事实来源

  workspace-meta 只管理规则、模板和 workspace 总览，不拥有项目内部技术事实。

  ## 三、两种 memory 的职责

  ### 1. 项目级 project-memory.md

  记录当前项目的详细知识：

  # Project Memory

  - Status: active
  - Last reviewed: 2026-08-07
  - Scope: 项目工具链、入口、验证、架构事实和运维约束

  ## Project identity

  ## Working entry points

  ## Toolchain and environment

  ## Verified facts

  ## Known hazards

  ## Unverified or open questions

  ## Recent durable changes

  它应该回答：

  - 这个项目做什么；
  - 如何启动、测试和验证；
  - 关键工具链是什么；
  - 哪些事实已经被确认；
  - 哪些事实可能已经过期；
  - 后续 AI 最容易踩什么坑。
  ### 2. workspace 级 workspace-memory.md

  只记录项目地图和总体进度：

  # Workspace Memory

  - Last reviewed: 2026-08-07
  - Workspace root: `~/workspace`

  ## Projects

  ### reality-ops

  - Path: `projects/reality-ops`
  - Purpose: 运维监控与代理相关项目
  - Lifecycle: active
  - Current phase: toolchain stabilization
  - Current status: Ansible control-node setup completed
  - TODO:
    - 完善 workspace memory integration
    - 验证新设备 bootstrap
  - Project memory: `projects/reality-ops/docs/project-memory.md`
  - Last project review: 2026-08-07
  - Evidence commit: `7e93c01`
  - Risks/blockers: none known

  它不记录：

  - Ansible 的具体版本细节；
  - 每个 role 的实现方式；
  - 生产节点清单；
  - 项目内部所有验证证据；
  - 完整代码审计结论。

  这些应该留在项目 memory 中。

  - 完整代码审计结论。

  这些应该留在项目 memory 中。

  ## 四、AI 的生命周期行为

  ### 场景 A：新设备

  实际流程：

  git clone <workspace-meta> ~/workspace
  cd ~/workspace
  make bootstrap
  make agent-sync-check

  预期效果：

  - workspace-meta 的全局 Codex/Claude 指导被安装；
  - AI 获得统一的 project-memory 和 workspace-memory 工作协议；
  - SessionStart 继续负责 workspace 状态提醒；
  - 不自动修改任何项目 memory。

  当前 workspace-meta 已经通过 /home/saberu/workspace/scripts/bootstrap-local.sh 和全局 Codex adapter 完成大部分基础设施，这一部分只需要增加
  memory 协议路由。

  ### 场景 B：新建或 clone 项目

  AI 在项目中首次执行实质性任务时：

  1. 识别最近的 Git 根目录；
  2. 读取项目已有的 AGENTS.md、CLAUDE.md、README 和运行文档；
  3. 查找已有 memory；
  4. 如果没有 memory：
      - 任务允许修改工作树：创建最小项目 memory；
      - 任务是只读任务：不创建文件，但报告 memory 缺失；

  5. 将没有证据的内容标记为 unverified；
  6. 完成任务前执行一次 memory reconciliation；
  7. 有持久化事实变化则更新，没有则明确说明无需更新。

  这里不使用“是否值得建立 memory”作为逃生条件。第一次实质性写入任务默认应初始化项目 memory。
  ### 场景 C：普通项目任务

  项目任务默认只修改当前项目：

  读取当前 project-memory
  → 调查与本任务相关的事实
  → 执行代码或配置变更
  → 验证结果
  → 判断是否形成新的持久化事实
  → 更新当前项目 memory 和 history

  不会因为项目位于 ~/workspace/projects/ 下，就自动修改 workspace memory。

  ### 场景 D：快速审计

  快速审计由自然语言触发，例如：

  快速审计当前项目的 Ansible memory，只检查 venv、版本和 syntax-check 相关内容。

  AI 应：

  1. 读取对应 memory 章节；
  2. 找出相关 claim；
  3. 选择合适的检查方式；
  4. 只验证指定范围；
  5. 更新对应内容；
  6. 写入一条审计历史；
  7. 报告未检查部分。
  ### 场景 E：完整项目审计

  自然语言触发：

  完整审计当前项目的 project memory。
  重新确认项目入口、工具链、测试方式、关键架构和运维约束，
  并记录审计范围和未覆盖部分。

  AI 应先形成审计范围：

  计划检查：
  - 项目入口
  - 依赖和工具链
  - 测试和验证命令
  - 关键目录
  - 运维/部署入口
  - 当前 memory 中的所有 verified claim

  不检查：
  - 未授权的生产变更
  - 未要求的远端写操作
  - 与项目无关的目录

  完整审计不应声称读过每一行代码，而要明确检查覆盖范围和剩余缺口。

  ### 场景 F：刷新 workspace memory

  这是一个明确不同的 workspace 级操作：

  刷新 workspace memory，只更新项目清单、项目功能、当前阶段、
  TODO、阻塞项和各项目 memory 的最近审计状态。
  不要修改各项目自身的 project-memory。

  AI 应：

  1. 枚举 workspace 下的项目；
  2. 确认项目路径和 Git 状态；
  3. 读取各项目 README、AGENTS 和 project memory；
  4. 形成 workspace 总览；
  5. 更新 ~/workspace/docs/workspace-memory.md；
  6. 写入 workspace 审计历史；
  7. 标记需要进一步项目级审计的项目。

  默认只修改 workspace-meta，不修改项目仓库。

  如果要求“workspace 下所有项目的完整审计”，则应分两阶段：

  第一阶段：生成各项目审计计划
  第二阶段：明确授权后，逐项目执行并分别修改项目 memory
  ## 五、历史记录设计

  不建议把完整历史都塞进当前 memory 文件。

  ### 当前视图

  docs/project-memory.md

  只保留当前仍然有用的信息。

  ### 历史事件

  docs/project-memory/history/2026-08-07-ansible-audit.md

  示例：

  # Audit PM-AUDIT-2026-08-07-001

  - Scope: project
  - Mode: quick
  - Target: Ansible control-node setup
  - Started: 2026-08-07 JST
  - Basis commit: 7e93c01
  - Performed by: Codex

  ## Reason

  确认 venv、Ansible 版本和 syntax-check 仍然有效。

  ## Evidence

  - `./setup --check`
  - `./ansible-playbook deploy --syntax-check`
  ## Result

  - venv 有效；
  - ansible-core 版本符合声明；
  - syntax-check 通过。

  ## Memory changes

  - 更新 `PM-ANSIBLE-001` 的 `Last verified`；
  - 补充 setup 入口说明。

  ## Gaps

  未执行远端真实部署验证。

  历史应记录：

  - 为什么审计；
  - 审计范围；
  - 依据的代码版本；
  - 做了什么调查；
  - 结果是什么；
  - 哪些内容被修改；
  - 哪些内容仍然未知。

  不记录：

  - 完整聊天 transcript；
  - 密码、Token、Vault 内容；
  - 未脱敏的命令输出；
  - 与项目无关的过程噪音。

 预期效果：避免在实现过程中反复改变所有权和路径。

  ### Phase 1：在 workspace-meta 增加通用协议

  预计新增或修改：

  .agents/rules/project-memory.md
  .agents/rules/workspace-memory.md
  .agents/templates/project-memory.md
  .agents/templates/workspace-memory.md
  docs/architecture/memory-governance.md
  .agents/host-templates/codex-AGENTS.md
  CLAUDE.md

  具体内容：

  - 增加 project-memory 触发路由；
  - 增加 workspace-memory 触发路由；
  - 明确任务开始、任务结束和中断恢复行为；
  - 明确项目级和 workspace 级写入边界；
  - 明确 verified、inferred、unverified、stale 等状态；
  - 提供模板，但不提供固定项目扫描脚本。

  预期效果：

  - 新设备执行 make bootstrap 后即可继承协议；
  - 不依赖每个新项目预先存在 AGENTS.md；
  - 不需要让 SessionStart 负责生成 memory。

  验证：

  make agent-sync-check
  make test
  git diff --check
  ### Phase 2：迁移 Reality Ops 项目原型

  修改范围：

  projects/reality-ops/AGENTS.md
  projects/reality-ops/docs/project-memory.md
  projects/reality-ops/docs/project-memory/history/

  具体操作：

  1. 保留 Ansible 和项目专有规则；
  2. 将通用 memory 生命周期改成引用 workspace-meta owner；
  3. 保留当前项目事实；
  4. 为已有 Ansible setup 验证创建第一条历史记录；
  5. 将当前 memory 的事实、证据和 gap 区分开；
  6. 增加项目级 history 目录。

  现有 scripts/check-project-memory.sh 暂不直接删除，但重新定位为：

  > Reality Ops 的项目专用辅助门禁，不是 workspace-meta 的通用 memory 引擎。

  这样可以避免一次迁移影响当前 CI。

  验证：

  bash -n scripts/check-project-memory.sh
  scripts/check-project-memory.sh --working-tree
  git diff --check

  并重新执行现有项目验证：

  ./setup --check
  ./ansible-playbook deploy --syntax-check

  ### Phase 3：实现 AI 驱动的快速/完整审计协议

  第一版不做 CLI，也不把项目检查命令硬编码进 workspace-meta。

  通过统一自然语言任务触发：

  快速审计当前项目 memory，范围是……

  完整审计当前项目 memory，先给出审计范围，再执行。

  workspace-meta 提供审计规则和输出格式，AI 自己决定：

  - 读取哪些文件；
  - 执行哪些检查；
  - 哪些事实需要重新验证；
  - 哪些事实应该降级为 stale 或 unverified。

  预期效果：

  - 项目技术栈变化时不需要修改中央脚本；
  - AI 可以选择适合项目类型的调查方式；
  - 审计结果可以记录完整证据和缺口。

  验证方式：

  准备几个本地 fixture：

  1. 没有 memory 的新项目；
  2. 有过期 claim 的项目；
  3. memory 与代码事实矛盾的项目；
  4. 只读任务；
  5. 有未提交用户修改的项目。

  检查 AI 是否：

  - 正确初始化；
  - 不伪造事实；
  - 只修改指定范围；
  - 保留用户修改；
  - 输出审计范围和缺口；
  - 写入历史记录。
  ### Phase 4：增加 workspace memory

  在 workspace-meta 中新增：

  docs/workspace-memory.md
  docs/workspace-memory/history/

  具体内容：

  - 项目清单；
  - 项目功能；
  - 生命周期；
  - 当前阶段；
  - 当前 TODO；
  - 阻塞项；
  - project memory 链接；
  - 最近审计时间；
  - 基于哪个项目 commit 或文档生成。

  默认更新方式：

  刷新 workspace memory

  不自动触碰各项目 memory。

  验证：

  - 新增项目后能被列出；
  - 删除或归档项目后总览能反映；
  - 项目路径变化能被发现；
  - 项目摘要链接有效；
  - workspace memory 不包含项目内部敏感事实；
  - 重复刷新不会生成重复项目条目。
  ### Phase 5：增加轻量机械保护

  这一阶段只增加不依赖 AI 语义判断的检查：

  - workspace memory 中的项目路径是否存在；
  - project memory 链接是否存在；
  - history 文件是否可读；
  - Markdown 是否有明显损坏；
  - 是否出现明显敏感字段；
  - history 是否使用有效日期和审计 ID。

  不实现：

  - 通过路径列表判断“必须更新哪一段 memory”；
  - 通过脚本判断项目功能；
  - 通过脚本判断 AI 是否正确理解代码；
  - 通过脚本自动生成 memory 内容。

  如果后续确实需要强制审查，应考虑 AI reviewer，而不是继续增加固定脚本。

  ### Phase 6：评估是否需要数据库索引

  第一版采用 Git 可审查的 Markdown history。

  当出现以下问题时，再考虑 SQLite 或其他索引：

  - 项目数量明显增加；
  - history 查询变慢；
  - 需要按项目、阶段、状态、日期统一检索；
  - 需要生成跨项目报表。

  即使引入数据库，也应遵循：

  Markdown/history = 权威来源
  SQLite = 可重建的本地索引

  不能让一个本地数据库成为唯一事实来源，否则新设备 clone 后无法自然恢复。
  ## 七、预期最终效果

  ### 新设备

  clone workspace-meta
  → make bootstrap
  → AI 获得统一 memory 协议
  → 不需要手工复制规则

  ### 新项目

  第一次 AI 实质性工作
  → 自动发现没有 project memory
  → AI 初始化最小 memory
  → 根据实际调查逐步补充

  ### 当前项目任务

  AI 只读取和更新当前项目 memory
  → 不影响其他项目
  → 不自动修改 workspace 总览

  ### 快速审计

  只验证指定章节或 claim
  → 更新当前项目 memory
  → 写入一次历史
  → 报告未检查内容
  ### 完整项目审计

  AI 先确定审计范围
  → 自主选择调查方法
  → 更新项目 memory
  → 写入完整审计历史

  ### workspace 刷新

  读取各项目摘要
  → 更新 workspace-memory.md
  → 记录项目阶段、TODO、阻塞项
  → 不修改项目内部 memory

  ## 八、需要你审查的关键决策

  我建议暂时采用以下默认值：

  1. 项目 memory：docs/project-memory.md；
  2. 项目历史：docs/project-memory/history/；
  3. workspace memory：docs/workspace-memory.md；
  4. workspace 历史：docs/workspace-memory/history/；
  5. 新项目第一次实质性写入任务自动初始化 memory；
  6. 只读任务不自动写文件；
  7. workspace 审计默认只更新 workspace memory；
  8. 项目详细审计必须在项目范围内执行；
  9. 第一版使用 Markdown history，不使用数据库；
  10. 现有 Reality Ops memory 检查脚本暂时保留为项目专用辅助门禁。



只有两种情况可以不写：

  - 当前任务明确是只读任务，且没有得到写入项目的授权；
  - 项目已有其他等价的持久化文档，不需要重复创建。

  否则，AI 应该自动创建默认的 docs/project-memory.md，或者沿用项目已有的 memory 路径。

  初始文件不需要非常完整，但必须真实：

  # Project Memory

  - Status: onboarding
  - Last reviewed: 2026-08-07
  - Scope: 记录后续 AI 工作需要的项目事实和验证证据

  ## Project identity

  待调查。

  ## Working entry points

  待调查。

  ## Toolchain and environment

  待调查。
 ## Verified facts

  暂无。

  ## Unverified or open questions

  - 项目启动方式尚未确认。
  - 项目验证方式尚未确认。

  然后 AI 在当前任务中逐步补充，而不是只生成一堆空标题。

## AI 应该遵循的正式协议

  workspace-meta 提供的规则应该更接近下面这样：

  Project Memory Protocol

  当你在一个 Git 项目中开始实质性工作时：

  1. 识别最近的 Git 根目录和适用的 AGENTS/CLAUDE/README 指导。
  2. 查找项目已有的 memory、运行手册、架构说明和验证入口。
  3. 如果项目没有等价的持久化 memory：
     - 在允许修改工作树时，先初始化最小 memory；
     - 在只读任务中，不创建文件，但必须报告 memory 缺失。
  4. 读取已有 memory，但不得把其中未经验证的内容当作当前事实。
  5. 根据任务范围调查项目，不要求使用预设命令；由你选择合适的检查方式。
  6. 将事实区分为：
     - 已观察并验证；
     - 根据证据推断；
     - 尚未验证；
     - 已失效或需要重新确认。
  7. 完成任务和验证后，必须做一次 memory reconciliation：
     - 有新的持久化项目事实：更新 memory；
     - 没有新的持久化事实：明确记录本次无需更新；
     - 无法确认：记录缺口，不得编造结论。
  8. 在最终交付前，确认 memory 与本次实际变更、命令结果和环境状态没有矛盾。
  9. 如果任务中断，下次恢复时先检查 Git 工作树、已有 memory 和未完成证据，再继续工作。
  10. memory 不能覆盖安全规则、权限边界、项目配置或当前验证结果。

  这里没有规定 AI 必须使用 rg、某个脚本或某种项目结构。规定的是目标、判断标准和交付责任。



  workspace-meta 应该提供的是一套稳定的自然语言规则，例如：

    当你进入一个项目时：

    1. 识别当前项目的 Git 根目录和适用的项目规则。
    2. 查找项目已有的 memory、运行手册、README 和 agent 指导。
    3. 如果没有 memory，判断当前项目是否值得建立持久化项目记忆。
    4. 如果需要，创建一个最小模板，但所有未知内容必须明确标记为
       unverified，不得根据文件名或经验臆测。
    5. 开始工作前，读取已有 memory；对关键事实重新验证。
    6. 完成任务前，判断本次工作是否产生了值得长期保留的项目事实。
    7. 如果产生了，就根据实际证据更新 memory。
    8. 如果没有产生，就不要为了更新时间而修改 memory。
    9. memory 是辅助上下文，不得覆盖安全规则、权限规则和项目真实配置。

    这段规则的重点是“让 AI 做判断”，而不是规定 AI 必须执行某个固定脚本。 请重新深度思考

