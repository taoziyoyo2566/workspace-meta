# Memory Governance Protocol v0.1 设计方案

Status: 研究基线与设计草案；未授权实施，也不是已批准的最终协议。

Date: 2026-08-08

处置状态：Superseded / reference-only；本文设计基线已由 memory-governance-protocol-v0.1-2026-08-08.zh-CN.md 替代。
本文保留用于解释协议演进，不作为当前规范或实施计划。

## 1. 文档定位

本方案设计的是一套通用型 AI Memory 管理机制。Ansible 只是第一个真实案例，
用于验证记忆写入、证据保存、过期识别、冲突处理和审计闭环；它不应成为协议
的领域核心。

本方案基于：

- 当前项目的需求记录、解决方案和实施计划；
- 对现有 `memory-plan.md` 的审查；
- OpenAI 官方 Memory 参考实现；
- Codex 和 Claude Code 官方关于持久规则与记忆边界的说明。

官方资料提供的是参考模式，不是适用于所有项目的统一标准。最终协议仍需由
本项目根据项目事实、权限边界和评测结果确定。

## 2. 官方参考依据

OpenAI 官方 Cookbook 的长期记忆示例采用“结构化状态、会话级候选记忆、长期
合并、相关注入”的生命周期，并明确要求处理去重、冲突、过期、禁止凭空创造
事实、敏感信息和端到端评测：

- [Context Engineering for Personalization - State Management with Long-Term Memory Notes](https://developers.openai.com/cookbook/examples/agents_sdk/context_personalization)

该示例还明确指出 Memory 没有一套适用于所有场景的方案；记忆结构必须由任务
决定。因此本项目借鉴其生命周期和安全原则，不直接复制旅行助手的领域模型。

Codex 官方区分持久项目指导与 Memory：必须长期遵守的团队规则应放在
`AGENTS.md` 或已提交文档中，Memory 只能作为辅助回忆层：

- [Codex Memories](https://learn.chatgpt.com/docs/customization/memories)
- [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

Claude Code 官方也将持久规则文件与自动记忆区分，并指出记忆内容属于上下文，
不是硬性执行层：

- [How Claude remembers your project](https://code.claude.com/docs/en/memory)

## 3. 设计目标

本机制应实现：

1. AI 能在不同项目和不同会话之间继承有用的上下文；
2. AI 能区分临时信息、项目长期事实和 workspace 摘要；
3. Memory 的每次持久化变化都有来源、证据、时间和结果；
4. 过期、重复、冲突和错误记忆可以被发现和修正；
5. 当前用户意图和当前验证结果不会被旧 Memory 覆盖；
6. 项目事实仍由项目自己的 Git 仓库拥有；
7. workspace-meta 只拥有协议、模板和 workspace 项目地图；
8. 不依赖固定脚本理解所有项目的语义；
9. 不把完整聊天记录、原始命令输出或秘密写入 Memory；
10. 通过场景和评测持续验证 Memory 的实际效果。

## 4. 记忆分层与所有权

| 层级 | 所有者 | 作用 | 默认是否注入 |
|---|---|---|---|
| 协议层 | workspace-meta | 规定 AI 如何管理 Memory | 注入精简规则 |
| 任务/会话层 | AI 运行时 | 保存本次任务中的临时信息和候选记忆 | 仅注入相关内容 |
| 项目 Memory | 项目自己的 Git 仓库 | 保存项目长期事实、入口、约束和风险 | 按任务注入 |
| Workspace Memory | workspace-meta | 保存项目地图、阶段、状态、TODO 和阻塞项 | 仅 workspace 任务注入 |
| 历史证据 | 对应 Memory 所有者 | 记录记忆为何变化以及依据是什么 | 默认不全部注入 |
| 主机本地 Memory | Codex/Claude 主机 | 提供辅助回忆 | 不能作为唯一规则来源 |

核心关系：

```text
协议决定“如何管理记忆”
项目仓库决定“项目事实是什么”
历史记录说明“事实为什么变化”
当前观察结果可以推翻过期记忆
```

## 5. Memory 记录模型

每条可持久化记忆至少应能表达以下字段：

```text
memory_id
scope                  # session / project / workspace
kind                   # fact / preference / constraint / hazard / decision / todo
content
status                 # candidate / verified / inferred / unverified / stale / superseded
source                 # user / file / command / tool / human_review / inference
evidence               # 文件、提交、测试或脱敏证据
observed_at
last_verified_at
valid_until / ttl
confidence
supersedes / conflicts
owner
sensitivity
```

状态含义：

- `candidate`：从当前任务中提取、尚未合并的候选记忆；
- `verified`：有明确证据确认；
- `inferred`：AI 推断但没有直接证据；
- `unverified`：目前无法确认；
- `stale`：过去可能成立，但需要重新验证；
- `superseded`：已经被新内容替代。

对于人类可读的当前视图，可以使用 Markdown；对于需要稳定处理的元数据，
可以使用 YAML frontmatter 或等价的结构化字段。表达形式不能改变所有权和
证据要求。

## 6. Memory 生命周期

### 6.1 发现

开始项目任务时，AI 应确认：

- 当前 Git 根目录和项目边界；
- 当前任务的作用范围和写入权限；
- 适用的 Agent 规则；
- 已有项目 Memory 和运行文档；
- 当前项目实际状态；
- 是否存在多个候选 Memory 文件。

### 6.2 读取与选择

AI 只加载与当前任务相关的 Memory，不把整个 workspace、全部项目历史和全部
聊天内容塞入上下文。

Memory 默认是辅助上下文，不是绝对事实。当前项目的实际观察结果必须能够
标记旧 Memory 为 `stale`、`superseded` 或 `contradicted`。

### 6.3 候选记忆提取

只有满足以下条件的信息才适合进入候选记忆：

- 明确表达或明确观察到；
- 对未来任务有实际作用；
- 具有一定持久性，或明确标注为本次会话专用；
- 可以引用证据；
- 不属于一次性过程噪音。

不应保存：

- AI 猜测或没有证据的推论；
- Agent 指令、系统规则或权限规则；
- 完整聊天记录和原始命令输出；
- 密码、Token、私钥、认证码、账号和身份证件信息；
- 不必要的个人敏感信息。

### 6.4 会话暂存

候选记忆先进入当前任务或会话级暂存区，不应立即成为长期事实。例如：

```text
SESSION:
本次 Ansible 调试使用 Python 3.12 虚拟环境。
```

只有在确认它是项目长期事实时，才提升为项目 Memory。一次性偏好、临时限制
和本次任务上下文默认不提升到长期层。

### 6.5 合并

任务结束或明确触发合并时，AI 应：

1. 合并语义重复的记忆；
2. 处理新旧事实冲突；
3. 判断内容是否长期有效；
4. 标记或淘汰过期信息；
5. 禁止凭空增加来源中不存在的事实；
6. 将临时信息留在 session，或明确提升到 project；
7. 生成对应的历史记录。

“遗忘”是正常生命周期，不是异常。长期保留所有旧信息会增加噪音和错误影响。

### 6.6 注入

下一次任务只注入相关 Memory，并使用明确边界标记，避免把 Memory 文本误当成
系统规则或用户的新指令。Memory 对 AI 的作用应是建议性的，不能绕过安全规则、
权限边界、项目配置或当前验证结果。

### 6.7 纠错与遗忘

Memory 必须支持：

- 更新；
- 标记过期；
- 标记被替代；
- 用户要求忘记；
- 删除敏感内容；
- 保留必要的修正原因和审查证据。

## 7. 优先级与冲突处理

不同类型的冲突应分别处理。

### 行为和偏好冲突

```text
安全与权限规则
> 当前用户明确意图
> 当前会话临时约束
> 项目长期偏好
> Workspace 默认值
> 历史推断
```

当前用户的明确请求可以覆盖长期默认偏好。若冲突会影响重要操作，AI 应提出
一个聚焦的澄清问题，不应静默选择。

### 项目事实冲突

```text
当前实际观察和验证结果
> 最新有证据的项目事实
> 旧项目 Memory
> Workspace 摘要
> 无证据推断
```

旧 Memory 不得覆盖当前代码、配置、测试结果或实际环境证据。

## 8. 正式操作模式

### Report-only

只调查和报告：

- 不修改当前 Memory；
- 不写历史；
- 输出发现、证据、排除项和缺口；
- 适合只读任务。

### Reconcile

调查并同步：

- 更新当前 Memory；
- 合并候选记忆；
- 写入历史事件；
- 记录变更、证据和遗留问题。

自然语言入口可以是：

```text
只审计并报告当前项目 Memory，禁止修改文件。
```

```text
审计并同步当前项目 Memory，先列出范围和写入目标。
```

```text
刷新 workspace Memory，只更新 workspace 项目地图。
```

## 9. 初始化规则

项目被 clone 或创建本身不应触发后台写入。

首次项目级任务应先检查是否已经存在等价的持久化 Memory。若不存在：

- 只读、解释、报告、计划或 report-only 任务：只报告缺失；
- 已明确允许修改项目文档，或使用 Reconcile 模式：可以创建最小 Memory；
- 不得因为 Memory 缺失而扩大原任务的仓库或跨项目写入范围；
- 初始化只记录实际观察到的事实，未知内容标记为 `unverified`。

“第一次实质性任务自动初始化”是本项目的可选治理决策，不是官方规范。若采用，
必须把“实质性任务”定义为项目范围内的变更、构建、修复或明确的 Memory 操作，
并明确初始化文件属于已授权的最小文档副作用。

## 10. 项目 Memory 与 Workspace Memory

### 项目 Memory

项目 Memory 记录：

- 项目身份和目的；
- 工作入口；
- 工具链和验证方式；
- 已验证事实；
- 已知风险；
- 未验证问题；
- 最近的持久性变化。

项目 Memory 的详细事实和历史由项目自己的 Git 仓库拥有。

### Workspace Memory

Workspace Memory 只记录：

- 项目名称和相对路径；
- 项目用途；
- 生命周期和阶段；
- 当前高层状态；
- TODO 和阻塞项；
- 项目 Memory 链接；
- 最近审计时间和证据快照。

它不复制：

- 项目内部工具版本；
- role 或模块实现细节；
- 生产节点清单；
- 私有主机数据；
- 项目详细审计证据。

普通项目任务不更新 Workspace Memory。Workspace 刷新默认也不修改项目 Memory。

## 11. 历史与溯源

每个审计或持久性变化应形成可追踪事件，至少记录：

```text
event_id
scope
mode                    # report-only / reconcile
target
actor                   # human / AI / both
basis_revision          # commit、分支和必要的 dirty 状态
reason
evidence
claims_added_or_changed
claims_retired
result
gaps
redaction_status
```

历史记录保存证据摘要和引用，不保存秘密、原始输出和完整 transcript。

当前视图应保持简洁；历史是追加式证据。重复刷新不能复制当前项目条目，但可以
在确有审计意义时生成独立事件。第一版使用 Git 可读 Markdown；未来数据库只能
作为可重建索引，不能成为唯一事实来源。

## 12. 安全边界

Memory 可能被注入恶意内容，也可能反过来影响 AI 行为，因此需要在三个阶段
实施保护：

### 写入保护

- 拒绝敏感字段和秘密；
- 拒绝指令形态或策略形态的内容；
- 只允许批准的记忆类型和字段；
- 不把 AI 推断直接标记为已验证事实。

### 合并保护

- 严格禁止创造来源中不存在的事实；
- 应用明确的冲突规则；
- 语义去重；
- 处理 TTL、过期和淘汰。

### 注入保护

- 使用显式 Memory 分隔符；
- 当前用户意图优先；
- 只注入相关内容；
- 将 Memory 视为建议而非权威；
- 不允许 Memory 覆盖安全和权限规则。

如果一条 Memory 能改变 AI 行为，它就必须在写入、合并和注入三个阶段都经过
安全检查。

## 13. 场景与评测

场景示例不是规范本身，而是协议的可理解说明和回归测试材料。每个场景应记录：

- 初始 Memory；
- 用户输入或任务；
- AI 识别出的候选记忆；
- 预期状态变化；
- 预期历史记录；
- 禁止发生的写入；
- 最终评测结果。

第一批场景：

1. 新项目没有 Memory；
2. 项目已有自定义 Memory 路径；
3. Memory 与当前代码事实冲突；
4. 会话临时偏好覆盖长期偏好；
5. 重复 Memory 合并；
6. 过期 Memory 淘汰；
7. 诱导保存 Token 或系统规则；
8. 只读审计；
9. Workspace 刷新；
10. Ansible 作为具体项目案例。

评测至少覆盖：

- 写入精确率和召回率；
- 敏感写入拦截率；
- 注入相关性和过期处理；
- 当前意图是否被错误覆盖；
- 去重和冲突处理质量；
- 是否凭空创造事实；
- Token/context 使用量；
- 是否发生跨项目写入；
- 是否保留用户未提交修改。

## 14. 推荐文档结构

```text
workspace-meta/
├── .agents/rules/
│   ├── memory-protocol.md       # 唯一核心协议
│   ├── project-memory.md        # 项目范围补充
│   └── workspace-memory.md      # workspace 范围补充
├── .agents/templates/
│   ├── project-memory.md
│   └── workspace-memory.md
├── docs/architecture/
│   └── memory-governance.md     # 设计解释，不重复协议
└── docs/reviews/project-memory-governance/
    ├── scenarios/
    └── evals/

projects/<project>/
└── docs/
    ├── project-memory.md
    └── project-memory/history/

workspace-meta/
└── docs/
    ├── workspace-memory.md
    └── workspace-memory/history/
```

`memory-protocol.md` 应是唯一规范来源。适配器只负责精简路由，不重复整套规则。

## 15. 现有文档的重新定位

- `conversation-requirements-2026-08-07.md`：需求和决策溯源；
- `memory-plan.md`：历史设计底稿，不作为当前规范；
- `solution-project-workspace-memory.md`：架构说明；
- `plan-project-workspace-memory-2026-08-07.md`：待协议确认后重写的实施计划；
- `review-project-workspace-memory-2026-08-08.md`：实施前阻塞审查；
- 本文：Memory Governance Protocol v0.1 设计基线。

不应继续把 `memory-plan.md` 修补成最终协议，因为它混合了需求、方案、决策、
实施阶段和多个互相冲突的协议草稿。

## 16. 实施路线

### Phase 0：整理设计来源

解决现有审查中的写入边界、Memory 路径发现、审计模式、历史 ID、敏感信息和
Reality Ops 跨仓库迁移问题。

### Phase 1：完成 Memory Protocol v0.1

只写协议和模板，不迁移项目，不接入复杂脚本。

### Phase 2：完成场景和评测

用本地 fixture 验证初始化、候选记忆、冲突、过期、敏感内容、只读审计和范围保护。

### Phase 3：实现项目级 Memory

先实现项目 Memory 初始化、候选暂存、任务结束合并、项目审计和项目历史。

### Phase 4：实现 Workspace Memory

只维护项目地图，不复制项目详细事实。

### Phase 5：单独迁移 Reality Ops

Reality Ops 是独立 Git 仓库，必须使用独立迁移计划，不能和 workspace-meta 协议
实施混成一个变更。

### Phase 6：评估索引或数据库

第一版继续使用 Git 可读 Markdown。只有在历史查询或跨项目检索真正产生压力时，
再增加可重建索引。

## 17. 方案结论

本设计保留原始方向：

- Memory 机制是通用能力；
- Ansible 只是案例；
- workspace-meta 提供稳定自然语言协议；
- AI 负责语义判断；
- 项目事实归项目；
- 历史可追溯；
- 场景用于解释和评测。

同时补充了原方案缺少的：

- 会话暂存；
- 记忆合并；
- 冲突和过期；
- 注入优先级；
- 写入安全；
- 评测闭环；
- 协议、方案、计划和示例之间的文档边界。

下一步应从本文派生正式的 `Memory Protocol v0.1`，再重写 solution 和 implementation
plan；不应直接按旧 `memory-plan.md` 开始实施。
