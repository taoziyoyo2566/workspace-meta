# 新 VPS Runbook：workspace-meta、Codex 与 Claude

这份 runbook 适用于一台没有现成 workspace-meta 主机状态的新 VPS。它把
仓库中的共享内容、每台主机必须自己配置的内容，以及“修改后如何生效”放在
同一条可执行流程里。

## 0. 先理解边界

| 内容 | 所在位置 | 是否从 Git 同步 |
|---|---|---|
| 共享规则、模板、脚本、测试 | `~/workspace` | 是 |
| 独立项目 checkout | `~/workspace/projects/<project>` | 项目各自同步 |
| Codex 全局指导和 Hook 标记块 | `~/.codex/AGENTS.md`、`config.toml` | 由 `bootstrap` 收敛，不直接提交 |
| Claude SessionStart、status line 和托管 skills（`env-sync`、`project-bootstrap`、`interview`） | `CLAUDE_CONFIG_DIRS`（冒号分隔）列出的每个 Claude 配置目录；未设置时自动发现 `~/.claude` 和每个含 `.claude.json` 的 `~/.claude-*`，跳过名称像副本或备份的目录 | 由 `bootstrap` 收敛，不直接提交 |
| 凭据、登录、项目 trust、Hook trust、approval rules | `~/.codex/`、每个 Claude 配置目录 | 永不复制或提交 |
| auto memory、模型/effort 默认值、permissions 与 auto mode、插件、MCP server | 每个 Claude 配置目录各自一份 | 否；属于该账号和主机 |
| 项目入口文件（`AGENTS.md` 和导入它的 `CLAUDE.md`） | `~/workspace/projects/<project>` | 项目各自的 Git；缺失时由 agent 创建，不由 bootstrap 生成 |
| 本机能力快照 | `~/workspace/.agents/env/<hostname -s>.yml` | 否；本机生成并由 Git 忽略 |

不要从旧 VPS 复制 `auth.json`、`history`、`default.rules`、
`permissions.rules`、Hook trust state，或整个 `~/.codex`、`~/.claude` 及其他
Claude 配置目录。

## 1. 前置条件

在 VPS 上准备：

- Git，以及访问 workspace-meta 和各项目远端的凭据；
- Python 3.11+、`make`；
- 按官方方式安装并登录 Codex CLI；
- 如果使用 Claude，安装并登录 Claude Code；用多个账号时（每个账号通过
  `CLAUDE_CONFIG_DIR` 使用自己的配置目录，例如 `~/.claude-<account>`），每个目录
  都要各自登录一次。自动发现靠迁移出的目录中的 `.claude.json` 识别它，
  该文件在 Claude Code 第一次用这个目录运行后才存在，所以先登录，再运行
  第 6 节的 bootstrap。目录名不要像副本或备份（含 `bak`、`old`、`copy` 等，
  或以日期结尾），否则自动发现会跳过它，只能用 `CLAUDE_CONFIG_DIRS` 显式列出；
- 项目所需的 Docker、Ansible、Node 等工具由项目自己的治理文档决定。

先做无写入检查：

```bash
git --version
make --version
codex --version
claude --version  # 不使用 Claude 时可跳过
```

这里不要求系统命令 `python3` 本身就是 3.11+；克隆 workspace-meta 后，
`scripts/find_python.sh` 会选择能导入标准库 `tomllib` 的解释器。Codex/Claude
的安装、登录和版本差异以各自当前官方文档为准；本仓库只负责接入，不负责
安装它们或保存凭据。

## 2. 获取 workspace-meta

### 全新 VPS

使用 SSH 或已配置的 Git credential helper。不要把访问 token 写进远端 URL：

```bash
git clone <workspace-meta-remote> "$HOME/workspace"
cd "$HOME/workspace"
git remote -v
git status --short --branch
```

### 已经存在目录

先确认它确实是 workspace-meta 根目录；不要对含有未知改动的目录直接覆盖、
清理或重新初始化：

```bash
git -C "$HOME/workspace" rev-parse --show-toplevel
git -C "$HOME/workspace" remote -v
git -C "$HOME/workspace" status --short --branch
```

确认 workspace-meta 选中的 Python：

```bash
cd "$HOME/workspace"
PYTHON_BIN="$(./scripts/find_python.sh)"
"$PYTHON_BIN" --version
"$PYTHON_BIN" -c 'import tomllib'
```

如果解析器返回失败，先安装或启用 Python 3.11+；同步器不会在缺少
`tomllib` 时退化为未经校验的文本拼接。

配置本机 Git 身份。`bootstrap` 只检查，不会替 operator 写入身份：

```bash
git config --global user.name "你的姓名"
git config --global user.email "你的邮箱"
git config --show-origin --get user.name
git config --show-origin --get user.email
```

## 3. 放置独立项目

项目必须是 workspace-meta 下面的独立 Git 根目录：

```bash
mkdir -p "$HOME/workspace/projects"
git clone <project-remote> "$HOME/workspace/projects/<project>"
git -C "$HOME/workspace/projects/<project>" rev-parse --show-toplevel
```

项目的 `AGENTS.md`、`CLAUDE.md`、测试命令和凭据要求以该项目仓库为准。
不要把项目内容直接放到 workspace-meta 根目录，也不要用 workspace-meta 的
Git 命令管理嵌套项目。

缺少 agent 入口文件的 Git 项目不需要手工准备：agent 第一次在项目里做实质
工作时，按 `.agents/rules/documentation.md` Project Bootstrap 创建
`AGENTS.md` 和导入它的 `CLAUDE.md`（不属于你的 clone 只得到本地未跟踪的
`CLAUDE.local.md`），不提交，并报告创建了什么；SessionStart 也会提示这类项目。
不是 Git 仓库的目录只在你要求时才处理。

不要在 `~/workspace/projects/` 下创建 `.git`。Claude Code 把任何 `.git` 条目
都当作仓库根，`projects/.git` 会让其下所有非 Git 目录共用一个 auto memory
目录和 trust 根。

## 4. 初始化本机环境快照

执行前说明（Protected-Action Request Brief）：

- **What**：运行环境探针，在当前 workspace-meta checkout 写入本机能力快照。
- **Why now**：SessionStart 和环境检查需要一份不超过 7 天的当前主机事实。
- **Target / effect**：只写 `~/workspace/.agents/env/<hostname -s>.yml`，不写凭据。
- **Risk / recovery**：这是可覆盖的本机运行时文件；修复环境后重新运行探针即可
  刷新同一主机快照。
- **Excluded**：不安装软件、不登录服务、不修改 `~/.codex`/`~/.claude`，不 commit
  或 push。
- **Checks / boundary**：执行前确认当前目录是 workspace-meta 根目录；本说明只覆盖
  当前主机的一次 probe 和 check。

Exact operation:

第一次在这台机器上运行：

```bash
cd "$HOME/workspace"
make env-probe
make env-probe-check
```

这会生成 `.agents/env/<hostname -s>.yml`。它是带时间戳的本机能力快照，不是
凭据；脚本只记录通用工具可用性、Git 远端可达性等事实，不记录容器名称。
该文件由 Git 忽略，不应 force-add、提交或复制到其他机器。

每 7 天或能力发生变化时重新运行 `make env-probe`。`env-probe-check` 失败时，
不要继续引用旧快照作为当前环境事实。

## 5. 配置 Codex 的主机私有策略

workspace-meta 会管理 `~/.codex/AGENTS.md` 和 `~/.codex/config.toml` 中的
明确标记块；模型选择、项目 trust、Hook trust、凭据和执行授权规则仍由本机
维护。建议交互式使用采用：

| 设置 | 建议 |
|---|---|
| `sandbox_mode` | `workspace-write` |
| `approval_policy` | `on-request` |
| 项目 trust | 逐个信任 `~/workspace/projects/` 下的项目，不信任整个 `~/workspace` |

这允许工作区内的常规操作顺畅运行，在越过边界或需要额外权限时询问。若选择
更严格的 `untrusted`，未知命令出现更多技术权限提示是预期行为，不表示本仓库
配置失败。不要使用 `danger-full-access` 或 `never` 来绕过检查，也不要把宽泛的
shell/Python/Node 解释器授权规则复制到仓库。

如果设置了 `CODEX_HOME`，它必须在每次使用时指向同一个 Codex 主目录；否则
`bootstrap` 和 `agent-sync-check` 可能读写不同的 `config.toml`。主机私有的
`~/.codex/rules/*.rules` 不属于本仓库，且不应复制到其他 VPS。

## 6. 安装 workspace-meta 集成

执行前说明（Protected-Action Request Brief）：

- **What**：运行 `make bootstrap`，安装或收敛本机 Git Hook、Codex 管理块，以及
  每个 Claude 配置目录的 SessionStart、status line 和托管 skills，并运行只读的
  `agent-sync-check`。
- **Why now**：新 VPS 尚未接入 workspace-meta，或仓库中的托管模板已经发生变化。
- **Target / effect**：影响当前仓库的 `.git/config`、当前主机的
  `~/.codex/AGENTS.md`、`~/.codex/config.toml`，以及 `CLAUDE_CONFIG_DIRS` 中
  每个 Claude 配置目录的 `settings.json` 和 `skills/<name>/SKILL.md`
  （`env-sync`、`project-bootstrap`、`interview`）；托管标记之外的内容、其他
  owner 的 status line 和不带所有权标记的同名 skill 保留。
- **Risk / recovery**：输入 JSON/TOML 无效时同步器拒绝写入；写入异常时同步器会
  尽力回滚本轮已写入目标。修复输入后重新运行 bootstrap，再用 check 验证。
- **Excluded**：不安装或登录 Codex/Claude，不信任 Hook，不 pull/merge/commit/push，
  不改 nested project checkout 和主机私有 rules/credentials。
- **Checks / boundary**：先完成第 1–5 节。`bootstrap` 不询问就写入，所以先运行
  只读的 `make agent-sync-check`，确认输出开头列出的 Claude 配置目录正是本机
  在用的目录、被跳过的只是副本或备份（新主机上它报告漂移并返回非零是预期的）；
  本说明只覆盖当前主机的一次 bootstrap 和前后两次只读收敛检查。

Exact operation:

从 workspace-meta 根目录运行：

```bash
cd "$HOME/workspace"
make agent-sync-check  # 只读：先确认配置目录列表
make bootstrap
make agent-sync-check
```

`bootstrap` 是幂等的主机本地安装入口，具体会：

1. 将本仓库的 `core.hooksPath` 设置为 `.githooks`，启用 pre-commit 白名单守卫；
2. 检查全局 Git 身份，但不写身份；
3. 收敛 `~/.codex/AGENTS.md`、`~/.codex/config.toml` 中 workspace-meta 所有的
   标记块，以及每个 Claude 配置目录 `settings.json` 中的 SessionStart 组和
   status line；
4. 在每个 Claude 配置目录安装或更新 `skills/env-sync/SKILL.md`、
   `skills/project-bootstrap/SKILL.md` 和 `skills/interview/SKILL.md`。
   托管 skill 在 frontmatter 之后的第一行带有所有权标记
   `<!-- workspace-meta managed skill: make sync replaces this file -->`；
   已存在但不带这个标记的同名 `SKILL.md`（例如自己写的 `interview` skill）
   属于其他 owner，保持不变并显示 `kept: skill owned outside workspace-meta`，
   其他区域照常收敛。例外是标记出现前由 workspace-meta 安装的 `env-sync`：
   不带标记时仍会被更新，并带上标记。

输出开头的 `Claude config dirs (CLAUDE_CONFIG_DIRS):` 列出本次管理的配置目录。
未设置 `CLAUDE_CONFIG_DIRS` 时由同步器自动发现：`~/.claude` 加上每个含
`.claude.json` 的 `~/.claude-*` 目录。迁移出的配置目录的副本（例如
`cp -a ~/.claude-<account> ~/.claude-<account>.bak-20261017`）同样带着 `.claude.json`，
所以名称像副本或备份的目录不会被选中：`.claude-` 之后的部分按 `-`、`_`、`.`
切分后，某一段等于 `old`、`orig`、`copy` 或 `tmp`，或以 `bak`（含 `backup`）
开头；名称含 `~`；或以日期结尾。只比较完整片段，所以 `.claude-gold`、
`.claude-origin` 照常被发现。被跳过的目录列在
`Skipped as a likely copy or backup (name it in CLAUDE_CONFIG_DIRS to manage it):`
下面，并写明原因。`bootstrap` 不询问就写入，所以运行前先用只读的
`make agent-sync-check` 看一遍这两个列表。

列表不对，或要管理一个名称会被跳过的目录时，用冒号分隔的 `CLAUDE_CONFIG_DIRS`
显式列出要管理的全部目录（与 `PATH` 相同，目录名可以含空格）。显式列表取代
自动发现，其中的目录不论名称都会被管理。之后的 `sync` 和 `agent-sync-check`
使用同一个列表（把 `<account>` 换成第二个配置目录的实际名称）：

```bash
make agent-sync-check CLAUDE_CONFIG_DIRS="$HOME/.claude:$HOME/.claude-<account>"
make bootstrap CLAUDE_CONFIG_DIRS="$HOME/.claude:$HOME/.claude-<account>"
```

每一项必须是绝对路径或以 `~/` 开头。相对路径，或用空格而不是冒号分隔的
列表，会让同步器和 `scripts/bootstrap-local.sh` 在写入任何配置目录前报错退出。
直接运行 `scripts/bootstrap-local.sh` 时规则相同：设置了 `CLAUDE_CONFIG_DIRS`
就使用它，未设置就由同步器自动发现。没有 Python 3.11 时它无法自动发现，只把
托管 skills 装进列出的目录（未设置时只装 `~/.claude`），不改 `settings.json`；
不带所有权标记的同名 skill 同样保留，并打印
`kept <name> skill owned outside workspace-meta`。

标记块之外的主机内容会保留。如果某个 Claude 配置目录已有不带 workspace-meta
标记的 `statusLine`（例如另一个自行安装 status line 的工具，比如为第二个账号
提供的包装器），同步器把它当作其他工具所有，保持不变并显示
`kept: statusLine owned outside workspace-meta`；这不是错误，其他区域照常收敛。
`agent-sync-check` 只报告漂移，不写主机文件；返回 0 才表示 Codex 的托管区域和
每个 Claude 配置目录的托管区域都已收敛（`kept` 的 status line 和 skill 不算漂移）。
这个步骤不会安装 Codex/Claude，不会登录，不会信任 Hook，也不会自动 pull、
commit 或 push。

## 7. 修改后如何让它生效

只修改仓库文件、拉取了新的 workspace-meta 提交，或者升级了状态评估器后，
按下面顺序操作：

执行前说明（Protected-Action Request Brief）：

- **What**：刷新远端引用并检查状态；在审核 incoming commits 后，可选择一次精确
  的快进更新，然后运行交互式托管配置同步和只读收敛检查。
- **Why now**：让当前 checkout 和主机托管配置包含指定的 workspace-meta 变更。
- **Target / effect**：`git fetch` 更新当前仓库的 `origin` 引用；可选
  `git merge --ff-only origin/main` 更新当前 checkout；`make sync` 先显示当前
  checkout 与本机托管值的差异，只在确认后写入这些托管值。
- **Risk / recovery**：merge 只允许已审核且可快进的范围；发现本地改动或范围不明
  时停止，不 stash、reset、clean 或覆盖它们。主机配置变更失败时按第 6 节修复并
  重新检查。
- **Excluded**：不自动 pull、commit、push、rebase、解决冲突、信任 Hook 或修改项目
  仓库；Hook 信任和新会话仍按下面步骤手动完成。
- **Checks / boundary**：先查看 branch、ahead/behind、dirty state；这次说明只覆盖
  当前 workspace-meta checkout 和当前主机的一次更新/激活。

Exact operation:

```bash
cd "$HOME/workspace"
git fetch origin
git status --short --branch
# 审核 incoming commits 和本地改动后，按你的发布/更新决定执行更新
# 例如干净且确认只需快进时：git merge --ff-only origin/main

make sync
make agent-sync-check
make env-probe-check
git config --local --get core.hooksPath
test -x .githooks/pre-commit
```

`make sync` 总是先执行只读 dry-run。全部为 `OK` 时不询问也不写入；出现
`DRIFT` 时按组件显示真正变化的托管字段，并在确认前列出 `Changes to apply`；
Codex/Claude SessionStart 和 Claude `statusLine` 的脚本 pin 会显示仓库值与已安装值。
仅 `Y`/`y` 会应用，Enter、`N`/`n` 或其他输入都保持不变；出现 `ERROR` 时停止且
不提供确认。`make agent-sync-check` 使用相同诊断但永不询问或写入。

每一步的生效边界是：

1. **仓库文件变更**：必须先让 checkout 包含目标提交，再运行 `make sync`。
   只拉取或只编辑仓库文件，不会自动改写 `~/.codex`/`~/.claude`。
2. **Codex 指导或配置变更**：`sync` 成功后退出当前 Codex 会话并启动
   新会话，让新的 `AGENTS.md` 和配置从会话启动时加载。
3. **Codex Hook 定义或 evaluator hash 变更**：在 Codex 中运行 `/hooks`，找到
   workspace-meta 的 SessionStart Hook，审查并信任新定义；然后再启动全新会话。
   未重新信任时，Hook 不应被当作已生效。
4. **Claude 配置、status line 或 skill 变更**：`make sync` 会一次收敛列表中的
   所有 Claude 配置目录；随后用每个账号各自完全退出并重新打开 Claude Code，
   让新的 `settings.json` SessionStart/statusLine 和 skill 被重新加载；可用
   `/statusline` 确认 UI。评估器 hash 变化后，未同步的配置目录会在会话开始时
   提示运行 `make sync`。
5. **环境能力变更**：运行 `make env-probe`，审核本机生成的 registry；其他机器
   需要同类事实时在当地重新运行 probe。

最小验收标准是：`agent-sync-check` 返回 0、`env-probe-check` 返回 0、
`core.hooksPath` 输出 `.githooks`，并且 pre-commit 文件可执行。真实的 Codex
`/hooks` 信任和新的 Claude/Codex SessionStart 会话属于主机 UI 验证，不能由
仓库单元测试代替。

当前运行时的一个实用注意点：只读检查直接运行原命令即可；不要为了吞掉退出码
在外层额外拼接 `|| true`、变量展开或复杂 shell wrapper。执行授权可能按完整
命令重新匹配，导致本来可直接运行的检查再次弹技术权限提示。

## 8. 日常使用

开始工作时：

```bash
git -C "$HOME/workspace" status --short --branch
git -C "$HOME/workspace" fetch origin
make -C "$HOME/workspace" sync
make -C "$HOME/workspace" env-probe-check
```

确认 incoming commits、ahead/behind 和本地改动后，再显式执行 `merge` 或
其他项目允许的更新方式。workspace-meta 的 SessionStart 检查不会自动更新
checkout。workspace-meta 更新后重复第 7 节；项目更新则进入对应项目根目录，
执行项目自己的同步和验证流程。

## 9. 常见故障

| 现象 | 处理 |
|---|---|
| `env-probe-check` 提示 missing/stale | 回到第 4 节的 action brief，运行 `make env-probe`，审核后再运行 check |
| `agent-sync-check` 返回非零 | 先读它列出的具体目标；输入无效先修复主机 JSON/TOML，配置漂移运行 `make sync` 审核并确认 |
| Python/tomllib 不可用 | 安装 Python 3.11+；不要绕过同步器的解析校验 |
| `mixed hook group` | 将 workspace-meta handler 与用户 handler 拆到不同 SessionStart group；不要删除未知的用户 handler |
| `kept: statusLine owned outside workspace-meta` | 不是故障：该配置目录的 status line 属于其他工具（例如为第二个账号提供的包装器），同步器不改它。若明确要交给 workspace-meta，先在原 owner 处停用它，备份后只移除 `settings.json` 的 `statusLine` 字段，再运行 `make sync`，不要删除整个文件 |
| 某个账号的配置目录缺少 workspace-meta SessionStart 组或托管 skill | 健康时 SessionStart 不输出任何内容，所以没有提示不能说明 hook 存在；运行 `make agent-sync-check`，确认输出开头的配置目录列表包含该账号的 `CLAUDE_CONFIG_DIR`。它出现在 `Skipped as a likely copy or backup` 下，或根本没有出现（目录里还没有 `.claude.json`，先用该账号登录一次）时，用冒号分隔的 `CLAUDE_CONFIG_DIRS` 显式列出全部目录后重新同步，再用该账号启动新会话 |
| 配置目录列表包含不该管理的目录 | 用冒号分隔的 `CLAUDE_CONFIG_DIRS` 显式列出要管理的目录；自动发现只选含 `.claude.json` 的 `~/.claude-*`，并跳过名称像副本或备份的目录 |
| `ERROR: Claude config dir must be an absolute path or start with ~/` 或 `looks like a space-separated list` | `CLAUDE_CONFIG_DIRS` 中有相对路径，或用空格分隔了多个目录；改成冒号分隔的绝对路径或 `~/` 路径后重新运行。报错时没有写入任何配置目录 |
| 启动提示 `project <name> has no Claude entry file`、`no Claude entry file imports its AGENTS.md` 或 `has no AGENTS.md` | 让 agent 在该项目开始实质工作，它按 `documentation.md` Project Bootstrap 创建缺失的入口文件并报告；已有文件互相冲突时 agent 只报告并提出修改建议。linked worktree 的主 checkout 已有该入口文件时不会出现这条提示，分支合并后自然得到它 |
| Codex 启动提示 `project <name>: Codex does not load its CLAUDE.md` | 项目的 agent 事实在 `CLAUDE.md` 中，Codex 只读 `AGENTS.md` 且不能导入；agent 按 `codex-runtime.md` Project Entry Files 提出把内容移到 `AGENTS.md`、留下导入它的 `CLAUDE.md` 薄适配器，operator 同意后才改，不另建一份 `AGENTS.md` |
| 多个非 Git 项目目录共用同一份 Claude auto memory 或 trust | 检查 `~/workspace/projects/.git` 是否是空目录；先查明它由什么创建，再决定是否移除 |
| Codex Hook 不触发 | 按第 6 节重新 bootstrap，再在 `/hooks` 审查/信任并启动新会话；同时检查 `AGENTS.override.md` 是否遮蔽全局指导 |
| 仍然出现远端离线提示 | 检查 Git 凭据、DNS、远端可达性和 `~/.cache/workspace-meta/status.json` 的可写性 |
| 普通命令反复询问 | 检查本机 `approval_policy`；`untrusted` 对未知命令更严格，使用精确的执行授权检查，不要添加宽泛白名单 |
| `core.hooksPath` 不正确 | 按第 6 节重新 bootstrap，确认 `.git/config` 可写 |
| 项目命令跑到了 workspace-meta | 使用 `git -C "$HOME/workspace/projects/<project>" ...`，并先确认最近的 `.git` 根目录 |

## 10. 安全和发布底线

- 不复制或提交 `auth.json`、历史、缓存、数据库、日志、trust state 或主机授权规则。
- 不把一个 Claude 配置目录复制或软链接成另一个：每个目录的凭据、trust 和 auto
  memory 属于各自账号；需要的托管内容由 `make sync` 分别收敛。
- 不把 token、密码或私钥写入远端 URL、registry、日志或提交内容。
- 不用 `--dangerously-bypass-hook-trust` 替代真实 `/hooks` 信任验收。
- 不自动 commit、push、merge、rebase、清理未知改动或修改另一台主机的配置。
- 仓库修改完成后，保留可审查状态并明确报告“未提交/未推送”；发布需要单独的
  内容审查和授权。

## 11. 交接记录模板

完成新 VPS 初始化或一次集成升级后，可记录：

```text
workspace-meta checkout/commit:
workspace-meta remote reachability:
env registry: path, probed_at, reviewed yes/no
Claude config dirs (CLAUDE_CONFIG_DIRS):
bootstrap: passed/blocked, reason:
agent-sync-check: passed/blocked, reason:
Codex /hooks review: completed/pending
fresh Codex session: completed/pending
fresh Claude session per config dir: completed/pending/not used
uncommitted/unpushed changes:
```
