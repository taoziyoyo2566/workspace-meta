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
| Claude SessionStart 组和 env-sync skill | `~/.claude/` | 由 `bootstrap` 收敛，不直接提交 |
| 凭据、登录、项目 trust、Hook trust、approval rules | `~/.codex/`、`~/.claude/` | 永不复制或提交 |
| 本机能力快照 | `~/workspace/.agents/env/<hostname -s>.yml` | 可审核后提交到 workspace-meta |

不要从旧 VPS 复制 `auth.json`、`history`、`default.rules`、
`permissions.rules`、Hook trust state，或整个 `~/.codex`/`~/.claude`。

## 1. 前置条件

在 VPS 上准备：

- Git，以及访问 workspace-meta 和各项目远端的凭据；
- Python 3.11+、`make`；
- 按官方方式安装并登录 Codex CLI；
- 如果使用 Claude，安装并登录 Claude Code；
- 项目所需的 Docker、Ansible、Node 等工具由项目自己的治理文档决定。

先做无写入检查：

```bash
git --version
python3 --version
python3 -c 'import tomllib'
make --version
codex --version
claude --version  # 不使用 Claude 时可跳过
```

如果 Python 低于 3.11，先升级；同步器需要标准库 `tomllib`，不会在缺少
它时退化为未经校验的文本拼接。Codex/Claude 的安装、登录和版本差异以各自
当前官方文档为准；本仓库只负责接入，不负责安装它们或保存凭据。

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

## 4. 初始化本机环境快照

执行前说明（Protected-Action Request Brief）：

- **What**：运行环境探针，在当前 workspace-meta checkout 写入本机能力快照。
- **Why now**：SessionStart 和环境检查需要一份不超过 7 天的当前主机事实。
- **Target / effect**：只写 `~/workspace/.agents/env/<hostname -s>.yml`，不写凭据。
- **Risk / recovery**：这是工作树变更；发现内容不应共享时不要提交，修复环境后
  重新运行探针即可覆盖同一主机快照。
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

这会生成 `.agents/env/<hostname -s>.yml`。它是带时间戳的能力快照，不是凭据；
脚本只记录通用工具可用性、Git 远端可达性等事实，不记录容器名称。新文件应
先审核内容，再按正常 Git 发布流程决定是否提交；不会自动 commit 或 push。

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

这允许工作区内的常规操作顺畅运行，在越过边界或需要额外权限时询问。若选择
更严格的 `untrusted`，未知命令出现更多技术权限提示是预期行为，不表示本仓库
配置失败。不要使用 `danger-full-access` 或 `never` 来绕过检查，也不要把宽泛的
shell/Python/Node 解释器授权规则复制到仓库。

如果设置了 `CODEX_HOME`，它必须在每次使用时指向同一个 Codex 主目录；否则
`bootstrap` 和 `agent-sync-check` 可能读写不同的 `config.toml`。主机私有的
`~/.codex/rules/*.rules` 不属于本仓库，且不应复制到其他 VPS。

## 6. 安装 workspace-meta 集成

执行前说明（Protected-Action Request Brief）：

- **What**：运行 `make bootstrap`，安装或收敛本机 Git Hook、Codex 管理块、Claude
  SessionStart 组和 env-sync skill，并运行只读的 `agent-sync-check`。
- **Why now**：新 VPS 尚未接入 workspace-meta，或仓库中的托管模板已经发生变化。
- **Target / effect**：影响当前仓库的 `.git/config`、当前主机的
  `~/.codex/AGENTS.md`、`~/.codex/config.toml`、`~/.claude/settings.json` 和
  `~/.claude/skills/env-sync/SKILL.md`；托管标记之外的内容保留。
- **Risk / recovery**：输入 JSON/TOML 无效时同步器拒绝写入；写入异常时同步器会
  尽力回滚本轮已写入目标。修复输入后重新运行 bootstrap，再用 check 验证。
- **Excluded**：不安装或登录 Codex/Claude，不信任 Hook，不 pull/merge/commit/push，
  不改 nested project checkout 和主机私有 rules/credentials。
- **Checks / boundary**：先完成第 1–5 节；本说明只覆盖当前主机的一次 bootstrap
  和随后的只读收敛检查。

Exact operation:

从 workspace-meta 根目录运行：

```bash
cd "$HOME/workspace"
make bootstrap
make agent-sync-check
```

`bootstrap` 是幂等的主机本地安装入口，具体会：

1. 将本仓库的 `core.hooksPath` 设置为 `.githooks`，启用 pre-commit 白名单守卫；
2. 检查全局 Git 身份，但不写身份；
3. 收敛 `~/.codex/AGENTS.md`、`~/.codex/config.toml` 和
   `~/.claude/settings.json` 中 workspace-meta 所有的标记块；
4. 安装或更新 `~/.claude/skills/env-sync/SKILL.md`。

标记块之外的主机内容会保留。`agent-sync-check` 只报告漂移，不写主机文件；
返回 0 才表示三个托管目标已经收敛。这个步骤不会安装 Codex/Claude，不会登录，
不会信任 Hook，也不会自动 pull、commit 或 push。

## 7. 修改后如何让它生效

只修改仓库文件、拉取了新的 workspace-meta 提交，或者升级了状态评估器后，
按下面顺序操作：

执行前说明（Protected-Action Request Brief）：

- **What**：刷新远端引用并检查状态；在审核 incoming commits 后，可选择一次精确
  的快进更新，然后重新运行 bootstrap 和收敛检查。
- **Why now**：让当前 checkout 和主机托管配置包含指定的 workspace-meta 变更。
- **Target / effect**：`git fetch` 更新当前仓库的 `origin` 引用；可选
  `git merge --ff-only origin/main` 更新当前 checkout；`make bootstrap` 再写入本机
  托管配置。
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

make bootstrap
make agent-sync-check
make env-probe-check
git config --local --get core.hooksPath
test -x .githooks/pre-commit
```

每一步的生效边界是：

1. **仓库文件变更**：必须先让 checkout 包含目标提交，再运行 `make bootstrap`。
   只拉取或只编辑仓库文件，不会自动改写 `~/.codex`/`~/.claude`。
2. **Codex 指导或配置变更**：`bootstrap` 成功后退出当前 Codex 会话并启动
   新会话，让新的 `AGENTS.md` 和配置从会话启动时加载。
3. **Codex Hook 定义或 evaluator hash 变更**：在 Codex 中运行 `/hooks`，找到
   workspace-meta 的 SessionStart Hook，审查并信任新定义；然后再启动全新会话。
   未重新信任时，Hook 不应被当作已生效。
4. **Claude 配置或 skill 变更**：完全退出并重新打开 Claude Code，让新的
   `settings.json` SessionStart 组和 skill 被重新加载。
5. **环境能力变更**：运行 `make env-probe`，审核生成的 registry；需要共享时
   再按正常 Git 流程提交它。

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
make -C "$HOME/workspace" agent-sync-check
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
| `agent-sync-check` 返回非零 | 先读它列出的具体目标；输入无效先修复主机 JSON/TOML，配置漂移按第 6 节重新 bootstrap |
| Python/tomllib 不可用 | 安装 Python 3.11+；不要绕过同步器的解析校验 |
| `mixed hook group` | 将 workspace-meta handler 与用户 handler 拆到不同 SessionStart group；不要删除未知的用户 handler |
| Codex Hook 不触发 | 按第 6 节重新 bootstrap，再在 `/hooks` 审查/信任并启动新会话；同时检查 `AGENTS.override.md` 是否遮蔽全局指导 |
| 仍然出现远端离线提示 | 检查 Git 凭据、DNS、远端可达性和 `~/.cache/workspace-meta/status.json` 的可写性 |
| 普通命令反复询问 | 检查本机 `approval_policy`；`untrusted` 对未知命令更严格，使用精确的执行授权检查，不要添加宽泛白名单 |
| `core.hooksPath` 不正确 | 按第 6 节重新 bootstrap，确认 `.git/config` 可写 |
| 项目命令跑到了 workspace-meta | 使用 `git -C "$HOME/workspace/projects/<project>" ...`，并先确认最近的 `.git` 根目录 |

## 10. 安全和发布底线

- 不复制或提交 `auth.json`、历史、缓存、数据库、日志、trust state 或主机授权规则。
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
bootstrap: passed/blocked, reason:
agent-sync-check: passed/blocked, reason:
Codex /hooks review: completed/pending
fresh Codex session: completed/pending
fresh Claude session: completed/pending/not used
uncommitted/unpushed changes:
```
