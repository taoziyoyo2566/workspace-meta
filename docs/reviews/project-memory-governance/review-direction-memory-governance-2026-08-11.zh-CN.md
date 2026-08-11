# 对 Memory Governance program 的方向与可行性审查

Status: 审查备忘录；由 AI 会话产出。本文审查的对象不是 v0.1.1 文本的合规性，
而是本 program 的方向、交付物形态和可实施性。本文不构成操作者批准，不授权协议
安装、`.agents/` 变更、`.gitignore` 变更、项目迁移或 Git 发布，也不修改任何
Protocol、计划或历史文档正文。

Date: 2026-08-11

审查对象：

- [memory-governance-protocol-v0.1.1-2026-08-09.zh-CN.md](memory-governance-protocol-v0.1.1-2026-08-09.zh-CN.md)（Active working source，`MGP-v0.1.1`）
- [plan-memory-governance-v0.1.1-2026-08-09.zh-CN.md](plan-memory-governance-v0.1.1-2026-08-09.zh-CN.md)（Active plan）
- 本目录全部 22 份 Markdown 文档，作为 program 产出总体

对照材料：

- `~/workspace/.agents/rules/rule-authoring.md`（规则形态与来源证据的所有者）
- `~/workspace/feedback-register.md`（W-R24、W-R27）
- `~/workspace/CLAUDE.md`、`~/workspace/.agents/host-templates/codex-AGENTS.md`（规则路由）
- `~/workspace/projects/reality-ops/`（独立 Git 根，supplemental；见 §6 边界）
- Claude Code 与 Codex 官方 Memory 文档（2026-08-11 本轮实抓）

## 1. 总体判定

v0.1.1 的**文本质量没有问题**，问题在**交付物形态与范围划分**。

本轮判定：**不建议按当前计划推进到 Phase 1 之后的版本轮次**。理由不是文档写得
不好，而是三条可由证据直接复核的结构性问题：

1. 本 program 唯一已存在、已在 CI 强制执行的 memory 门禁，被协议用 D05 划到范围外；
2. 协议的标识符与并发机器要求其预定执行者（读取规则文件的 agent）执行确定性
   密码学计算与两阶段状态机，而承担该计算的脚本被协议自己推迟；
3. 本 program 没有引用任何源事件，不满足本工作区自己的规则写作方法
   （`rule-authoring.md` 与 W-R27）。

同时，协议的**核心原则是正确的**，并且与两家厂商的官方立场独立吻合（见 §4）。
建议的处置不是废弃思考成果，而是改变交付物形态——详见 §5，本文不执行任何变更。

## 2. 审查方法与可复算证据

本文每条结论都可由下列命令在本机复算。审查为只读，未修改任何被审查文件。

| # | 命令 | 本轮结果 |
|---|---|---|
| C1 | `git -C projects/reality-ops log -1 --format='%h'` | `7e93c01` |
| C2 | `git -C projects/reality-ops rev-list 7e93c01..HEAD --count` | `0` |
| C3 | `grep -rc "W-R" docs/reviews/project-memory-governance/*.md \| awk -F: '{s+=$2} END{print s}'` | `0` |
| C4 | 同上，关键词换 `源事件` / `feedback-register` | `0` / `0` |
| C5 | `wc -c` 协议与最大既有规则 | `33978` / `7159`（`authorization.md`） |
| C6 | `cat docs/reviews/project-memory-governance/*.md \| wc -l`；`ls *.md \| wc -l` | `7438` 行 / `22` 份 |
| C7 | 协议 D 表 `:74-85` 状态计数 | `11 proposed` + `1 deferred`，`0 accepted` |
| C8 | `grep -c "stale\|重验\|TTL\|contradicted"` 协议全文 | `12` 行 |
| C9 | `make test`（workspace-meta） | 28 项通过 |

未执行、因而不得计为通过的项：`make bootstrap`、隔离 HOME 双跑、第 12 节任何
fixture、reality-ops 的 `check-project-memory.sh` 实跑、以及 §1.1 四条官方引文中
未抓取的两条（OpenAI Cookbook、AGENTS.md 文档）。

## 3. 发现

### P1-1：唯一已落地的机械门禁被划在协议范围外

协议 `:42` 自述：「需要无条件阻断的行为必须由权限系统、hook、脚本或其他机械
门禁负责；本协议只规定 Memory 内容如何被管理和使用。」

该机械门禁**已经存在并在运行**，位置在 reality-ops：

| 事实 | 证据 |
|---|---|
| 项目 memory 文件存在，279 行，带日期戳 | `projects/reality-ops/docs/project-memory.md:3`（`Last updated: 2026-08-07 JST`） |
| 其声称的 HEAD 与实际一致，未漂移 | `:8` 声称 `7e93c01`；C1/C2 实测 `7e93c01`、0 条新提交 |
| 加载纪律已成文 | `projects/reality-ops/AGENTS.md:3`（`## Project memory loading`） |
| 维护触发与四条更新要求已成文 | 同上 `:16`（`## Project memory maintenance`） |
| **门禁由 CI 按变更 range 强制执行** | 同上 `:39`；`projects/reality-ops/.github/workflows/quality.yml:58,60,62` 三处调用 `./scripts/check-project-memory.sh --range ...` |
| 门禁脚本存在且可执行 | `projects/reality-ops/scripts/check-project-memory.sh`，2853 B，`-rwxrwxr-x` |
| 该实现**没有**使用协议的重型机器 | 无 `docs/project-memory/` history 目录；文件内无 `claim_id`、`operation_key`、ULID |

而协议 `:78` 将其定性为「D05 | Reality Ops checker 属于独立项目适配器，**不是通用
协议门禁**」，`:589` 进一步把它交回独立仓库。

净效果：**program 把已经验证可行、且是唯一具备强制力的组件排除在交付范围外，
把无法自我强制的部分作为全部交付物。** 这是范围划分错误，不是文本缺陷。

补充：该实现对协议 §7.4「首次实质性任务」的处理也更严格——
`AGENTS.md:44-46` 明确「Pure explanation, review, or unrelated documentation tasks
do not require a memory rewrite」和「Do not invent a memory update merely to change
the timestamp」，后者是协议正文没有的反模式约束。

### P1-2：标识符与并发机器没有可执行载体

协议要求的三项计算：

| 要求 | 位置 |
|---|---|
| 对规范 JSON 计算 SHA-256，输出 `reconcile-sha256:<64 位小写十六进制>` | `:495-505` |
| 生成 26 位 Crockford Base32 ULID，并做作用域内唯一性扫描 | `:265` |
| 两阶段写入状态机（prepared → 并发复核 → 更新 → applied） | `:528-541` |

协议的安装目标是 `:664` / `:694` 的 `.agents/rules/memory-protocol.md`，即由 agent
读取的规则文件（`CLAUDE.md:39`：「Read only the task-shaped owners」）。规则文件
约束的是行为，无法承载确定性密码学计算。

承担该计算的载体被协议自己推迟：`:697` 将「接入 SessionStart、hook、脚本或数据库」
列为「必须在协议和 fixture 评审后另行授权」的工作。

因此 Active plan `:159-162` 的 Phase 4「单项目最小垂直切片」在当前排序下没有前置：
要验证 `operation_key`、`claim_id` 和两阶段恢复，必须先有计算它们的程序，而该程序
的授权被排在其后。这是计划内部的顺序矛盾，不是实现细节。

说明其边界：并非无法解决——可以为 fixture 现写临时脚本。但协议未指定执行载体、
计划未为其安排阶段，因此**当前形态下 Phase 4 的前置条件不成立**。

### P1-3：无源事件，不满足本工作区自身的规则写作方法

`.agents/rules/rule-authoring.md:39` 定义 `## Match Form To Failure`，`:60` 规定
「the source incident is the normal baseline evidence」。`feedback-register.md:104`
的 W-R27（2026-06-26）把它写成强要求：「**the register's source-incident IS the
baseline test**」。

实测（C3/C4）：本目录 22 份文档中，`W-R` 引用 **0** 处，`源事件` **0** 处，
`feedback-register` **0** 处。整个 program 由第一性原理与官方文档推导，未锚定任何
观察到的失效。

公平说明：W-R27 的字面触发条件是「routing feedback into a new or edited
behavior-shaping rule」，本 program 并非从 register 路由而来。但其安装目标
（`:664`）是行为规则，因此形态-失效匹配的要求仍然适用。

### P2-1：规范重心与唯一有记录的真实失效不成比例

`feedback-register.md:93-95` 的 W-R24（2026-06-10）记录了本工作区唯一一条有日期、
有源事件的 memory 失效：一个 memory 文件写着「Do not re-discover this each session
— assume it」，Docker 装好后该记忆从不自更新，污染了一份 L2 计划。**失效类型是
陈旧（staleness）。**

协议篇幅分配（按章节行区间计，总 739 行）：

| 内容 | 行区间 | 行数 |
|---|---|---|
| §6.2 `claim_id` | 261-288 | 28 |
| §6.3 完整 history 事件 | 289-321 | 33 |
| §9 History、并发和恢复 | 460-544 | 85 |
| **小计（标识符/事件/并发/幂等/恢复）** | | **146（19.8%）** |
| 陈旧与重验相关（关键词命中行，C8） | 分散 12 处 | **12** |

方法披露：146 是章节行数，12 是关键词命中行数，两者口径不同，比较为指示性而非
精确。即便如此，量级差异（约 12:1）明确。

**反向公平核对**：fixture 层面并不失衡。`:623-638` 的 14 个场景中，陈旧相关
（MGP-06 冲突标记、MGP-09 TTL）与并发/恢复相关（MGP-10、MGP-11）各 2 个。
失衡出现在规范正文体量，不在场景覆盖。

### P2-2：规范体量与厂商官方形态指引冲突

协议 33978 B（C5），是本工作区现有最大规则 `authorization.md`（7159 B）的 **4.7 倍**。

Claude Code 官方文档（`https://code.claude.com/docs/en/memory`，本轮 2026-08-11 实抓）
对行为指令文件的形态指引：

> **Size**: target under 200 lines per CLAUDE.md file. Longer files consume more
> context and reduce adherence.

以及对强制力的定位：

> Claude treats them as context, not enforced configuration. To block an action
> regardless of what Claude decides, use a PreToolUse hook instead.

> Settings rules are enforced by the client regardless of what Claude decides to
> do. CLAUDE.md instructions shape Claude's behavior but are not a hard
> enforcement layer.

引用边界说明：该 200 行指引是针对 `CLAUDE.md` 给出的，不是对任意规则文件的通用
上限，故此项记为 P2 而非 P1。但其原理（长文件降低遵循度）与本协议的安装形态直接
相关。

**更正上一轮口径**：上一会话曾把该体量描述为 always-on token 成本。这不准确——
`CLAUDE.md:39` 表明 `.agents/rules/*` 由 agent 按任务形态**按需读取**，非常驻加载。
成本是每次 memory 任务一次性读取，不是每会话常驻。此更正不改变 P2-2 的结论方向，
但改变其量级，特此撤回原表述。

### P2-3：目标形态已存在，却被排在最后阶段

Active plan `:169-172` 把 Reality Ops 迁移列为 Phase 6，位于安装（Phase 3）和垂直
切片（Phase 4）之后。但按 §3 P1-1 的证据，该项目已具备可工作的完整实例：文件 +
契约 + CI 门禁，且事实准确性经 C1/C2 实测成立。

由此产生的顺序问题：唯一的真实运行样本被安排在设计验证的**最后**，而不是作为
设计输入。协议 `:20-22` 明确「Ansible 是第一个用于验证协议的真实案例，不是协议的
领域核心」——该定位本身可以成立，但当通用协议尚无任何执行实例、而领域实例已经跑通
时，把实例排在第六阶段会使前五个阶段失去经验校准。

### P2-4：program 产出与收敛度不成比例（过程观察）

| 度量 | 值 | 来源 |
|---|---|---|
| 文档数 / 总行数 | 22 份 / 7438 行 | C6 |
| 产出时间跨度 | 2026-08-07 → 2026-08-09（3 天） | 文件 mtime |
| 已接受的决策数 | **0**（11 proposed + 1 deferred） | C7 |
| 已执行的 fixture 数 | 0 | 协议 `:655` 自述 |
| 已安装的实现文件数 | 0（`.agents/rules/memory-protocol.md` 不存在） | `ls` |
| 其中「对审查文件的审查」层级文档 | 5 份 | 见下 |

第 5 项指：`review-analysis-...`、`response-review-analysis-...`、
`review-response-review-analysis-...`、`review-protocol-and-plan-...`、
`review-result-review-protocol-and-plan-...`。本文若继续沿同一路径产出，将成为
第 6 份，故本文改为方向审查而非再一次合规复审。

## 4. 复核为成立的部分

本节记录经核对**站得住**的内容，以免本文被读成全盘否定。

1. **§0.3 的权威边界与厂商官方立场独立吻合。** 协议 `:34-43` 主张 Memory 不授予
   权限、不覆盖规则、强制阻断交由机械门禁。Claude Code 官方文档同义（见 §3 P2-2
   引文）。Codex 官方文档（`https://learn.chatgpt.com/docs/customization/memories`，
   本轮实抓）称 memories 应被视为「a helpful recall layer, not as the only source
   for rules that must always apply」，并建议「team guidance be kept in checked-in
   documentation instead」。

2. **§3 的 host-local 边界正确，且与官方措辞几乎一致。** 协议 `:134`：
   「Host-local Memory | Codex/Claude 或主机 | 只能辅助回忆，不是唯一规则来源」。
   官方事实支持该分层：Claude Code 的 auto memory 位于
   `~/.claude/projects/<project>/memory/`，且「Auto memory is machine-local ...
   Files are not shared across machines or cloud environments」；Codex memories 位于
   `~/.codex/memories/`，同为主机本地、默认关闭。

   由此可确认：原生 memory **不能**替代仓库内项目 memory（不进 Git、不进 review、
   不跨机器、不跨 agent）。protocol 主张项目事实归项目仓库（`:104`、`:132`）在方向上
   是对的，且被两家厂商文档反向印证。

3. **§1.1 的官方引文属实。** 本轮实抓其中两条 URL，均可达且内容与所标定位相符。
   另两条本轮未抓，记为未复核。

4. **上一轮三个 P1 的文本修订确实落实。** Protocol §14（`:701-713`）不再定义数字
   Phase；D09 在 `:82`、`:95`、`:363-364` 三处措辞一致；`operation_key` 在
   `:485-514` 有成文推导规则。

5. **README 索引完整。** 22 份 `.md` 对应 21 条唯一链接加 README 自身，全目录零死链；
   无尾随空白；两份历史文件的 superseded 横幅存在。

6. **fixture 覆盖平衡**（见 §3 P2-1 反向核对）。

## 5. 处置建议

本节只提出选项和依据，不执行、不预设操作者选择。

### 5.1 建议方向

**冻结当前文档链为证据，改变交付物形态**，而不是继续 v0.1.2 版本轮次。依据是
§3 的三条 P1：范围排除了唯一有强制力的组件、机器没有执行载体、缺少方法要求的
源事件锚点。这三条都不能通过修订协议文本解决。

形态建议（供操作者裁决，本文不实施）：

1. 把 `projects/reality-ops/AGENTS.md:3-46` 的 memory 契约**向上提取**为
   `.agents/rules/memory.md`，与现有 14 份规则同形（带 `## Ownership`、agent-neutral、
   量级对齐 `authorization.md` 的 7159 B 以内）。依据：`rule-authoring.md:17`
   「portable cross-project method → shared workspace rule」。
2. 把 `check-project-memory.sh` 的门禁模式作为可复用组件对待，而不是 D05 的范围外项。
   依据：协议 `:42` 自述强制力只能来自机械门禁。
3. 原生 agent memory 以一条边界声明处理（主机本地草稿，非项目事实来源），依据为
   §4 第 2 条的官方事实，不需要协议章节。
4. 协议中值得保留的规范内容（所有权边界、report-only/reconcile 之分、密钥排除、
   memory 非权威、陈旧重验）体量约数十行，可并入上述规则文件。

若采纳该方向，需连带处理的既有约束（本文仅列出，未执行）：`.gitignore` 为
`.agents/rules/` 逐文件白名单，需新增一行；`CLAUDE.md` 与
`.agents/host-templates/codex-AGENTS.md:26-38` 两张路由表需各加一行；
`tests/test_sync_codex_config.py:260-275` 与 `:283-297` 两个硬编码元组需同步，
且新规则文件必须含 `## Ownership`、不得含 `Saberu`。

### 5.2 若操作者选择继续当前计划

则 Phase 1 之前必须先解决 §3 P1-2 的顺序矛盾：为标识符与两阶段语义指定执行载体
并为其安排阶段，否则 Phase 4 无法产生出口证据。此外 §3 P1-1 的范围划分需要一个
显式决定：D05 是否维持将 checker 排除在协议之外。

### 5.3 与实施方向无关、应先处理的一项

本目录 22 份文档与 `.gitignore` 修改**至今全部未跟踪、无 Git 基线**，也无
`review-result-...:79` 所建议的 SHA-256 清单。无论选择哪条方向，这批工作目前没有
任何完整性证据。该项独立于方向争议。

## 6. 审查边界与披露

- **审查类型**：方向与可行性审查，不是 v0.1.1 的合规复审。Active plan `:102-124`
  所定义的 Phase 1 定向复审**未被本文执行**，也未被本文替代。
- **比较基线**：workspace-meta `a5ce356`，与 `origin/main` 同步（`git fetch` 退出码 0）。
- **跨仓库边界**：`projects/reality-ops/` 是独立 Git 根，本文仅**只读**引用其
  `docs/project-memory.md`、`AGENTS.md`、`.github/workflows/quality.yml` 与
  `scripts/` 目录列表，作为 supplemental 证据；未修改该仓库任何文件，未运行其
  checker，未读取其 `docs/operations.md` 或部署相关内容。
- **未执行项**：`make bootstrap`、隔离 HOME 双跑、任何 fixture、`check-project-memory.sh`
  实跑、§1.1 中两条官方 URL 的复抓。以上一律记为未执行，不得读作通过。
- **本轮已执行**：`make test`（28 项通过）；两条官方文档 URL 于 2026-08-11 实抓。
- **对既有文档的改动**：本文为新增文件；按 `README.md:77` 的同轮索引维护要求，
  本轮同时在 `README.md` 登记本文一条链接。除该条链接外，未改动任何既有文档正文、
  状态横幅或路由结论。
- **未执行**：Git stage、commit、push、PR；`.agents/`、`.gitignore`、hook、主机配置
  与运行时注入链均未改动。
- **上一会话结论的更正**：撤回「协议体量构成 always-on 常驻上下文成本」的表述
  （见 §3 P2-2）。此外，上一会话报告的 `operation_key` 跨实现不确定性缺口本身成立，
  但若采纳 §5.1 方向，该机器整体移除，则不值得为其单开 v0.1.2 版本轮次；该缺口的
  处置取决于操作者对 §5 的选择。
