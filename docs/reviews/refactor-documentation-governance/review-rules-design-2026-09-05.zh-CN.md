# workspace-meta 规则设计审核报告

**审核日期**：2026-09-05
**审核类型**：documentation/governance（只读，未改动任何文件）
**轮次**：一轮广审 + 一轮定向复审，本报告为合并结论（复审中的两处更正已就地整合）

## 范围快照

- **目标仓库**：`/home/saberu/workspace`（workspace-meta，最近 Git 根）
- **对比基准**：`HEAD 185e641` + 当前工作树
- **范围内**：`.agents/rules/*.md`（16 个）及其载体 `CLAUDE.md`、
  `.agents/host-templates/codex-AGENTS.md`、`.agents/host-templates/README-agents.md`、
  `AGENTS.md`、`README.md`、`docs/architecture/codex-config-management.md`、
  `docs/runbooks/new-vps.md`、`feedback-register.md`、`tests/`、`scripts/bootstrap-local.sh`
- **仅作补充**：`docs/reviews/refactor-documentation-governance/`（plan + 两轮 changelog）
- **排除**：`docs/reviews/` 历史语料、`NanoPi_R6S*`、`projects/`

**判定标准**：项目自身的 `.agents/rules/documentation.md`（其来源为 Diátaxis / arc42 / ADR，
见 W-R38）加 `.agents/rules/rule-authoring.md`，而非外部另一套规范。

## 总体结论

规则设计整体**符合**标准文档规范，属于水准以上的信息架构。检出 **5 个 P1、6 个 P2**，
全部是自洽性缺口，无 P0。最严重的问题不在 `.agents/rules/` 内部，而在
`docs/architecture/codex-config-management.md` —— 它维护着规则层的平行副本且已实质分叉。

> **后续状态（2026-09-06）**：本报告保留审核时点的历史结论；修复与复验见
> [Round 3 remediation](round3-review-remediation-2026-09-06.changelog.md)。

---

## 符合的部分（有证据）

- **单一所有权**：16 个模块每个都有 `## Ownership`，并显式写出"不归我管"的边界
  （如 `authorization.md:12-14` 把 Git 程序推给 `git-*.md`、把密钥推给 `secrets.md`）。
  由 `tests/test_sync_codex_config.py:515` 强制。
- **任务切分是真 MECE**：`git.md` + 4 个动作模块，且有载荷剖面测试防串味 ——
  `force-with-lease` 只允许出现在 `git-recovery.md`、`gh pr create` 只允许出现在
  `git-publication.md`（`tests/…:615`）。这是这套规则里最扎实的设计。
- **真值分类分离**：当前指导在 `.agents/rules/`，来源溯源在 `feedback-register.md`
  （W-R 编号稳定、且明确声明"历史条目不等于现行政策"），决策/变更记录在 `docs/reviews/`。
- **不给永久性指南盖易变状态戳**：规则文件无 version/status 字段，正合
  `documentation.md:70-72`。
- **引用可解析**：机械扫描全部治理文档的仓内相对路径引用，无失效引用。
- **形制统一**：H1 + 一句范围描述 + `## Ownership` + 祈使句小节，正文折行 ≤80。
- **runbook 合规**：`docs/runbooks/new-vps.md` 结构（0 边界 / 1 前置条件 / 2-8 有序动作 /
  9 常见故障 / 10 安全和发布底线 / 11 交接记录模板）完全符合 `documentation.md:34`，
  且扫描无任何日期化观测。**同一个仓里标准是做得到的。**
- **模板无孤儿**：`env-sync-SKILL.md` 由 `scripts/bootstrap-local.sh:123` 正常安装。

---

## P1-1　架构文档是规则层的平行副本，且已实质分叉

`docs/architecture/codex-config-management.md:37-53` 维护着**第二份完整的规则所有权矩阵**
（中文），而 `README.md:78-80` 与 `:214-215` 两次声明
`.agents/host-templates/README-agents.md` 才是 canonical ownership matrix。
`round1` changelog 中 "updated the ownership matric**es**"（复数）说明这是被自觉手工同步的双份。

15 行中已有 8 行实质分叉，非翻译差异：

| 域 | `README-agents.md`（声明的权威） | 架构文档 |
|---|---|---|
| `git.md` | canonical remote and project facts | trunk 名称、CI/检查映射 |
| `git-branches.md` | topology, lifecycle, persistence, target | 分支拓扑、契约存放位置、归档工具 |
| `git-integration.md` | routes, topology, release/archive policy | 合并策略、受保护分支和 CI 门禁 |
| `planning.md` | artifact schema, sources, branch/live gates | 文件结构、项目来源、命令 |
| `verification.md` | commands, environments, thresholds, CI | 项目测试矩阵和功能入口 |
| `review.md` | domain scenarios, baseline, **risk refinements** | 领域场景和架构基线 |
| `capabilities.md` | project toolchain **and adapters** | 项目工具链 |
| `rule-authoring.md` | project-only owners and adapters | 项目反馈与本地路由 |

"项目可以补充什么"是规范性事实，现在有两个不同答案。因跨语言，`grep` 与现有测试均无法发现。

同一文件还承载：Git 任务路由表的第 4 份副本（`:69-75`，前三份在 `CLAUDE.md:26-31`、
`codex-AGENTS.md:28-31`、`README-agents.md`）、发布事务 Checkpoint A/B 的完整中文复述
（`:128-149`，权威在 `git-publication.md:22-52`）。

**违反**：`documentation.md:60-64`，以及该文件自己第 376-377 行
"不允许……通过复制共享授权、Git、计划或审查流程来建立第二个规则所有者"。

## P1-2　同一文件真值分类混装，含嵌入当前指导的日期化观测

`docs/architecture/codex-config-management.md` 一个文件同时是：
explanation（`:1-62`）、reference（仓库地图 `:151-171`）、how-to/runbook（操作手册 `:290-329`）、
troubleshooting（`:331-365`），并在当前指导中嵌入日期化实测结论
（`:350-354`「2026-07-11 在 Codex 0.144.1 上的实测中……」）。

**违反**：`documentation.md:46-58`（真值分类）与 W-R39 的 How to apply 原文
"re-audit every current owner for dated observations, event narration"。
该标准被完整施加给试点项目 NanoPi_R6S_Handbook，却未回施于 workspace-meta 自身。

## P1-3　workspace-meta 自己没有可执行文档闸门

`documentation.md:110-115` 要求文档密集型项目必须有项目自有的可执行闸门
（入口文件白名单、索引覆盖、内部链接与锚点、runbook 必需小节），W-R39 再次重申。

`round2` changelog 明写为 NanoPi_R6S_Handbook 建了该闸门并加了 GitHub Actions；
而 workspace-meta（约 70 个文档、且是该标准的**出产方**）的 `make test` 只有
sync/status 单测，`docs/` 下除 `docs/reviews/project-memory-governance/README.md`
外无任何索引，`.agents/rules/` 自身无索引。

若此处有同类闸门，P1-1 与 P1-4 均属可机检形态。

## P1-4　`documentation.md` 未被 Git 跟踪，而路由已经指向它

`.gitignore:48` 已放行，但文件仍是 UNTRACKED；同时 `CLAUDE.md:33` 与
`codex-AGENTS.md:34` 的路由行已写入（两者均为 modified）。
`git commit -a` 不带未跟踪文件，`.githooks/pre-commit` 只拦被 ignore 的路径，
没有任何机制保证"路由指向的规则文件存在且已跟踪"。

一旦适配器先发布，所有安装该托管 Codex 块的宿主机会拿到指向不存在文件的路由 ——
届时按 `review.md:56` 属 **P0**（routing that can place work on the wrong target）。

## P1-5　安全底线副本无归属源绑定

`tests/…:567-573` 只断言 `codex_floor == claude_floor`，即两份副本互测。
但 `rule-authoring.md:24` 要求 "tested against its canonical owner"，
`README-agents.md:49` 要求 "names its canonical owner and is tested for drift" —— 两条都未满足。

实际后果：`CLAUDE.md:10-11` 写 "never reset, clean, overwrite, move, hide, or delete"，
权威源 `git.md:43-44` 是 "Never reset, clean, overwrite, **switch away from**, move, hide,
or delete"。`git checkout/switch` 切走未识别工作恰是最常见的破坏路径，两个适配器都漏了，
而测试全绿。

> **证据性质说明**：`git log -L 43,44:.agents/rules/git.md` 与 `-L 10,11:CLAUDE.md` 显示
> 两者均创建于同一提交 `cd72c1c`，该动词从未出现在适配器底线中。所以这是**成文时的压缩遗漏**，
> 不是事后漂移。结论不变，但定性需准确。

---

## P2

1. **角色表重叠**：`implementation.md:29-37` 与 `documentation.md:30-40` 两张制品角色表在
   runbook / decision / changelog / contract↔reference 四类上重叠，且各写一遍
   "一个事实一个所有者"（`implementation.md:43-52` / `documentation.md:60-64`）。
   建议角色表只留在 `documentation.md`，`implementation.md` 保留 code/comment/test 行并引用前者。
2. **目录契约三种表述**：`CLAUDE.md:4-5` 与 `codex-AGENTS.md:4-6` 说 `.agents/rules/` 是纯
   agent-neutral；`README-agents.md:12` 说是 "portable owners plus explicit agent runtime
   modules"；架构文档 `:158-159` 又是第三种（也是最准确的一种）。
   同时结构不对称：Codex 有版本化 runtime 模块，Claude 的运行时机制只是路由表里一句内联从句。
3. **模块模板破例**：`documentation.md:1-3` 是唯一缺少 H1 后范围描述句的规则模块，
   其余 15 个都有 —— 而这句正是 agent 判断是否加载的依据。
4. **溯源映射过期**：`feedback-register.md:28` 仍只写 W-R38；W-R39 的规范内容
   （pointer 契约、可执行闸门）已落在 `documentation.md`，按 `planning.md:88-90` 应同轮同步。
   应改为 `| .agents/rules/documentation.md | W-R38, W-R39 |`。
5. **权威矩阵位置与角色不符**：`README-agents.md` 被 `README.md` 指定为权威所有权矩阵，
   却放在 `.agents/host-templates/` 下并以 README-agents 命名。
   `bootstrap-local.sh` 只安装 `codex-AGENTS.md`、`codex-hooks.toml`、`codex-preferences.toml`、
   `env-sync-SKILL.md` —— 该目录里唯独它不是宿主机模板。
6. **无语言策略声明**：规则/README/AGENTS 全英文，架构文档与 runbook 全中文。
   本身不违规，但它是 P1-1 分叉无法被机检发现的直接原因。

### 次要项

- `verification.md:14` 是唯一超过 80 列的正文行（81）。
- `.gitignore:65` 对 host-templates 用 `*.md` 通配，与 `README.md:213-215` 文档化的
  "每个规则文件一行 `!<file>`" 自定规则不一致；且无检查保证"已放行 ⇒ 已跟踪"。

> **定性更正**：`.gitignore` 逐条白名单本身是 `README.md:213-215` 文档化的**有意设计**
> （显式评审边界），不属于失控的人工副本，初审对此的定性已撤回。

---

## 已执行的检查

- `make test` → **56 passed**
- `git log -L` 追溯安全底线与 `git.md` 的成文史
- 两份所有权矩阵逐行对照
- 规则目录跟踪状态逐文件核对
- 治理文档仓内引用可解析性机械扫描（无失效引用）
- 正文列宽扫描
- `CLAUDE.md` / `codex-AGENTS.md` / `README-agents.md` / 架构文档四处路由表与安全底线逐条比对
- `feedback-register.md` 映射表与 W-R38/W-R39 落点比对
- `scripts/bootstrap-local.sh` 安装目标核对
- 两轮 changelog 的验证声称与实际比对（`make test` 56 passed 属实）

## 缺口

- 未审 `docs/reviews/` 历史语料的中英平行副本是否构成双语双权威（约 30 个 `.zh-CN.md`）。
- 未做 Codex/Claude 真实 UI 冒烟测试（按 `AGENTS.md` 属人工宿主验证，本次无法运行，
  报告为缺口而非通过）。
- `make test` 运行时向 stdout 泄漏一条 sync 报告（某调用 `main()` 的用例未重定向 stdout）；
  写入的是临时目录，不碰宿主机配置，属测试整洁度问题，未纳入本次范围。

## 建议修复顺序

1. **P1-1 + P1-2**：把架构文档的所有权矩阵、Git 路由表、发布事务复述替换为指向权威 owner
   的链接；把 `:350-354` 的日期化实测移入 `docs/reviews/` 的验证记录。
   这一步同时消掉两个 P1 和 P2-2 的一半。
2. **P1-4 + P1-5**：新增 `tests/test_governance_docs.py`，把
   "路由行 ⇒ 文件存在且已跟踪"、"底线条目 ⇒ 归属源"变成机检。
3. **P1-3**：将上一步扩成完整文档闸门（入口白名单、索引覆盖、链接锚点、日期分离）。
4. **P2-3 / P2-4**：两处一行修改，可随任意一轮附带。
