# Claude/Codex 配置管理架构

本文说明 workspace-meta 如何把跨项目治理规则安装到本机 Claude Code 和
Codex，同时避免把凭据、授权、信任状态和运行时数据同步到其他机器。

## 一句话模型

Git 仓库保存“应当如何安装”的模板和脚本；`make bootstrap` 只收敛明确归
workspace-meta 所有的配置面；用户目录中其余内容始终由当前主机维护。

## 配置分层

| 层级 | 内容 | 所有者 | 同步方式 |
|---|---|---|---|
| workspace-meta | 跨项目方法、模板、安装器、状态评估器、规则来源 | 本仓库 | Git 私有远端 |
| Codex 全局指导 | `~/.codex/AGENTS.md` 中的标记块 | workspace-meta + 主机 | `make bootstrap` 只替换标记块 |
| Codex 全局配置 | `~/.codex/config.toml` 中的标记 hook 块 | workspace-meta + 主机 | `make bootstrap` 只替换标记块 |
| Claude 全局配置 | `~/.claude/settings.json` 中一个专用 SessionStart 组 | workspace-meta + 主机 | `make bootstrap` 收敛该组，保留其他键和组 |
| 项目配置 | 项目的 `AGENTS.md`、`.agents/`、`.codex/` | 项目仓库 | 项目自己的 Git |
| 主机私有状态 | 凭据、模型偏好、信任 hash、审批规则、历史、缓存、数据库 | 当前主机 | 不同步 |

“混合所有权”不是复制整个文件。它表示 workspace-meta 只拥有文件中一个可
识别的区域，安装器必须保留区域外的内容。

## 仓库地图

| 路径 | 作用 |
|---|---|
| `AGENTS.md` | 本仓库自己的 Codex 开发与交付约束 |
| `.agents/host-templates/codex-AGENTS.md` | 安装到 Codex 全局 `AGENTS.md` 的标记块 |
| `.agents/host-templates/codex-hooks.toml` | Codex SessionStart 标记块模板 |
| `.agents/host-templates/README-codex.md` | 精简的所有权矩阵 |
| `scripts/workspace_status.py` | Claude/Codex 共用的状态评估策略 |
| `scripts/sync_codex_config.py` | 渲染、迁移、校验并写入三个主机目标 |
| `scripts/bootstrap-local.sh` | 一台机器的安装入口 |
| `tests/test_workspace_status.py` | 状态顺序、离线降噪和输出契约测试 |
| `tests/test_sync_codex_config.py` | 安装、迁移、保留、拒绝和幂等测试 |
| `docs/reviews/` | 非小型变更的计划与每轮 changelog |

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

当前官方 hooks 文档明确说明：`SessionStart` 的 JSON `systemMessage` 会显示为
UI 或事件流 warning，而纯文本 stdout 会进入额外 developer context。Codex
0.144.1 的对应实现也与此一致，可查看该版本源码
`codex-rs/hooks/src/events/session_start.rs`。这证实了本项目统一使用 JSON 的
协议选择，不再只是由配置 schema 推断。

## 同步与迁移

`scripts/sync_codex_config.py` 先在内存中完成三个目标的渲染和结构校验：

1. Codex `AGENTS.md`：验证标记唯一且有序；替换旧标记块，或在首次安装时
   追加并保留现有用户指导。
2. Codex `config.toml`：渲染 hash-pinned 命令，移除完全归 workspace-meta
   所有的旧 hook 组，插入新标记块，再用 `tomllib` 解析整个结果。
3. Claude `settings.json`：解析整个 JSON，移除完全归 workspace-meta 所有的
   旧组，在原位置插入一个新组，再序列化完整结果。

只有三个目标全部通过校验后才开始原子写入。如果写入中途出现操作系统错误，
同步器会尽力恢复本轮已经写过的目标。它不是跨文件系统事务，但避免了已知的
“先写 AGENTS、后发现 JSON/TOML 无效”的部分升级。

### 拒绝而不是猜测

若同一个 SessionStart group 同时包含 workspace-meta handler 和用户 handler，
同步器会报错并且不写任何目标。需要人工先把两类 handler 拆成独立 group。
这是所有权边界不明确，自动删除或改写都有丢配置风险。

旧的三个独立 workspace-meta hook 会自动迁移为一个 handler。Codex 旧 trust
索引可能成为孤立记录，但它属于主机状态且不影响运行，本项目不会删除。

## 操作手册

### 新机器

```bash
git clone https://github.com/taoziyoyo2566/workspace-meta.git ~/workspace
make -C ~/workspace bootstrap
```

然后在 Codex 中运行 `/hooks`，审查并信任 workspace-meta SessionStart hook。

### 日常升级

```bash
git -C ~/workspace pull
make -C ~/workspace agent-sync-check
make -C ~/workspace bootstrap
```

`agent-sync-check` 只报告漂移，返回 0 表示三个托管目标均已收敛；非零表示
存在漂移或输入无效。`bootstrap` 才会写主机配置。

### 修改本项目

```bash
make test
bash -n scripts/*.sh .githooks/pre-commit
python3 -m py_compile scripts/*.py tests/*.py
git diff --check
```

非小型治理变更还需在 `docs/reviews/<topic>/` 写 plan 和 round changelog。
除非用户明确要求，不自动 commit 或 push；交付时必须报告未提交/未推送状态。

## 故障排查

### `agent-sync-check` 返回非零

先阅读三行目标状态。若只是 `installed or updated`，运行 `make bootstrap`。
若提示 invalid JSON/TOML，先修复对应主机文件语法；同步器不会覆盖无效输入。

### 提示 mixed hook group

打开对应的 Claude JSON 或 Codex TOML，把 workspace-meta command 与用户 command
拆成不同 SessionStart group，然后重新运行 bootstrap。不要删除无法识别的用户
handler 来换取通过。

### Codex hook 不触发

运行 `/hooks` 检查新命令是否已信任。每次状态评估器 hash 改变都需要重新审查。
同时检查 `~/.codex/AGENTS.override.md`；非空 override 会让全局 `AGENTS.md` 基线
失效，但不会影响 hook 本身。

不要把 `--dangerously-bypass-hook-trust` 当作 UI 验收的替代。2026-07-11 在
Codex 0.144.1 上的实测中，`/hooks` 正确显示一个待审查 SessionStart hook，
但一次性 bypass 会话没有在 TUI 或 `exec --json` 事件流中暴露该 hook 的
`systemMessage`，尽管同一安装命令直接执行会输出正确 JSON。最终 UI smoke
应在操作者通过 `/hooks` 持久信任后，用一个全新会话完成。

### 每次离线都提示

检查 `~/.cache/workspace-meta/status.json` 是否可写、系统时间是否合理。远端失败
默认 24 小时只提示一次；其他持续状态按设计每次提示。

### Python 不满足要求

安装器要求 Python 3.11+，因为使用标准库 `tomllib` 校验完整 Codex 配置。前置
条件不满足时 bootstrap 会跳过 agent 同步并明确警告，不会退化为未经校验的
字符串追加。

## 明确不做的事

- 不同步 `~/.codex/rules/default.rules`、`auth.json`、数据库、日志或历史。
- 不同步模型选择、project trust、hook trust hash 或 Claude/Codex 凭据。
- 不自动 pull、commit、push、解决冲突或信任 hook。
- 不把项目专用规则提升到全局；它们应留在项目自己的治理文件中。
- 不保证所有 agent 版本都具有相同 hook stdout 协议；升级 Codex 后应重新核对
  官方 hooks 文档或对应版本实现并做一次真实 SessionStart UI smoke test。

## 参考

- Codex hooks 与 stdout 协议：<https://developers.openai.com/codex/hooks>
- Codex 内联 hooks 配置：<https://developers.openai.com/codex/config-advanced#hooks>
- Codex 配置参考：<https://developers.openai.com/codex/config-reference#configtoml>
- Codex `AGENTS.md` 指导：<https://developers.openai.com/codex/concepts/customization#agents-guidance>
- 本次协议核验源码：<https://github.com/openai/codex/blob/rust-v0.144.1/codex-rs/hooks/src/events/session_start.rs>
- 决策来源：`feedback-register.md` 的 W-R28
