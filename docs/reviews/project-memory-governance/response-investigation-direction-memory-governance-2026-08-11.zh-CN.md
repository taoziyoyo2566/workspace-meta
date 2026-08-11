# 对方向审查独立调查的响应

Status: 反馈产物；由 AI 会话产出。本文接受独立调查对 P1-1 的证据推翻，披露一处
调查未发现的同类错误，逐条回应其七项复核意见，补充两处对调查本身的修正，并登记
对原方向审查的更正清单。本文不构成操作者批准，不授权 Protocol 安装、`.agents/`
或 `.gitignore` 变更、Reality Ops 迁移或 Git 发布。

Date: 2026-08-11

回应对象：

- [investigation-direction-memory-governance-2026-08-11.zh-CN.md](investigation-direction-memory-governance-2026-08-11.zh-CN.md)

被审查的本方文档：

- [review-direction-memory-governance-2026-08-11.zh-CN.md](review-direction-memory-governance-2026-08-11.zh-CN.md)

对照材料：

- `~/workspace/projects/reality-ops/`（独立 Git 根，supplemental；见 §8 边界）
- `~/workspace/.agents/rules/review.md`（跨 Git 根证据纪律）
- `~/workspace/feedback-register.md`（W-R24、W-R27）

## 1. 总体回应

**接受调查的核心判定。** 原方向审查的 P1-1 事实表述不成立，其上建立的「冻结并改
形态」建议因此过强。调查提出的分层处置（先定义 freshness MVP，把 Claim 身份、
`operation_key`、两阶段恢复保留为候选 reference）比原审查的处置更准确，本方采纳。

原审查中仍然成立的部分是 §3 P2-1（规范重心与已知失效不成比例）、P2-2（体量与厂商
形态指引冲突）、P2-4（过程未收敛）和降级后的 P1-2（计划阶段顺序缺口）。调查对这四项
的判定与本方一致，分歧只在严重度和处置强度。

本文另披露一处调查未发现、且与被推翻的 P1-1 同源的错误（§2.2），它使原审查该条
证据链的失效范围比调查所述更大。

## 2. 接受的修正

### 2.1 P1-1 的事实基础被推翻——完全接受

本方独立复算，结果与调查一致：

| 检查 | 命令 | 结果 |
|---|---|---|
| `AGENTS.md` 是否被 HEAD 跟踪 | `git -C projects/reality-ops ls-files --error-unmatch AGENTS.md` | **UNTRACKED** |
| checker 是否被 HEAD 跟踪 | 同上，`scripts/check-project-memory.sh` | **UNTRACKED** |
| HEAD 的 workflow 是否含 memory gate | `git show HEAD:.github/workflows/quality.yml \| grep -c check-project-memory` | **0** |
| 工作树 workflow 状态 | `git status --porcelain .github/workflows/quality.yml` | ` M`（未提交修改） |
| dirty/untracked 路径总数 | `git status --porcelain \| wc -l` | **17**（与调查计数一致） |

原审查 §3 P1-1 证据表中的「**门禁由 CI 按变更 range 强制执行**」为错误陈述。该 gate
不存在于任何已发布状态，CI 从未执行过它。原审查引用的
`.github/workflows/quality.yml:58,60,62` 是工作树行号，不是提交内容。

因此原审查「唯一已落地的机械门禁被划在协议范围外」不成立，其据此推出的「D05 划分
错误」亦不成立。调查 §3.1 的判定正确。

### 2.2 调查未发现的同源错误——本方主动披露

原审查用于证明「该实现可工作」的第二项证据同样测错了对象：
`docs/project-memory.md` **本身也处于未提交修改状态**。

| | HEAD（已发布） | 工作树（原审查所读） |
|---|---|---|
| 行数 | 170 | 279 |
| `Last updated` | 2026-06-23 JST | 2026-08-07 JST |
| 声称的 Active branch | `fix/monitor-integrity` | `feat/roadmap-2026-08` |
| 是否含「HEAD at the time」断言 | 无 | `:8` 有 |

补充事实：

- 该文件末次提交为 `3a59809`（2026-06-23 10:55:39 +0900）；
- 仓库 HEAD 为 `7e93c01`（2026-08-02 08:32:21 +0900）；
- 两者之间相隔 **13 个提交**。

原审查 §3 P1-1 表中「其声称的 HEAD 与实际一致，未漂移」以及 §2 的 C1/C2 结论，均是
在未提交副本上得出的。已发布版本声称的分支是 `fix/monitor-integrity`，与当前分支
不符。

### 2.3 根因与规则归属

原审查违反 `.agents/rules/review.md:44-51`：跨 Git 根状态必须标为 supplemental 并
报告确切来源。原审查标注了 supplemental，但**未区分 tracked 与工作树状态**，直接用
`Read`/`grep` 读取嵌套仓库文件并将其陈述为已发布契约。正确做法是对任何跨仓库承重
引用先执行 `git ls-files` 与 `git show HEAD:<path>`。

附带承认一项披露缺陷：原审查「审查对象」写作「本目录全部 22 份 Markdown 文档」，
实际完整阅读约 6 份，其余为关键词检索；`conversation-requirements-2026-08-07.zh-CN.md`
未被阅读。该表述为虚报，见 §3.3。

## 3. 逐条回应

### 3.1 对 §3.1（P1-1）：接受，无保留

见 §2.1。原审查该条撤回。调查保留的提醒——候选 checker 适合作为项目适配器样例，但
须先在其自身仓库完成计划、验证和发布——本方同意。

### 3.2 对 §3.2（P1-2）：接受降级，保留缺口本体

接受「Protocol 是规范草案，不是可执行程序」的定性，以及「规则文件不能计算
SHA-256/ULID 只证明需要实现层」的推论。原审查「当前形态下 Phase 4 的前置条件不成立」
的措辞过强，撤回该表述。

保留的部分是调查自己也确认的计划缺口：协议 `:697` 把「接入 SessionStart、hook、
脚本或数据库」推迟到协议与 fixture 评审之后，而 Active plan `:159-162` 的 Phase 4
需要该载体产生出口证据。调查 §3.2 提出的最小修订方向（Phase 2 提供隔离 reference
harness，Phase 4 再实现项目边界内 adapter）优于原审查框架，本方采纳。

### 3.3 对 §3.3（P1-3）：接受降级为 P2

原审查的扫描结果（本目录 `W-R`、`源事件`、`feedback-register` 引用数均为 0）作为
计数事实成立且可复算，但原审查将其读作「program 没有源事件锚点」，属于过度解读：
引用缺失不等于来源不存在。

加重接受的理由：原审查从未阅读 `conversation-requirements-2026-08-07.zh-CN.md`——
即调查指出的来源记录所在——却对来源问题下了 P1 判断。该判断在证据上没有资格成立。

同意调查的结论：真实缺口是 Protocol `§1.1 设计依据` 未把 W-R24 与对话需求纳入来源
链，应补 provenance mapping，而非据此废弃 program。

### 3.4 对 §3.4（P2-1）：一致，并补强证据

双方判定一致。本方补充一项使该条更强的证据，见 §5：W-R24 的失效模式不只是历史
register 条目，它**当前正体现在该仓库唯一的已发布 memory 文件中**。

### 3.5 对 §3.5（P2-2）：接受，并接收其新增事实

接受「体量风险成立、常驻上下文成本不成立」的双向判定；原审查已在其 §3 P2-2 主动
撤回 always-on 表述。

接收调查提供的新事实：Codex 官方文档说明 `AGENTS.md` 指令链默认有 32 KiB 上限。
本方据此复算：协议 33978 B 已超过 32768 B。该数字原审查没有，调查补上后，体量问题
从「与形态指引冲突」升级为「已越过一条具体的机械上限」——尽管协议当前并未安装到
`AGENTS.md`，该数字仍应进入安装可行性评估。

同意其处置：不立即压缩，而是拆成短 operational rule + protocol reference +
fixture/schema 三层，只有短规则进入默认路由。该方案优于原审查 §5.1 提出的
「收敛为单一规则文件」，撤回原方案。

### 3.6 对 §3.6（P2-3）：接受折中

接受「Reality Ops 不能作为已验证基线提前，也不应完全留到 Phase 6」的折中，以及
Phase 1/2 只做只读 compatibility mapping、使用隔离 fixture 或冻结文本快照的做法。

需要附加一项约束：按 §2.2，用于 mapping 的「冻结文本快照」必须显式声明取自 HEAD
还是工作树。原审查的错误正是在此处产生。

### 3.7 对 §3.7（P2-4）：一致

双方判定一致：过程风险成立，非技术阻塞。同意停止产生「审查审查结果」的文档层级。
本文为对调查的响应，属既有 response 文档类型，不新增审查层级；本方不再产出新的
方向 review。

## 4. 对调查本身的两处补充

以下两点不影响调查的结论，但影响其证据表述的精确度。

### 4.1 `docs/project-memory.md` 是 tracked，调查清单未列出

调查 §3.1 的复核清单列出 `AGENTS.md`、checker 与 workflow gate 三项未跟踪，准确；
但未指出 memory 文件本身**已被 HEAD 跟踪**（见 §2.2）。

该区分是实质性的：它决定了当前处境是「制品尚不存在」还是「制品已发布并正在腐化」。
按 §5 的证据，实际是后者，而后者恰好是调查所主张的 freshness MVP 的直接适用场景。
建议在后续证据基线中按三态区分：已发布且新鲜 / 已发布但过期 / 未发布候选。

### 4.2 目录计数在落盘瞬间即失效，属结构性缺陷

调查 §3.7 正确指出原审查的「22 份」是写入自身前的快照。同一机制作用于调查自身：
其「当前目录已有 23 份 Markdown」在该文件写入后即为 24；本文写入后为 25。

这与本目录既有的 R-02 属同一失效。按 W-R27 的分类，这是 shape/omission 型失效，
应采用结构手段处理（改为读取时计算，或在正文中不写绝对计数、只写核对命令），而不是
要求作者更谨慎。建议将其登记为文档治理规则修订项，而非逐轮追责。

## 5. 新增证据：W-R24 的失效模式当前处于活跃状态

本方在复核调查指控的过程中获得一项两份文档均未包含的事实。

已发布的 `projects/reality-ops/docs/project-memory.md@HEAD`：

- `Last updated: 2026-06-23`，末次提交 `3a59809`（2026-06-23）；
- 声称 `Active branch: fix/monitor-integrity`，与仓库当前分支 `feat/roadmap-2026-08` 不符；
- 落后仓库 HEAD `7e93c01`（2026-08-02）**13 个提交**。

即：**该工作区唯一一份已发布的项目 memory，此刻正处于过期状态，且其过期形态正是
W-R24 记录的失效类型**（陈旧事实未随环境变化重验，后续读者可能据错误前提行事）。

与之对应，该仓库工作树中未提交的三项改动——279 行新 memory、`AGENTS.md` 维护契约、
workflow 中的 freshness gate——共同构成一次**未发布的 freshness 补救**。本方阅读了
`scripts/check-project-memory.sh`（未运行）：其机制为「触发路径清单命中时，要求
`docs/project-memory.md` 在同一提交内一并变更」，与调查 §3.1 的描述一致，且不实现
Claim 身份、history、幂等或并发语义。

该事实的意义：

1. 它为 program 提供了 W-R27 所要求、而 program 一直缺失的 RED 证据，且是当前可观察
   实例，不只是历史 register 条目；
2. 它从独立方向支持调查 §7 的 verdict——第一版范围应由 stale-memory 失效定义；
3. 它同时说明该 checker 的设计目标本身就是 freshness gate，因此适合作为 MVP 的
   适配器参考，但仍须按调查 §3.1 的要求先在其自身仓库发布。

本条为只读观察，未修改、未运行、未 stage Reality Ops 任何内容。

## 6. 对原方向审查的更正清单

按 `README.md:80`（历史文档不得静默改写），原审查文件正文**未被修改**；更正以本文
为载体登记，日期 2026-08-11。

| 原审查条目 | 处置 |
|---|---|
| §3 P1-1 全条 | **撤回**。CI 强制执行为错误陈述；D05 划分未被证伪 |
| §3 P1-1 表中「其声称的 HEAD 与实际一致，未漂移」 | **撤回**。测于未提交副本；已发布版本过期（§2.2） |
| §2 证据表 C1/C2 | **限定**。仅对工作树成立，不代表已发布状态 |
| §3 P1-2 「当前形态下 Phase 4 的前置条件不成立」 | **撤回措辞**，保留计划顺序缺口本体，降级为计划级问题 |
| §3 P1-3 严重度 | **降级为 P2**。引用缺失不等于来源不存在 |
| 「审查对象：本目录全部 22 份 Markdown 文档」 | **更正**。实际完整阅读约 6 份，其余为关键词检索 |
| §5.1 「收敛为单一规则文件」 | **撤回**，改采调查 §3.5 的三层拆分 |
| §3 P2-1、P2-2、P2-4、§5.3 | **维持**。P2-2 因 32 KiB 上限而增强（§3.5） |

## 7. 对后续顺序的确认与一项补充

确认调查 §5 的七步顺序，并提出一项应提升优先级的补充。

调查 §5 第 2 步要求把 Reality Ops checker 标注为 dirty/untracked supplemental
candidate。本方建议将**持久化风险单列为与方向决策并行的一项**，理由是它跨越两个
仓库且不受方向争议影响：

- workspace-meta：本目录全部 Markdown 与 `.gitignore` 修改均未跟踪，无 Git 基线，
  亦无 `review-result-...:79` 所建议的 SHA-256 清单。核对命令（按 §4.2 不写绝对
  计数）：`git status --porcelain --untracked-files=all docs/reviews/project-memory-governance`；
- Reality Ops：17 条 dirty/untracked 路径，其中包含 memory 文件本身与整套未发布的
  freshness 补救。

两处的 memory 相关工作目前都没有完整性证据。该项独立于「freshness MVP 还是完整协议」
的范围决策，任一方向下都应先处理。

## 8. 已执行的核验与缺口

已执行：

- Reality Ops tracked/untracked 对账（`git ls-files`）、`git show HEAD:` 内容比对、
  工作树与 HEAD 的行数/字段差异、memory 文件末次提交与 HEAD 的提交距离；
- `scripts/check-project-memory.sh` **只读阅读**（触发路径清单与同提交要求）；
- 协议字节数与 32 KiB 的复算；
- 本目录 Markdown 计数与 README 索引核对。

未执行、不得读作通过：

- `check-project-memory.sh` 实跑（其所在仓库处于 dirty/untracked 状态，且本文不授权
  运行或修改）；
- `make bootstrap`、隔离 HOME 双跑、任何 Memory fixture；
- Reality Ops 远端 freshness fetch；
- 本轮未重复运行 `make test`（上一轮 28 项通过，本轮未改动代码）；
- `conversation-requirements-2026-08-07.zh-CN.md` 本轮仍未通读，故本文不对调查
  §3.3 关于该文件内容的具体描述作独立背书，仅接受其「来源记录存在」的结论。

边界：

- Reality Ops 为独立 Git 根，本文仅只读引用，未修改、未 stage、未运行其脚本；
- 未修改原方向审查、调查文件、Protocol、Active plan 或任何历史文档正文；
- 按 `README.md:79` 的同轮索引维护要求，本轮同时在 `README.md` 登记本文一条链接；
- 未执行 Git stage、commit、push、PR；`.agents/`、`.gitignore`、hook、主机配置与
  运行时注入链均未改动。
