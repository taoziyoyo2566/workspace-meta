# claude-mem Runbook：可选的会话历史插件

claude-mem 是第三方 Claude Code 插件：它的 hooks 把工具调用和 prompt 交给后台
模型压缩成笔记，存进 `~/.claude-mem/`，会话启动时注入最近的笔记，并提供检索
工具。它属于主机本地层，workspace-meta 不安装也不同步它；装不装、装进哪个配置
目录由你决定。它和规则的分工，以及哪些功能必须关闭、为什么，见
[`claude-runtime.md` Memory](../../.agents/rules/claude-runtime.md#memory)；
后台记录为什么可以保留，见 [backlog 的 Session History](../backlog.md#session-history)。
本 runbook 只给做法。

下面的键名、默认值、开关和命令核对自 claude-mem 15.8.0 的源码和 npm 包，以及
Claude Code 2.1.316。整套步骤在一台主机上装过一次，其中 Bun 解压、写设置和关闭
自动更新用的是等效脚本。本文第 2 到 6 节、第 8 节和第 9 节的命令另外在一个临时
HOME 里原样运行过：调用安装器、`doctor`、`telemetry` 和关停接口的几行用桩代替，
只覆盖 x86_64 分支；第 7 节的会话检查在真实安装上做过。claude-mem 升级或
`claude update` 之后，先重新核对再沿用。核对记录在该主机的证据库
`~/.local/share/workspace-meta/evidence/` 里。

## 1. 执行前说明

Protected-Action Request Brief（覆盖第 3 到 7 节的全部写入）：

- **What**：把 claude-mem 装进一个 Claude 配置目录：先装好固定版本的 Bun 和 uv，
  写 claude-mem 的设置和配置目录里的开关与拒绝规则，再运行安装器，关闭 telemetry
  和 marketplace 自动更新。
- **Why now**：你决定在这台主机上保留会话历史。
- **Target / effect**：
  - `~/.bun/bin/bun`；没有 uv 时 `~/.local/bin/uv`、`uvx`；
  - `~/.claude-mem/`：设置、`telemetry.json`、`.env`、数据库、chroma 数据和日志；
  - 配置目录 `$cfg`：`settings.json` 的 `env`、`permissions.deny` 和 `enabledPlugins`，
    `plugins/known_marketplaces.json` 的 `thedotmack`，`plugins/installed_plugins.json`，
    `plugins/marketplaces/thedotmack/`、`plugins/cache/thedotmack/`、
    `plugins/data/claude-mem-thedotmack/`；备份放在 `$cfg/backup-pre-claude-mem/`；
  - `~/.local/bin/claude-mem`（安装器用 Bun 编译的 launcher）；
  - `npx` 从 npm 下载 `claude-mem@15.8.0` 和它的依赖（其中 better-auth 没有锁定
    版本），安装器下载固定 SHA-256 的 tree-sitter；
  - 第一次会话起：常驻 worker（只监听 `127.0.0.1:$port`），通过 uvx 运行的
    chroma-mcp（`~/.cache/uv`、`~/.local/share/uv`；没有合适的系统 Python 3.13 时
    还会下载一个），以及 embedding 模型（`~/.cache/chroma`）。笔记模型用该账号的
    订阅额度。
  - `~/.local/bin` 已在 `PATH` 中、或 shell rc 文件里已有这个路径时，不改任何 rc
    文件；两者都不满足时，安装器或会话启动的 hook 会往 `$SHELL` 对应的 `~/.bashrc`、
    `~/.zshrc` 或 fish 配置追加一次 `PATH`。`~/.profile` 不会被改。workspace-meta 的
    托管区域和 `~/.codex` 不受影响。
- **Risk / recovery**：工具输入输出和 prompt 会写进本机数据库并发给笔记模型。
  第 3 节的备份在任何写入之前做；回滚按第 9 节手动做。
- **Excluded**：不登录 cmem.ai，不启用托管 observer、Cloud Sync 或 TeamBrain，不关闭
  Claude Code 的 auto memory，不装进 rule-eval 的 `--claude-config-dir` 配置目录，
  不用 sudo，不改 workspace-meta 的文件。
- **Checks / boundary**：第 2 节的前提全部满足；从第 6 节的安装命令到关闭自动更新
  之间，不要启动这个配置目录的新会话。本说明只覆盖一个配置目录的一次安装和之后的
  检查；升级和回滚各自需要再确认。

## 2. 前提和变量

只装进一个配置目录。每个配置目录各用一个库的做法（`CLAUDE_MEM_DATA_DIR`、
`CLAUDE_MEM_WORKER_PORT`，以及每个库各自关闭 telemetry）还没有验证，见 backlog。
不要装进 rule-eval 用 `--claude-config-dir` 指定的干净配置目录。在日常配置目录里
跑 rule-eval 不受影响：它带 `--setting-sources project` 启动，不加载用户插件。

在你自己的新终端里设好变量并检查前提。后面每一节都用这三个变量；隔了一段时间再
做升级或回滚时，先重新设一次：

```bash
cfg="$HOME/.claude-<account>"      # 选定的配置目录，绝对路径；默认目录写 $HOME/.claude
port=$((37700 + $(id -u) % 100))   # claude-mem worker 的端口
ver=15.8.0                          # 核对过的 claude-mem 版本
test -d "$cfg" && echo "cfg ok: $cfg" || echo "cfg 不存在：检查路径"
uname -m                            # x86_64 或 aarch64
node --version                      # 需要 ^20.19.0 或 >=22.12.0；hooks 和 MCP server 也要用 node
npm --version && npx --version && python3 --version && curl --version | head -1
case ":$PATH:" in *":$HOME/.local/bin:"*) echo "PATH ok" ;; *) echo "先把 ~/.local/bin 加进 PATH，重新登录后再继续" ;; esac
```

`node`、`npx` 和 `~/.local/bin` 都要在 Claude Code 运行时的 `PATH` 里：hooks 直接
调用 `claude-mem` 和 `node`。

默认目录要注意：对 `claude` 命令，`CLAUDE_CONFIG_DIR=$HOME/.claude` 和不设并不相同
（前者让 Claude Code 改用 `~/.claude/.claude.json`），所以选默认目录时，下面的
`claude` 命令都去掉 `CLAUDE_CONFIG_DIR=...`；claude-mem 自己的命令（`npx claude-mem
...`）两种写法效果一样。

## 3. 备份（任何写入之前）

备份放在配置目录里，和原文件同样受保护；`settings.json` 的 `env` 可能含凭据，不要
复制进证据库。备份目录已经存在时，这段保留原来的备份，什么都不改：

```bash
b="$cfg/backup-pre-claude-mem"
if mkdir -m 700 "$b"; then
  for f in settings.json plugins/known_marketplaces.json plugins/installed_plugins.json; do
    if [ -e "$cfg/$f" ]; then cp -a "$cfg/$f" "$b/$(echo "$f" | tr / _)"; else echo "absent $cfg/$f" >> "$b/absent.txt"; fi
  done
  for p in "$cfg/plugins/cache" "$cfg/plugins/data" ~/.claude-mem ~/.bun ~/.local/bin/uv ~/.local/bin/uvx \
           ~/.local/bin/claude-mem ~/.cache/uv ~/.local/share/uv ~/.cache/chroma; do
    [ -e "$p" ] || echo "absent $p" >> "$b/absent.txt"
  done
else
  echo "$b already exists: keeping the earlier backup"
fi
ls -la "$b" && cat "$b/absent.txt"
```

`absent.txt` 记下安装前不存在的路径，第 9 节回滚时只删其中列出的。`~/.claude-mem`
已经存在时先停下，弄清它属于谁再继续。

## 4. 装好 Bun 和 uv

claude-mem 需要 Bun（不低于 1.2.16）和 uv。缺少时安装器会把
`https://bun.sh/install` 和 `https://astral.sh/uv/install.sh` 直接交给 shell 执行，
装的是当天的最新版本，Bun 的脚本还会往 `~/.bashrc` 追加三行；主机没有 `unzip` 时
Bun 的脚本直接退出，而安装器这时已经启用了插件，留下半装状态：每个会话的 hook 都
去调用一个不存在的 `claude-mem`。所以先自己装好固定版本；安装器在
`~/.bun/bin/bun`、`PATH` 或 `~/.local/bin` 里找到它们，就不再运行这两个脚本。下面
的块自动核对三处 SHA-256（发布方的校验文件、GitHub API 记录的 digest、本地计算
值），不一致就停，最后删掉临时目录：

```bash
d=$(mktemp -d) && cd "$d"
case "$(uname -m)" in
  x86_64)  if grep -qm1 avx2 /proc/cpuinfo; then bun_asset=bun-linux-x64; else bun_asset=bun-linux-x64-baseline; fi
           uv_asset=uv-x86_64-unknown-linux-gnu ;;
  aarch64) bun_asset=bun-linux-aarch64; uv_asset=uv-aarch64-unknown-linux-gnu ;;
esac
verify() {  # $1 仓库, $2 tag, $3 资产文件
  want=$(curl -fsSL "https://api.github.com/repos/$1/releases/tags/$2" | python3 -c 'import json, sys; print([a["digest"] for a in json.load(sys.stdin)["assets"] if a["name"] == sys.argv[1]][0])' "$3")
  have="sha256:$(sha256sum "$3" | cut -d' ' -f1)"
  if [ "$want" = "$have" ]; then echo "digest OK $3"; else echo "DIGEST MISMATCH $3"; return 1; fi
}
curl -fsSLO "https://github.com/oven-sh/bun/releases/download/bun-v1.4.4/$bun_asset.zip"
curl -fsSLO https://github.com/oven-sh/bun/releases/download/bun-v1.4.4/SHASUMS256.txt
grep " $bun_asset.zip\$" SHASUMS256.txt | sha256sum -c - && verify oven-sh/bun bun-v1.4.4 "$bun_asset.zip" &&
  mkdir -p ~/.bun/bin &&
  python3 -c 'import zipfile, shutil, sys; shutil.copyfileobj(zipfile.ZipFile(sys.argv[1] + ".zip").open(sys.argv[1] + "/bun"), open(sys.argv[2], "xb"))' "$bun_asset" ~/.bun/bin/bun &&
  chmod 755 ~/.bun/bin/bun && ~/.bun/bin/bun --version
if command -v uv >/dev/null; then
  uv --version
else
  curl -fsSLO "https://github.com/astral-sh/uv/releases/download/0.13.6/$uv_asset.tar.gz"
  curl -fsSLO "https://github.com/astral-sh/uv/releases/download/0.13.6/$uv_asset.tar.gz.sha256"
  sha256sum -c "$uv_asset.tar.gz.sha256" && verify astral-sh/uv 0.13.6 "$uv_asset.tar.gz" &&
    tar -xzf "$uv_asset.tar.gz" --no-same-owner && mkdir -p ~/.local/bin &&
    install -m 755 "$uv_asset/uv" "$uv_asset/uvx" ~/.local/bin/ && ~/.local/bin/uv --version
fi
cd ~ && rm -rf "$d"
```

Bun 一步要输出 `OK`、`digest OK` 和 `1.4.4`；`~/.bun/bin/bun` 已经存在时 Python 会报
`FileExistsError` 并停下，不会覆盖。uv 一步输出 `uv 0.13.6`（已有 uv 时是现有版本）。
Bun 不需要加进 `PATH`。

## 5. 写设置

几项默认开启的功能会和 workspace 的 owner 冲突，所以安装前先写好
`~/.claude-mem/settings.json`（文件已存在时这段会报 `FileExistsError` 并停下，
那时手动合并这些键，第 7 节会逐个核对）。值一律是 JSON 字符串：

```bash
python3 - <<'EOF'
import json, os
directory = os.path.expanduser("~/.claude-mem")
os.makedirs(directory, mode=0o700, exist_ok=True)
path = os.path.join(directory, "settings.json")
settings = {
    "CLAUDE_MEM_PROVIDER": "claude",
    "CLAUDE_MEM_MEMORY_INSTRUCTIONS_ENABLED": "false",
    "CLAUDE_MEM_WORK_STATE_ENABLED": "false",
    "CLAUDE_MEM_WORK_VIEW_AUTO_REFRESH": "false",
    "CLAUDE_MEM_WELCOME_HINT_ENABLED": "false",
    "CLAUDE_MEM_CONTEXT_OBSERVATIONS": "10",
    "CLAUDE_MEM_CONTEXT_SESSION_COUNT": "3",
    "CLAUDE_MEM_FILE_READ_GATE_ENABLED": "false",
    "CLAUDE_MEM_FOLDER_CLAUDEMD_ENABLED": "false",
    "CLAUDE_MEM_DELIVERABLES_ENABLED": "false",
    "CLAUDE_MEM_REDACT_ENABLED": "true",
    "CLAUDE_MEM_REDACT_GENERIC_ENABLED": "true",
}
with open(path, "x") as stream:
    json.dump(settings, stream, indent=2)
    stream.write("\n")
os.chmod(path, 0o600)
print("written", path, len(settings), "keys")
EOF
```

| 键 | 为什么这样设 |
|---|---|
| `CLAUDE_MEM_PROVIDER` | 笔记由该账号的 Claude 订阅生成（默认模型 `haiku`，占用订阅额度），工具输出只发给 Anthropic，不发给托管 observer 等其他服务 |
| `CLAUDE_MEM_MEMORY_INSTRUCTIONS_ENABLED` | 默认开启；注入的说明会让 agent 用 `save_memory` 记偏好、纠正和决定，形成第二个 owner |
| `CLAUDE_MEM_WORK_STATE_ENABLED` | 默认开启；启动时注入工作状态并提供 `work_state_*` 工具，和计划、backlog 重复 |
| `CLAUDE_MEM_WORK_VIEW_AUTO_REFRESH` | 默认开启；worker 启动时和之后每 10 分钟检查一次，有待处理的（新库的第一次检查、未归组的新会话、超过一天未更新的目标）就用已登录的 Claude Code、Codex 或 Gemini 跑一次后台任务，更新目标时还读取默认的 `~/.claude/projects`、`~/.codex/sessions`、`~/.gemini` 等记录 |
| `CLAUDE_MEM_WELCOME_HINT_ENABLED` | 默认开启；新项目第一次会话注入一段推荐 `/learn-codebase` 并带 cmem.ai 试用广告的提示；关掉后注入的是简短的空状态 |
| `CLAUDE_MEM_CONTEXT_OBSERVATIONS`、`CLAUDE_MEM_CONTEXT_SESSION_COUNT` | 默认在启动时注入最多 50 条笔记和 10 个会话摘要，截到 hook 的 10,000 字符上限；降到 10 条和 3 个，只留简短提醒，其余靠检索。不要设成 0：那样注入的是 "No previous sessions found."，会让 agent 以为没有历史可查 |
| `CLAUDE_MEM_FILE_READ_GATE_ENABLED` | 默认开启；主会话整文件读取 32 KB 以上、已有笔记且之后没改过的代码文件时，返回笔记时间线而不是文件内容 |
| `CLAUDE_MEM_FOLDER_CLAUDEMD_ENABLED` | 默认关闭，保持关闭；打开后会往目录里写 `CLAUDE.md`，和项目入口文件冲突 |
| `CLAUDE_MEM_DELIVERABLES_ENABLED` | 默认开启；每轮结束时把产出文件复制到 `~/.claude-mem/deliverables/`，在项目外多出副本 |
| `CLAUDE_MEM_REDACT_ENABLED`、`CLAUDE_MEM_REDACT_GENERIC_ENABLED` | 默认关闭；工具输出会明文入库并发给笔记模型，打开后先替换常见的凭据格式 |

然后在配置目录的 `settings.json` 里加两样东西：

- `env.CLAUDE_MEM_DISABLE_FILE_CONTEXT = "1"`：读文件前注入笔记历史的 hook 只认环境
  变量，不读上面的设置文件；Claude Code 把这个 `env` 交给会话和它的 hooks。设了之后，
  读文件前不再注入历史，read gate 也不再拦截。
- `permissions.deny` 里的拒绝规则：插件带 30 个 skill，全部允许模型自动调用。按
  `claude-runtime.md` 的标准（看 skill 默认会做什么）拒绝其中 20 个，每个两条
  （`Skill(claude-mem:<名字>)` 拦不带参数的调用，`Skill(claude-mem:<名字> *)` 拦带
  参数的调用）。分组如下：
  - 接管 owner 管的工作：规划、执行和审查（`make-plan`、`do`、`build`、`standup`、
    `pathfinder`、`design-is`，以及每小时巡检规则和 worker 的 `ccs-align`），交接
    （`handoff`），发布（`build-and-release`、`release`、`version-bump`、
    `childhood`），目标和进度（`owner-goals`、`request-progress`）；
  - 写 GitHub 或其他外部服务、或安装软件：`babysit`、`oh-my-issues`（GitHub），
    `cloud-sync`（cmem.ai），`wowerpoint`（装 Playwright 并上传到 Google
    NotebookLM），`mode-creator`（Telegram 告警，重启 worker）；
  - 把整个仓库读进会话：`learn-codebase`。

  保留的 10 个是 `mem-search`、`knowledge-agent`、`timeline-report`、
  `weekly-digests`、`agent-cost-report`、`backup-setup`、`smart-explore`、
  `screenpipe`、`what-the`、`how-it-works`。其中 `knowledge-agent` 只在被调用时
  启动它自己的会话；`agent-cost-report` 的 `--classify` 会把记录片段发给
  OpenRouter，默认关闭且需要密钥，不要打开。拒绝只挡调用，这些 skill 的描述仍在
  每个会话里（全部 30 个约 2,900 token）。

```bash
python3 - "$cfg/settings.json" <<'EOF'
import json, os, sys
path = sys.argv[1]
data = json.load(open(path)) if os.path.exists(path) else {}
denied = ["make-plan", "do", "build", "standup", "pathfinder", "design-is", "ccs-align",
          "handoff", "build-and-release", "release", "version-bump", "childhood",
          "owner-goals", "request-progress", "babysit", "oh-my-issues", "cloud-sync",
          "wowerpoint", "mode-creator", "learn-codebase"]
environment = data.setdefault("env", {})
permissions = data.setdefault("permissions", {})
deny = permissions.setdefault("deny", []) if isinstance(permissions, dict) else None
if not isinstance(environment, dict) or not isinstance(deny, list):
    sys.exit("refusing: env, permissions or permissions.deny has an unexpected type")
environment["CLAUDE_MEM_DISABLE_FILE_CONTEXT"] = "1"
for name in denied:
    for rule in (f"Skill(claude-mem:{name})", f"Skill(claude-mem:{name} *)"):
        if rule not in deny:
            deny.append(rule)
mode = os.stat(path).st_mode & 0o777 if os.path.exists(path) else 0o600
temporary = path + ".tmp"
with open(temporary, "w") as stream:
    json.dump(data, stream, indent=2)
    stream.write("\n")
os.chmod(temporary, mode)
os.replace(temporary, path)
print(sum(rule.startswith("Skill(claude-mem:") for rule in deny), "claude-mem deny rules")
EOF
```

应输出 `40 claude-mem deny rules`。`env` 和 `permissions` 不属于 workspace-meta 的
托管区域，`make sync` 会保留它们。

## 6. 安装

依次运行。安装那一行只在第 5 节的两份设置都在时才执行。安装中途失败后重试，从
第 4 节开始（第 3 节的备份保留不动）：

```bash
cd "$HOME"
DO_NOT_TRACK=1 npx --yes "claude-mem@$ver" telemetry disable </dev/null
grep -q '"CLAUDE_MEM_DISABLE_FILE_CONTEXT"' "$cfg/settings.json" && test -f ~/.claude-mem/settings.json &&
  CI=1 DO_NOT_TRACK=1 CLAUDE_CONFIG_DIR="$cfg" npx --yes "claude-mem@$ver" install --ide claude-code --provider claude --no-auto-start </dev/null
python3 - "$cfg/plugins/known_marketplaces.json" <<'EOF'
import json, os, sys
path = sys.argv[1]
data = json.load(open(path)) if os.path.exists(path) else {}
if "thedotmack" not in data:
    print("thedotmack not registered; nothing to change")
else:
    data["thedotmack"]["autoUpdate"] = False
    json.dump(data, open(path, "w"), indent=2)
    print("thedotmack autoUpdate off")
EOF
```

几个参数的原因：

- `telemetry disable` 把 `enabled: false` 写进 `~/.claude-mem/telemetry.json`，worker
  也按它关闭；安装时的 `DO_NOT_TRACK=1` 只管安装器本身，不会保存下来。
- `CI=1`：claude-mem README 里的 `CLAUDE_MEM_ONLINE_OPTIN=false` 在 15.8.0 里没有任何
  代码读取。只有 `CI` 能挡住安装结束时向 cmem.ai 发送主机名的请求；`CI` 在安装器里
  没有别的写入作用。
- `--ide claude-code` 和 `</dev/null`：在终端里交互运行时，安装器会预选检测到的所有
  工具，本机装了 Codex 就会修改 `~/.codex/config.toml`。非交互运行时 auto memory
  自动保留，不要加 `--disable-auto-memory`。
- `--no-auto-start`：安装中途失败后重跑时，不会顺带启动 worker。
- 最后一段关闭自动更新，安装失败时也要运行（`thedotmack` 在安装早期就写入了）。
  安装器每次运行都会把它重写为 `true`；Claude Code 会在新会话收到第一条消息后检查
  自动更新，所以从安装到这一段之间不要开新会话。

安装器最后打印的 Next Steps 不用照做：worker 由第一次会话启动，不需要
`npx claude-mem start`；`/learn-codebase` 已被拒绝。

## 7. 检查

先检查配置，再开第一次会话：

```bash
python3 - "$cfg" <<'EOF'
import json, os, sys
cfg = sys.argv[1]
marketplaces = json.load(open(os.path.join(cfg, "plugins/known_marketplaces.json")))
settings = json.load(open(os.path.join(cfg, "settings.json")))
telemetry = json.load(open(os.path.expanduser("~/.claude-mem/telemetry.json")))
claude_mem = json.load(open(os.path.expanduser("~/.claude-mem/settings.json")))
expected = {
    "CLAUDE_MEM_PROVIDER": "claude", "CLAUDE_MEM_MEMORY_INSTRUCTIONS_ENABLED": "false",
    "CLAUDE_MEM_WORK_STATE_ENABLED": "false", "CLAUDE_MEM_WORK_VIEW_AUTO_REFRESH": "false",
    "CLAUDE_MEM_WELCOME_HINT_ENABLED": "false", "CLAUDE_MEM_CONTEXT_OBSERVATIONS": "10",
    "CLAUDE_MEM_CONTEXT_SESSION_COUNT": "3", "CLAUDE_MEM_FILE_READ_GATE_ENABLED": "false",
    "CLAUDE_MEM_FOLDER_CLAUDEMD_ENABLED": "false", "CLAUDE_MEM_DELIVERABLES_ENABLED": "false",
    "CLAUDE_MEM_REDACT_ENABLED": "true", "CLAUDE_MEM_REDACT_GENERIC_ENABLED": "true",
}
print("autoUpdate:", marketplaces["thedotmack"].get("autoUpdate"))
print("enabled:", settings.get("enabledPlugins", {}).get("claude-mem@thedotmack"))
print("file-context switch:", settings.get("env", {}).get("CLAUDE_MEM_DISABLE_FILE_CONTEXT"))
print("deny rules:", sum(rule.startswith("Skill(claude-mem:") for rule in settings.get("permissions", {}).get("deny", [])))
print("telemetry enabled:", telemetry.get("enabled"))
print("settings mismatches:", {key: claude_mem.get(key) for key, value in expected.items() if claude_mem.get(key) != value} or "none")
EOF
if [ "$cfg" = "$HOME/.claude" ]; then claude plugin details claude-mem@thedotmack; else CLAUDE_CONFIG_DIR="$cfg" claude plugin details claude-mem@thedotmack; fi
cd "$HOME/workspace" && make agent-sync-check
```

应依次看到 `False`、`True`、`1`、`40`、`False` 和 `settings mismatches: none`；
`claude plugin details` 列出组件和每个会话固定增加的 token 数；`agent-sync-check`
返回 0，说明安装没碰 workspace-meta 的托管区域。

然后跑一次很小的会话，它会启动 worker（默认目录去掉 `CLAUDE_CONFIG_DIR=...`）：

```bash
t=$(mktemp -d) && cd "$t" && printf 'hello\n' > hello.txt
CLAUDE_CONFIG_DIR="$cfg" claude -p 'Run `printenv CLAUDE_MEM_DISABLE_FILE_CONTEXT`, read hello.txt, then call the Skill tool with skill "claude-mem:handoff". Report each result word for word.' --model haiku --allowedTools Read 'Bash(printenv:*)' Skill --max-turns 6 </dev/null
cd ~ && rm -rf "$t"
curl -s "http://127.0.0.1:$port/api/health"; echo
curl -s "http://127.0.0.1:$port/api/stats"; echo
CLAUDE_CONFIG_DIR="$cfg" DO_NOT_TRACK=1 npx --yes "claude-mem@$ver" doctor </dev/null
```

应看到：`printenv` 输出 `1`，文件读到 `hello`，`claude-mem:handoff` 返回
`Skill execution blocked by permission rules`；`/api/health` 的 `status` 是 `ok`；
`/api/stats` 的 `worker.port` 等于 `$port`、`database.path` 是
`~/.claude-mem/claude-mem.db`、`sessions` 至少为 1；`doctor` 显示
`All required checks passed.` 且 Worker daemon 一行是 ✓。在没有桌面的主机上看
viewer，先在自己电脑上开隧道 `ssh -L $port:127.0.0.1:$port <host>`，再打开
`http://127.0.0.1:$port/viewer`。

## 8. 升级

1. 读新版本的 release notes，按本 runbook 逐项核对键名、默认值、开关和自带 skill
   列表；新增的 skill 按 `claude-runtime.md` 的标准决定是否拒绝；
2. 退出所有使用 `$cfg` 的 Claude Code 会话，用第 9 节第一步的命令停 worker，等它
   退出；
3. 备份。claude-mem 的数据库和 chroma 只会向前迁移，新版本写过之后旧版本可能打不开：

   新版本号写进 `ver`，再运行（这是一条完整命令，复制时连同前面的 `ver=` 一起）：

```bash
ver="<新版本>"                       # 换成新版本号，例如 15.9.0
u="$cfg/backup-pre-claude-mem-$ver"
mkdir -m 700 "$u" && cp -a ~/.claude-mem "$u/claude-mem" &&
  for f in settings.json plugins/known_marketplaces.json plugins/installed_plugins.json; do cp -a "$cfg/$f" "$u/$(echo "$f" | tr / _)"; done &&
  ls -la "$u"
```

4. 用新的 `ver` 重跑第 6 节的安装和关闭自动更新两段（同样的环境变量和参数），按需
   补拒绝规则，再做第 7 节的检查（`doctor` 也用新的 `ver`）；
5. 通过 workspace-meta 的下一次改动更新本 runbook 记录的版本号。

退回旧版本：退出会话、停 worker 并等它退出，然后用第 3 步的备份还原，再把 `ver`
设回旧版本，重跑第 6 节并做第 7 节的检查：

```bash
u="$cfg/backup-pre-claude-mem-<新版本>"
test -d "$u/claude-mem" && rm -rf ~/.claude-mem && cp -a "$u/claude-mem" ~/.claude-mem &&
  for f in settings.json plugins/known_marketplaces.json plugins/installed_plugins.json; do cp -a "$u/$(echo "$f" | tr / _)" "$cfg/$f"; done &&
  rm -rf "$cfg/plugins/cache/thedotmack/claude-mem/<新版本>"
```

不要用 `npx claude-mem update` 或 `upgrade`：它们忽略所有参数，在终端里运行会预选
Codex，没有 `CLAUDE_CONFIG_DIR` 时装进 `~/.claude`。也不要用 `@latest`，它装的是没
核对过的版本。不要对 `thedotmack` 运行 `claude plugin update`、`/plugin` 里的
**Update now** 或 **Update marketplace**、不带名字的
`claude plugin marketplace update`：它们从 GitHub main 重新拉取，而 main 可能和同一
版本号的 release 代码不同。

## 9. 回滚

不要直接用 `npx claude-mem uninstall`：它会往 `~/.codex/config.toml` 追加两段配置并
运行 `codex plugin marketplace remove`；`telemetry.json` 不在时还会发送 telemetry。
手动回滚（先按第 2 节重新设好 `cfg`、`port` 和 `ver`）。

第一步，退出所有使用 `$cfg` 的 Claude Code 会话，否则下一条 prompt 或 MCP 调用会
重新拉起 worker；然后停 worker，并等它和 chroma-mcp 都真正退出（最多 30 秒）：

```bash
curl -s -X POST "http://127.0.0.1:$port/api/admin/shutdown"; echo
pid=$(python3 -c 'import json, os; print(json.load(open(os.path.expanduser("~/.claude-mem/worker.pid")))["pid"])' 2>/dev/null)
for i in $(seq 30); do
  if { [ -z "$pid" ] || ! kill -0 "$pid" 2>/dev/null; } && ! pgrep -u "$USER" -f '[c]hroma-mcp' >/dev/null; then echo "worker stopped"; break; fi
  sleep 1
done
ss -ltn | grep ":$port " || echo "port free"
```

应看到 `worker stopped` 和 `port free`；没看到就不要继续。

第二步，从配置目录删掉这次加的条目。`installed_plugins.json` 只有在安装前不存在、
现在又只剩空表时才删除；最后和第 3 节的备份对比，应输出 `True`：

```bash
python3 - "$cfg" <<'EOF'
import json, os, sys
cfg = sys.argv[1]
absent = open(os.path.join(cfg, "backup-pre-claude-mem", "absent.txt")).read().splitlines()
path = os.path.join(cfg, "settings.json")
data = json.load(open(path))
data.get("enabledPlugins", {}).pop("claude-mem@thedotmack", None)
data.get("env", {}).pop("CLAUDE_MEM_DISABLE_FILE_CONTEXT", None)
permissions = data.get("permissions", {})
if "deny" in permissions:
    permissions["deny"] = [rule for rule in permissions["deny"] if not rule.startswith("Skill(claude-mem:")]
    if not permissions["deny"]:
        del permissions["deny"]
for key in ("enabledPlugins", "env", "permissions"):
    if key in data and not data[key]:
        del data[key]
json.dump(data, open(path, "w"), indent=2)
path = os.path.join(cfg, "plugins/known_marketplaces.json")
if os.path.exists(path):
    data = json.load(open(path))
    data.pop("thedotmack", None)
    json.dump(data, open(path, "w"), indent=2)
path = os.path.join(cfg, "plugins/installed_plugins.json")
if os.path.exists(path):
    data = json.load(open(path))
    data.get("plugins", {}).pop("claude-mem@thedotmack", None)
    if not data.get("plugins") and "absent " + path in absent:
        os.remove(path)
        print("removed", path)
    else:
        json.dump(data, open(path, "w"), indent=2)
EOF
python3 -c 'import json, sys; print(json.load(open(sys.argv[1])) == json.load(open(sys.argv[2])))' "$cfg/backup-pre-claude-mem/settings.json" "$cfg/settings.json"
```

第三步，删除插件文件，以及安装前不存在的 Bun、uv 和缓存（还想保留它们就跳过
`for` 那几行）。`plugins/cache` 和 `plugins/data` 只在安装前不存在、现在又已经空了时
删除，其他插件放在里面的东西不受影响：

```bash
b="$cfg/backup-pre-claude-mem"
rm -rf "$cfg/plugins/marketplaces/thedotmack" "$cfg/plugins/cache/thedotmack" "$cfg/plugins/data/claude-mem-thedotmack" ~/.local/bin/claude-mem
for p in "$cfg/plugins/cache" "$cfg/plugins/data"; do
  [ -d "$p" ] && grep -qxF "absent $p" "$b/absent.txt" && rmdir "$p" 2>/dev/null && echo "removed empty $p"
done
for p in ~/.bun ~/.local/bin/uv ~/.local/bin/uvx ~/.cache/uv ~/.local/share/uv ~/.cache/chroma; do
  [ -e "$p" ] && grep -qxF "absent $p" "$b/absent.txt" && rm -rf "$p" && echo "removed $p"
done
grep -n 'Added by claude-mem installer' ~/.bashrc ~/.zshrc ~/.config/fish/config.fish 2>/dev/null || echo "no rc lines from claude-mem"
```

最后一行有输出时，用编辑器删掉那一行注释和紧跟的 `export PATH=...` 行。不再需要这些
历史时删除 `~/.claude-mem/`；插件 MCP 的日志在
`~/.cache/claude-cli-nodejs/*/mcp-logs-plugin-claude-mem-*`，npx 缓存在
`~/.npm/_npx/`，都可以按需清理。确认回滚无误后，再删除 `$cfg/backup-pre-claude-mem`。
