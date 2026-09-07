# Claude/Codex 配置与共享规则架构

本文说明 workspace-meta 如何让 Claude Code 和 Codex 共用一套跨项目规则，
同时把 agent 运行机制留在各自适配器中，并避免把凭据、可执行授权、信任状态
和运行时数据同步到其他机器。

## 一句话模型

Git 仓库保存“应当如何安装”的模板和脚本；`make bootstrap` 只收敛明确归
workspace-meta 所有的配置面；用户目录中其余内容始终由当前主机维护。

## 配置分层

| 层级 | 内容 | 所有者 | 同步方式 |
|---|---|---|---|
| workspace-meta | `.agents/rules/` 中的跨项目方法、模板、安装器、状态评估器 | 本仓库 | 有意公开的 Git 远端；仅同步白名单中的可移植内容 |
| 本机能力快照 | `.agents/env/<hostname -s>.yml` | 当前主机 | 本机 probe；Git 忽略 |
| Claude 工作区适配器 | `~/workspace/CLAUDE.md` 中的紧凑路由与安全底线 | workspace-meta | 本仓库 Git |
| Codex 全局指导 | `~/.codex/AGENTS.md` 中的路由与安全底线标记块 | workspace-meta + 主机 | `make bootstrap` 只替换标记块 |
| Codex 全局配置 | `~/.codex/config.toml` 中的标记 hook 块和声明的偏好字段 | workspace-meta + 主机 | `make bootstrap` 只替换 hook 标记块并按字段收敛声明的偏好 |
| Claude 全局配置 | `~/.claude/settings.json` 中一个专用 SessionStart 组和带标记的 `statusLine` | workspace-meta + 主机 | `make bootstrap` 收敛这两个字段，保留其他键和组；拒绝覆盖未知 status line |
| 项目配置 | `~/workspace/projects/<project>/` 中项目的 `AGENTS.md`、`.agents/`、`.codex/` | 项目仓库 | 项目自己的 Git |
| 主机私有状态 | 凭据、未声明的模型/偏好、信任 hash、审批规则、历史数据、缓存、数据库 | 当前主机 | 不同步 |

workspace-meta 远端有意公开；可发布范围仍由反向白名单和现有安全/发布规则
决定。仓库公开不等于工作区、独立项目或主机运行时状态公开。

“混合所有权”不是复制整个文件。它表示 workspace-meta 只拥有文件中一个可
识别的区域，安装器必须保留区域外的内容。

工作区根目录只承载 workspace-meta 治理文件；独立项目 checkout 放在
`~/workspace/projects/<project>/`，并保留各自最近的 `.git` 根目录。

## 规则与权限分层

两个 agent 都采用“紧凑常驻适配器 + 按任务读取共享模块”。共享行为由
`.agents/rules/` 下的 agent-neutral 文件负责；Codex 的 sandbox、工具发现和
配置表面等运行机制由 `codex-runtime.md` 负责。Claude 的运行时机制只留在其
适配器或实际客户端配置中。

规则域、唯一 owner 和项目允许补充的内容以
[Agent 配置与规则所有权矩阵](../../.agents/host-templates/README-agents.md) 为准。
本文只解释分层关系，不复制矩阵、任务路由或事务步骤。

语义授权与技术执行权限是两层独立机制：

- [共享授权规则](../../.agents/rules/authorization.md) 定义用户意图和受保护动作；
- [Codex 运行时规则](../../.agents/rules/codex-runtime.md) 定义 sandbox、escalation
  和 host-local execpolicy 的技术边界；
- Git 检查与动作流程由 `.agents/rules/git*.md` 中按任务加载的 owner 定义。

`CLAUDE.md` 与 `.agents/host-templates/codex-AGENTS.md` 负责把可观察的任务触发器
路由到这些 owner。项目 entry file 只增加项目事实和更窄约束；共享规则的具体
步骤不在架构说明或项目适配器中维护副本。

## 仓库地图

| 路径 | 作用 |
|---|---|
| `AGENTS.md` | 本仓库自己的 Codex 开发与交付约束 |
| `CLAUDE.md` | Claude 的工作区级薄适配器 |
| `.agents/host-templates/codex-AGENTS.md` | 安装到 Codex 全局 `AGENTS.md` 的标记块 |
| `.agents/rules/*.md` | agent-neutral 的跨项目按任务读取模块 |
| `.agents/rules/codex-runtime.md` | Codex-specific 运行机制 |
| `.agents/host-templates/codex-hooks.toml` | Codex SessionStart 标记块模板 |
| `.agents/host-templates/codex-preferences.toml` | Codex 字段级偏好期望配置 |
| `.agents/host-templates/README-agents.md` | 共享核心、适配器和主机状态所有权矩阵 |
| `scripts/workspace_status.py` | Claude/Codex 共用的状态评估策略 |
| `scripts/claude_status_line.py` | 从 Claude 官方 stdin payload 渲染交互式状态栏 |
| `scripts/check_documentation.py` | 校验入口、owner 路由、链接、truth lifecycle 和 runbook 结构 |
| `scripts/sync_codex_config.py` | 渲染、迁移、校验并写入三个主机目标 |
| `scripts/bootstrap-local.sh` | 一台机器的安装入口 |
| `tests/test_workspace_status.py` | 状态顺序、离线降噪和输出契约测试 |
| `tests/test_claude_status_line.py` | Claude 状态栏字段、颜色、格式与失败降噪测试 |
| `tests/test_governance_docs.py` | 文档闸门的仓库正例与关键负向场景 |
| `tests/test_sync_codex_config.py` | 安装、迁移、保留、拒绝和幂等测试 |
| `docs/reviews/` | 非小型变更的已批准 Plan（意图/执行合同）与验证完成、可提交时的 Changelog（结果） |
| `projects/<project>/` | 独立项目仓库；不属于 workspace-meta 的跟踪范围 |

## 启动检查流程

Claude 和 Codex 各安装一个 SessionStart handler。两个 handler 只在容器格式
上不同，最终都执行同一个 `scripts/workspace_status.py`。

评估器按固定顺序运行：

1. 检查 `~/workspace` 是否是可用仓库，并读取工作区 dirty 状态。
2. 在 8 秒上限内执行非交互式 `git fetch --quiet --no-tags origin`。
3. 基于同一次 fetch 后的引用计算相对 `origin/main` 的 behind/ahead 数。
4. 执行 `scripts/env_probe.sh --check` 检查当前主机能力快照。
5. 健康时不输出；异常时只输出一个
   `{"systemMessage":"workspace-meta: ..."}` JSON 对象。

单一评估器解决了旧模型的两个问题：三个并发 handler 可能看到不同的远端
引用状态；Claude 与 Codex 的离线行为可能分叉。现在顺序、措辞和降噪策略
都只有一个实现。

### 离线与缓存策略

缓存位于 `~/.cache/workspace-meta/status.json`，属于主机运行时状态，不进入
Git。默认策略如下：

- 最近 300 秒已有成功远端检查时，不重复 fetch。
- 首次无法确认远端状态时提示一次。
- 后续远端失败在 24 小时内不重复提示。
- dirty、ahead、behind、环境快照陈旧不受该 TTL 抑制。
- Git 命令设置 `GIT_TERMINAL_PROMPT=0`，SessionStart 不会等待交互认证。

缓存使用原子替换写入。缓存损坏会被当成空缓存；缓存不可写会附加一条状态
缓存不可用的提示，不会阻止 agent 启动。

## Hook 信任边界

安装器计算 `scripts/workspace_status.py` 的 SHA-256，并把期望 hash 写入 hook
命令。启动时的小型 loader 先验证当前脚本：

- hash 一致：执行评估器；
- hash 不一致或文件不可读：不执行脚本，只提示重新运行 `make bootstrap`。

这样，Git pull 带来的评估器逻辑变化不会在旧的已信任命令下静默运行。
重新 bootstrap 会产生新命令，Codex 因命令 hash 变化而要求在 `/hooks` 中
重新审查。workspace-meta 不自动写入或清理 Codex hook trust state。
Codex 可能把 `[hooks.state]` 写入 inline managed block 的结束标记之前；同步器
会把这段主机状态移到 managed marker 之外并保留它，避免每次检查都产生漂移或
意外重置 hook trust。

当前官方 hooks 文档定义 `SessionStart` 的 JSON `systemMessage` 为 UI 或事件流
warning，而纯文本 stdout 会进入额外 developer context。本项目因此统一使用
JSON 协议。版本化源码核验和 UI 探测属于 dated evidence，保存在
[hook 同步验证记录](../reviews/refactor-codex-sync/round1-2026-07-11.changelog.md)，
不嵌入当前架构说明。

## 同步与迁移

`scripts/sync_codex_config.py` 先在内存中完成三个目标的渲染和结构校验：

1. Codex `AGENTS.md`：验证标记唯一且有序；替换旧标记块，或在首次安装时
   追加并保留现有用户指导。
2. Codex `config.toml`：先渲染 hash-pinned 命令，移除完全归 workspace-meta
   所有的旧 hook 组，插入新标记块；再按
   `.agents/host-templates/codex-preferences.toml` 的字段 allowlist 比较并
   局部更新 `history.persistence`、`history.max_bytes`、`tui.status_line` 等
   声明字段。整个合并结果再用 `tomllib` 解析。
3. Claude `settings.json`：解析整个 JSON，移除完全归 workspace-meta 所有的
   旧组，在原位置插入一个新组，并收敛带 workspace-meta 标记的 `statusLine`
   对象，再序列化完整结果。若已有无法识别的 status line，拒绝写入所有目标。

只有三个目标全部通过校验后才开始原子写入。如果写入中途出现操作系统错误，
同步器会尽力恢复本轮已经写过的目标。它不是跨文件系统事务，但避免了已知的
“先写 AGENTS、后发现 JSON/TOML 无效”的部分升级。

### 字段级 Codex 偏好

`.agents/host-templates/codex-preferences.toml` 是一个 allowlist，而不是
`~/.codex/config.toml` 的镜像。当前只声明 `history.persistence`、
`history.max_bytes` 和 `tui.status_line`：

- 使用解析后的 TOML 值比较；只有值缺失或不一致时才产生配置写入；
- 只局部替换或插入声明字段，保留同一 section 内的未声明字段、注释和
  Codex 生成的状态；
- 无法定位的重复、冲突或复杂定义会拒绝同步，不自动删除用户内容；
- `history.persistence = "save-all"` 只改变每台主机是否保存自己的
  `history.jsonl`，不把已有对话历史带入仓库。
- `history.max_bytes = 5242880` 使用官方样例中的 5 MiB 上限，超限时由 Codex
  丢弃最旧条目；状态栏采用官方样例的 model/context/branch 组合。
- 源码定位器跨行跟踪多行字符串；渲染后会重新解析并验证所有托管字段及
  未托管 TOML 值，避免把字符串正文误认成 section 或赋值。

新增偏好字段必须先在模板 allowlist、所有权矩阵和测试中登记。不要把
`tui.model_availability_nux` 等机器生成的 UI 状态加入模板。

### 拒绝而不是猜测

若同一个 SessionStart group 同时包含 workspace-meta handler 和用户 handler，
同步器会报错并且不写任何目标。需要人工先把两类 handler 拆成独立 group。
这是所有权边界不明确，自动删除或改写都有丢配置风险。

旧的三个独立 workspace-meta hook 会自动迁移为一个 handler。Codex 旧 trust
索引可能成为孤立记录，但它属于主机状态且不影响运行，本项目不会删除。

### Claude/Codex 交互式状态栏

两个客户端都有 `/statusline`，但协议不同：Claude 配置一个 command，并把当前
session 的 JSON 送到 stdin；Codex 配置内建 footer item 的有序列表。这里共享的
是展示意图而不是脚本接口。

Claude renderer 只读官方 status line payload 送进 stdin 的字段：不按 cwd 猜
session，不扫描私有 transcript，也不写死某个模型的价格。具体消费哪些字段
以 `scripts/claude_status_line.py` 为准，本文不维护第二份清单。token 分项
是当前上下文/最近响应数据；美元金额是 Claude 客户端给出的 session 估算
值；额度窗口按剩余百分比加重置倒计时显示，payload 缺少该数据时整段省略。

Codex 继续使用 `.agents/host-templates/codex-preferences.toml` 中的原生
`tui.status_line`。当前配置覆盖 model、context、Git branch、session token totals
和 weekly limit；没有已验证的原生成本项时不模拟美元金额。

## 运维与治理入口

安装、升级、生效、恢复和故障排查由
[新 VPS runbook](../runbooks/new-vps.md) 负责；本项目的开发与交付约束由根目录
`AGENTS.md` 负责。本文不维护操作步骤副本。

配置范围以 [Agent 配置与规则所有权矩阵](../../.agents/host-templates/README-agents.md)
为准。主机 credentials、trust、authorization、history、cache 和生成状态不属于
版本化架构载体；受保护动作、Git 发布和验证分别由对应 `.agents/rules/` owner
定义。

## 参考

- Codex hooks 与 stdout 协议：<https://developers.openai.com/codex/hooks>
- Codex 内联 hooks 配置：<https://developers.openai.com/codex/config-advanced#hooks>
- Codex 配置参考：<https://developers.openai.com/codex/config-reference#configtoml>
- Codex 配置样例：<https://developers.openai.com/codex/config-sample>
- Codex `AGENTS.md` 指导：<https://developers.openai.com/codex/concepts/customization#agents-guidance>
- Codex `tui.status_line` 配置参考：<https://learn.chatgpt.com/docs/config-file/config-reference>
- Claude Code status line：<https://code.claude.com/docs/en/statusline>
- 决策来源：`feedback-register.md` 的 W-R28
