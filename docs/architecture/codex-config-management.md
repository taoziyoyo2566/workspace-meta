# Claude/Codex 配置与共享规则架构

本文说明 workspace-meta 如何让 Claude Code 和 Codex 共用一套跨项目规则，
同时把 agent 运行机制留在各自适配器中，并避免把凭据、可执行授权、信任状态
和运行时数据同步到其他机器。

## 一句话模型

Git 仓库保存“应当如何安装”的模板和脚本；`make bootstrap` 和日常使用的
`make sync` 只收敛明确归 workspace-meta 所有的配置面；用户目录中其余内容
始终由当前主机维护。

## 配置分层

| 层级 | 内容 | 所有者 | 同步方式 |
|---|---|---|---|
| workspace-meta | `.agents/rules/` 中的跨项目方法、模板、安装器、状态评估器 | 本仓库 | 有意公开的 Git 远端；仅同步白名单中的可移植内容 |
| 本机能力快照 | `.agents/env/<hostname -s>.yml` | 当前主机 | 本机 probe；Git 忽略 |
| Claude 工作区适配器 | `~/workspace/CLAUDE.md` 中的紧凑路由与安全底线 | workspace-meta | 本仓库 Git |
| Codex 全局指导 | `~/.codex/AGENTS.md` 中的路由与安全底线标记块 | workspace-meta + 主机 | `make bootstrap` / `make sync` 只替换标记块 |
| Codex 全局配置 | `~/.codex/config.toml` 中的标记 hook 块和声明的偏好字段 | workspace-meta + 主机 | `make bootstrap` / `make sync` 只替换 hook 标记块并按字段收敛声明的偏好 |
| Claude 配置目录设置 | `CLAUDE_CONFIG_DIRS` 中每个 Claude 配置目录的 `settings.json`：一个专用 SessionStart 组和 `statusLine` | workspace-meta + 主机 | `make bootstrap` / `make sync` 对每个目录收敛 SessionStart 组，保留其他键和组；`statusLine` 缺失时安装、带 workspace-meta 标记时收敛，不带标记时视为其他 owner 所有，保持不变并报告 |
| Claude 托管 skills | 每个 Claude 配置目录的 `skills/<name>/SKILL.md`（`env-sync`、`project-bootstrap`、`interview`） | workspace-meta（带所有权标记的文件） | `make bootstrap` / `make sync` 从 `.agents/host-templates/<name>-SKILL.md` 收敛整个文件；缺失时安装，带 workspace-meta 所有权标记时收敛，同名但不带标记的 `SKILL.md` 视为其他 owner 所有，保持不变并报告 |
| 项目配置 | `~/workspace/projects/<project>/` 中项目的 `AGENTS.md`（项目 agent 事实的 canonical owner）、导入它的 `CLAUDE.md` 薄适配器、`.claude/`、`.agents/`、`.codex/` | 项目仓库 | 项目自己的 Git；缺失的入口文件由 agent 在首次实质工作时按 `documentation.md` Project Bootstrap 创建，不提交 |
| 项目本地个人文件 | 项目内的 `CLAUDE.local.md`、`.claude/settings.local.json` | 该 checkout 的使用者 | 不进入 Git；不属于 operator 的 clone 只得到这类本地文件 |
| 主机私有状态 | 每个配置目录各自的凭据、未声明的模型/effort/偏好、permissions 与 auto mode、插件、MCP server、信任 hash、审批规则、auto memory、历史数据、缓存、数据库 | 当前主机的对应配置目录 | 不同步 |

workspace-meta 远端有意公开；可发布范围仍由反向白名单和现有安全/发布规则
决定。仓库公开不等于工作区、独立项目或主机运行时状态公开。

“混合所有权”不是复制整个文件。它表示 workspace-meta 只拥有文件中一个可
识别的区域，安装器必须保留区域外的内容。

Claude 的用户层按配置目录划分：`~/.claude` 和 `CLAUDE_CONFIG_DIR` 指向的每个
目录（例如第二个账号使用的 `~/.claude-<account>`）各是一份独立的用户层，分别保存
设置、skills、trust、auto memory 和登录状态。workspace-meta 把托管配置面收敛
到主机上每个在用的 Claude 配置目录，其余内容留在各自目录中。目录列表是主机
本地输入，不提交：`CLAUDE_CONFIG_DIRS` 是冒号分隔的列表（与 `PATH` 相同，
因此目录名可以含空格），每一项必须是绝对路径或以 `~/` 开头；相对路径或
看起来像用空格拼接的多个路径会在任何写入前报错。设置了它时 Makefile 和
bootstrap 把它原样交给同步器，列表中的目录不论名称都会被管理。未设置或为空时
由 `scripts/sync_codex_config.py` 自己发现：`~/.claude` 加上每个含有
`.claude.json` 的 `~/.claude-*` 目录。`.claude.json` 只能把配置目录和
`~/.claude` 的普通备份区分开，迁移出的目录的副本同样带着它，所以发现时跳过
名称像副本或备份的目录。判断按名称片段而不是子串：`.claude-` 之后的部分按
`-`、`_`、`.` 切分，某一段等于 `old`、`orig`、`copy` 或 `tmp`，或以 `bak`
（含 `backup`）开头；名称含 `~`；或以日期结尾（例如 `.bak-20261017`）。
因此 `.claude-gold`、`.claude-origin` 这类名称照常被发现。每个被跳过的目录
连同原因一起打印；确实要管理这样命名的目录时，用 `CLAUDE_CONFIG_DIRS` 显式
列出。check、sync 和 bootstrap 在写入任何配置目录前先打印解析出的目录列表和
跳过的目录。没有 Python 3.11 时 bootstrap 无法发现目录：它只把托管 skills
装进 `CLAUDE_CONFIG_DIRS` 列出的目录（未设置时只装 `~/.claude`），同样保留
不带所有权标记的同名 skill，不改任何 `settings.json`。组织托管、主机用户层、
workspace、项目和项目本地个人文件这五层的所有权模型以
[Agent 配置层与托管配置面](../../.agents/host-templates/README-agents.md#managed-and-host-local-surfaces)
为准。

工作区根目录只承载 workspace-meta 治理文件；独立项目 checkout 放在
`~/workspace/projects/<project>/`，并保留各自最近的 `.git` 根目录。

## 规则与权限分层

两个 agent 都采用“紧凑常驻适配器 + 按任务读取共享模块”。共享行为由
`.agents/rules/` 下的 agent-neutral 文件负责；Codex 的 sandbox、工具发现和
配置表面等运行机制由 `codex-runtime.md` 负责；Claude 的配置层、项目入口文件、
memory、向 operator 提问、委派和长时间无人值守运行等机制由 `claude-runtime.md`
负责。每个 runtime 模块只由自己 agent 的适配器路由。

规则域、唯一 owner、加载路由、执行检查和项目允许补充的内容以
[Workspace-Meta 设计地图](design-map.md) 为准；主机层模型和托管配置面以
[Agent 配置层与托管配置面](../../.agents/host-templates/README-agents.md) 为准。
本文只解释分层关系，不复制领域目录、任务路由或事务步骤。

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
| `.agents/rules/claude-runtime.md` | Claude-specific 运行机制 |
| `.agents/host-templates/codex-hooks.toml` | Codex SessionStart 标记块模板 |
| `.agents/host-templates/codex-preferences.toml` | Codex 字段级偏好期望配置 |
| `.agents/host-templates/<name>-SKILL.md` | 安装到每个 Claude 配置目录 `skills/<name>/SKILL.md` 的托管 skill 模板 |
| `.agents/host-templates/README-agents.md` | 主机层模型与托管配置面 |
| `docs/architecture/design-map.md` | 领域目录：从观察到的现象找到负责的功能或领域及其 owner |
| `scripts/workspace_status.py` | Claude/Codex 共用的状态评估策略，含项目就绪检查 |
| `scripts/claude_status_line.py` | 从 Claude 官方 stdin payload 渲染交互式状态栏 |
| `scripts/check_documentation.py` | 校验入口、owner 路由、runtime 模块归属、设计地图覆盖、链接、truth lifecycle 和 runbook 结构 |
| `scripts/sync_codex_config.py` | 渲染、迁移、校验并按 check、交互或 bootstrap 模式收敛 Codex 的托管区域和每个 Claude 配置目录的托管区域 |
| `scripts/bootstrap-local.sh` | 一台机器的安装入口 |
| `tests/test_workspace_status.py` | 状态顺序、离线降噪、项目就绪检查和输出契约测试 |
| `tests/test_claude_status_line.py` | Claude 状态栏字段、颜色、格式与失败降噪测试 |
| `tests/test_governance_docs.py` | 文档闸门的仓库正例与关键负向场景 |
| `tests/test_sync_codex_config.py` | 安装、迁移、保留、拒绝和幂等测试 |
| `tests/test_bootstrap_local.py` | 在临时仓库副本和临时 HOME 中运行 bootstrap：配置目录发现、显式列表、无 Python 回退、拒绝相对路径和幂等 |
| `docs/reviews/` | 非小型变更的已批准 Plan（意图/执行合同）与验证完成、可提交时的 Changelog（结果） |
| `projects/<project>/` | 独立项目仓库；不属于 workspace-meta 的跟踪范围 |

## 启动检查流程

Codex 安装一个 SessionStart handler，每个 Claude 配置目录也各安装一个。这些
handler 只在容器格式和 `--agent claude|codex` 参数上不同，最终都执行同一个
`scripts/workspace_status.py`。

评估器按固定顺序运行：

1. 检查 `~/workspace` 是否是可用仓库，并读取工作区 dirty 状态。
2. 在 8 秒上限内执行非交互式 `git fetch --quiet --no-tags origin`。
3. 基于同一次 fetch 后的引用计算相对 `origin/main` 的 behind/ahead 数。
4. 执行 `scripts/env_probe.sh --check` 检查当前主机能力快照。
5. 用 `statvfs` 检查 agent 临时目录所在文件系统：优先用 hook 输入里的
   `scratchpad_dir`（Claude 提供），否则用 `TMPDIR`，再否则用 `/tmp`。
   使用率达到 80% 或剩余空间低于 256 MiB 时给出警告，并指向
   `.agents/rules/temporary-files.md`。阈值可用 `--temp-used-percent` 和
   `--temp-min-free-mb` 调整。
6. 检查会话所在项目是否就绪（只读文件系统，不启动子进程）：
   - 工作目录取 hook 输入的 `cwd`，否则取环境变量 `CLAUDE_PROJECT_DIR`；
     两者都没有时跳过。只有工作目录位于 `<workspace>/projects/<name>/` 之内
     （不含 `projects/` 本身）时才检查。
   - `projects` 本身是符号链接时先解析到真实目录，再与解析后的工作目录比较。
   - 项目根是工作目录向上、不超过 `projects/<name>` 的最近一个含可用 `.git`
     的目录：`.git` 是含 `HEAD` 的目录，或是一个 `gitdir:` 文件且它指向
     （相对路径按该文件所在目录解析）的目录含 `HEAD`。指向已删除或已 prune
     目标的 `.git` 文件不算仓库，查找继续向上。找不到时跳过，因为非 Git 目录
     只在 operator 要求时才建立入口文件。`projects/.git` 永远不算项目根，所以
     那里的空 `.git` 目录不会把所有项目当成一个。
   - 项目根是 linked worktree（`.git` 文件指向 `<common>/worktrees/<name>`，
     且 `<common>` 是主 checkout 的 `.git` 目录），而 worktree 自己没有任何
     入口文件（`AGENTS.md`、`CLAUDE.md`、`.claude/CLAUDE.md`、
     `CLAUDE.local.md` 都没有）时，改为检查主 checkout，提示里写成
     `project <主 checkout> (main checkout of <worktree>)`：入口文件应建在主
     checkout，分支合并后自然得到它们，在 worktree 里另写一份会形成第二个、
     不一致的 owner。worktree 自己有入口文件时照常检查它自己，冲突也照常报告。
     bare 仓库的 worktree 没有主 checkout，照常检查。
   - `--agent claude`：项目根有 `CLAUDE.md`、`.claude/CLAUDE.md` 或
     `CLAUDE.local.md` 才算就绪；若项目根有 `AGENTS.md`，其中至少一个文件
     还要在 fenced code 之外有一行恰好是 `@AGENTS.md`（允许首尾空白）。
     只提到或链接 `AGENTS.md` 不会加载它。
   - `--agent codex`：项目根有 `AGENTS.md` 即就绪。没有 `AGENTS.md` 但有
     `CLAUDE.md` 或 `.claude/CLAUDE.md` 时，Codex 不会加载这个 owner，也不能
     导入它，所以提示
     `project <name>: Codex does not load its CLAUDE.md`，并指向
     `.agents/rules/codex-runtime.md` Project Entry Files 提出把 owner 移到
     `AGENTS.md`，而不是在旁边再建一个。
   - 其他未就绪情况提示 `project <name> has no Claude entry file`、
     `project <name>: no Claude entry file imports its AGENTS.md` 或
     `project <name> has no AGENTS.md`，并指向
     `.agents/rules/documentation.md` Project Bootstrap。`<name>` 是项目根
     相对 `projects/` 的路径。这只是兜底提示，创建入口文件由 agent 按规则
     完成，项目自己的文档闸门仍负责校验其适配器。
7. 健康时不输出；异常时只输出一个
   `{"systemMessage":"workspace-meta: ..."}` JSON 对象。临时空间警告和项目
   就绪提示还会写进 `hookSpecificOutput.additionalContext`，让 agent 也看到；
   其他提示仍只给操作者看。

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
- hash 不一致或文件不可读：不执行脚本，只提示重新运行 `make sync`。

这样，Git pull 带来的评估器逻辑变化不会在旧的已信任命令下静默运行。
重新 bootstrap 会产生新命令，Codex 因命令 hash 变化而要求在 `/hooks` 中
重新审查。workspace-meta 不自动写入或清理 Codex hook trust state。
Codex 可能把 `[hooks.state]` 写入 inline managed block 的结束标记之前；同步器
会把这段主机状态移到 managed marker 之外并保留它，避免每次检查都产生漂移或
意外重置 hook trust。

当前官方 hooks 文档定义 `SessionStart` 的 JSON `systemMessage` 为 UI 或事件流
warning，而纯文本 stdout 会进入额外 developer context。本项目因此统一使用
JSON 协议。两家文档都把 `hookSpecificOutput.additionalContext`（配合
`hookEventName: "SessionStart"`）定义为给模型的额外上下文，临时空间警告用它
同时到达 agent。版本化源码核验和 UI 探测属于 dated evidence，保存在
[hook 同步验证记录](../reviews/refactor-codex-sync/round1-2026-07-11.changelog.md)，
不嵌入当前架构说明。

## 同步与迁移

`scripts/sync_codex_config.py` 先在内存中完成全部主机文件和报告区域的渲染与
结构校验。区域包括 Codex 的 `Codex AGENTS.md`、`Codex SessionStart hook`、
`Codex preferences`，以及每个 `--claude-config-dir` 目录的
`Claude SessionStart [<dir>]`、`Claude statusLine [<dir>]` 和每个
`--claude-skill-template` 对应的 `skill <name> [<dir>]`；目录名以 `~` 缩写，
状态列按最长标签对齐。目录来自 `--claude-config-dir`（可重复）和
`--claude-config-dirs`（冒号分隔）；两者都没有给出时，同步器按上文规则自行
发现。Makefile 和 bootstrap 只在设置了 `CLAUDE_CONFIG_DIRS` 时才传入目录，
并总是传入 `.agents/host-templates/` 下的全部 `*-SKILL.md`。目录列表在报告
区域之前解析一次，pre-validation 和写入后的复查使用同一份列表。各类目标
依次处理：

1. Codex `AGENTS.md`：验证标记唯一且有序；替换旧标记块，或在首次安装时
   追加并保留现有用户指导。
2. Codex `config.toml`：先渲染 hash-pinned 命令，移除完全归 workspace-meta
   所有的旧 hook 组，插入新标记块；再按
   `.agents/host-templates/codex-preferences.toml` 的字段 allowlist 比较并
   局部更新 `history.persistence`、`history.max_bytes`、`tui.status_line` 等
   声明字段。整个合并结果再用 `tomllib` 解析。
3. 每个 Claude 配置目录的 `settings.json`：解析整个 JSON，移除完全归
   workspace-meta 所有的旧组，在原位置插入一个新组，再序列化完整结果。
   `statusLine` 缺失时安装；带 workspace-meta 标记时收敛；不带标记时属于
   其他 owner（例如另一个自行安装 status line 的工具，比如为第二个账号提供的
   包装器），保持不变，并在状态输出中报告
   `kept: statusLine owned outside workspace-meta`。
   这不是错误，不会中止其他区域，也不计为漂移。
4. 托管 skills：每个 `<name>-SKILL.md` 模板对应每个配置目录的
   `skills/<name>/SKILL.md`，将完整文件与版本化模板比较。模板名必须是
   小写连字符名称加 `-SKILL.md` 后缀，两个模板不能安装同一个名称；每个模板
   在 YAML frontmatter 之后的第一行必须是所有权标记
   `<!-- workspace-meta managed skill: make sync replaces this file -->`，
   否则在任何写入前报错。目标文件缺失时安装；第一行（frontmatter 之后）是该
   标记时收敛；存在但不带标记时属于其他 owner（例如 operator 自己的同名
   `interview` skill），不写入，并在状态输出中报告
   `kept: skill owned outside workspace-meta`，与外部 `statusLine` 一样不中止
   其他区域、不计为漂移。唯一例外是标记出现之前已由 workspace-meta 安装的
   `env-sync`：不带标记的 `env-sync` 仍按托管文件收敛（dry-run 显示
   `legacy unmarked workspace-meta skill`），写入后带上标记。没有 Python 时
   bootstrap 的 fallback 按同一规则跳过不带标记的同名文件并打印
   `kept <name> skill owned outside workspace-meta`。

报告层把每个配置目录 `settings.json` 中的 SessionStart 和 `statusLine` 分为两个组件；
Codex 和 Claude 的 hook/statusLine 漂移直接比较已解析结构中的 matcher、timeout、
statusMessage、padding、脚本路径、命令目标、解释器、hash pin、hash 不匹配恢复命令
和命令结构版本等托管字段。仅 pin 变化时会明确指出同步将信任当前仓库脚本；只有
无法由这些字段解释的命令结构变化才保留原始 SHA-256 作为兜底证据。交互模式在
确认提示前汇总本次将修改的组件或字段；Codex 原生 `tui.status_line` 继续使用已有的
字段级列表比较。

只有全部目标通过校验后才会在交互确认或 bootstrap 直接应用阶段开始原子写入。
`make sync` 的 dry-run 和 `make agent-sync-check` 使用同一份内存渲染结果；前者只在
存在漂移且没有错误时询问，后者始终只读。`make sync SYNC_EXPECT='标签;标签'`（标签与
状态行一致）不询问：漂移的区域全部在列表内时直接应用，列表外的区域有漂移或标签
未知时拒绝并且不写入任何文件。若确认前目标又发生变化，同步器拒绝
应用并要求重新检查。如果写入中途出现操作系统错误，
同步器会尽力恢复本轮已经写过的目标。它不是跨文件系统事务，但避免了已知的
“先写 AGENTS、后发现 JSON/TOML 无效”的部分升级。

### 字段级 Codex 偏好

`.agents/host-templates/codex-preferences.toml` 是一个 allowlist，而不是
`~/.codex/config.toml` 的镜像。当前只声明 `history.persistence`、
`history.max_bytes` 和 `tui.status_line`：

- 使用解析后的 TOML 值比较；只有值缺失或不一致时才产生配置写入；
- 只局部替换或插入声明字段，保留同一 section 内的未声明字段、注释和
  Codex 生成的状态；
- 若某个 section 的 TOML 语义范围跨入 Codex hook 标记块，缺失偏好字段会插在
  begin marker 之前，避免后续 hook 块替换再次删除该字段；
- 无法定位的重复、冲突或复杂定义会拒绝同步，不自动删除用户内容；
- `history.persistence = "save-all"` 只改变每台主机是否保存自己的
  `history.jsonl`，不把已有对话历史带入仓库。
- `history.max_bytes = 5242880` 使用官方样例中的 5 MiB 上限，超限时由 Codex
  丢弃最旧条目。
- 源码定位器跨行跟踪多行字符串；渲染后会重新解析并验证所有托管字段及
  未托管 TOML 值，避免把字符串正文误认成 section 或赋值。

新增偏好字段必须先在模板 allowlist、所有权矩阵和测试中登记。不要把
`tui.model_availability_nux` 等机器生成的 UI 状态加入模板。

### 拒绝而不是猜测

若同一个 SessionStart group 同时包含 workspace-meta handler 和用户 handler，
同步器会报错并且不写任何目标。需要人工先把两类 handler 拆成独立 group。
这是所有权边界不明确，自动删除或改写都有丢配置风险。

不带标记的 `statusLine` 不同：它整体属于另一个 owner，边界是清楚的，保留它
不会丢配置。因此同步器保留并报告它，而不是拒绝；拒绝会让一个配置目录里其他
工具的 status line 阻止所有目录和 Codex 的收敛。若要改由 workspace-meta 管理，
先在原 owner 处停用它，再移除该字段并重新同步。

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
某个 Claude 配置目录的 status line 属于其他工具时，该目录不安装此 renderer，
由那个工具负责它的显示。

Codex 继续使用 `.agents/host-templates/codex-preferences.toml` 中的原生
`tui.status_line`；该模板是项目与 Git、模型、用量和额度展示顺序的唯一 owner。
原生字段在当前线程没有可用值时可不显示，缺少 pull request 或估算成本不是同步
错误。

## 运维与治理入口

安装、升级、生效、恢复和故障排查由
[新 VPS runbook](../runbooks/new-vps.md) 负责；本项目的开发与交付约束由根目录
`AGENTS.md` 负责。本文不维护操作步骤副本。

配置范围以 [Agent 配置层与托管配置面](../../.agents/host-templates/README-agents.md)
为准，领域与 owner 以 [设计地图](design-map.md) 为准。主机 credentials、trust、
authorization、history、auto memory、cache 和生成状态不属于版本化架构载体；
受保护动作、Git 发布和验证分别由对应 `.agents/rules/` owner 定义。Claude
客户端加载与配置目录行为的版本化证据和复核条件见
[Claude Code 运行时调查记录](../reviews/feature-claude-native-governance/investigation-claude-code-runtime-2026-10-17.md)，
不嵌入当前架构说明。

## 参考

- Codex hooks 与 stdout 协议：<https://developers.openai.com/codex/hooks>
- Codex 内联 hooks 配置：<https://developers.openai.com/codex/config-advanced#hooks>
- Codex 配置参考：<https://developers.openai.com/codex/config-reference#configtoml>
- Codex 配置样例：<https://developers.openai.com/codex/config-sample>
- Codex `AGENTS.md` 指导：<https://developers.openai.com/codex/concepts/customization#agents-guidance>
- Codex `tui.status_line` 配置参考：<https://learn.chatgpt.com/docs/config-file/config-reference>
- Claude Code status line：<https://code.claude.com/docs/en/statusline>
- Claude Code 配置目录与 `CLAUDE_CONFIG_DIR`：<https://code.claude.com/docs/en/claude-directory>、<https://code.claude.com/docs/en/env-vars>
- Claude Code 指令文件、`AGENTS.md` 与 auto memory：<https://code.claude.com/docs/en/memory>
- Claude Code skills：<https://code.claude.com/docs/en/skills>
- Claude Code SessionStart hook 输入与输出：<https://code.claude.com/docs/en/hooks>
- 决策来源：`feedback-register.md` 的 W-R28、W-R73、W-R74
