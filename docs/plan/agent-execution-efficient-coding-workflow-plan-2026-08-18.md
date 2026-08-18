# Agent Execution / Efficient Coding Workflow Rules 设计与实施计划

> 文档类型：Design Plan / Governance Plan  
> 主题：为 Codex 与 Claude 增加统一的 Agent Execution / Efficient Coding Workflow Rules  
> 日期：2026-08-18  
> 状态：Planning  
> 目标对象：Codex、Claude Code、未来接入的 Coding Agent，以及维护本仓库的开发者  
> 适用范围：所有需要读取仓库、修改代码、运行测试、执行验证、进行 review 或调用本地工具的 Coding Agent 工作流

---

## 1. 背景与事件缘由

### 1.1 当前项目背景

当前仓库的核心目标之一，是通过 GitHub 中统一维护的 rules、skills、hooks 及相关配置，为 Codex 和 Claude Code 提供一致的开发约束、编码风格、质量标准和工作方式。

整体思路是：

1. 将自定义的 rules、skills、配置和相关治理内容集中维护在 GitHub 仓库中；
2. clone 到本地后，通过 bootstrap / sync / hooks 等机制，将这些内容同步到 Codex、Claude Code 等工具的指定位置；
3. 避免不同 Coding Agent 各自使用不同规范，导致代码风格、测试纪律、review 方法和交付质量不一致；
4. 使“统一规则源（single source of truth）”成为长期可维护的 Agent 工程基础设施。

现有体系已经较好地解决了以下问题：

- rules 如何集中维护；
- skills 如何集中维护；
- Codex 与 Claude 如何从同一个仓库获得配置；
- hooks / sync 如何把仓库中的内容同步到实际运行位置；
- 如何通过统一的规则与技能约束 Coding Agent 的输出质量。

但近期一次实际修改任务暴露出一个此前未被系统化覆盖的问题：

> **即使 Codex 已经拥有正确的 rules、skills 和 hooks，它在“如何执行一个代码修改任务”这一层，仍可能产生大量不必要的 Agent/tool round-trip、重复文件读取、失败 patch、重复测试和过重验证。**

这说明“规范内容一致”与“执行过程高效”是两个不同层次的问题。

现有 rules 更多关注：

- 应该写出什么样的代码；
- 哪些质量要求必须满足；
- 哪些测试必须存在；
- review 应检查什么；
- 哪些项目规则不能违反。

而本次事件暴露的是另一层：

- Agent 应如何获取上下文；
- 应如何控制读取范围；
- 应如何选择编辑方式；
- patch 失败后如何降级；
- 应何时跑 focused test；
- 应何时跑 full test；
- 如何避免重复验证；
- 如何避免为了验证一个很小的性质而启动整个集成链路；
- 如何主动减少工具调用和 Agent round-trip；
- 如何在正确性、完整性和执行效率之间建立统一的执行纪律。

因此，有必要增加一个独立的规则领域：

> **Agent Execution / Efficient Coding Workflow Rules**

其职责不是重新定义编码风格，也不是替代已有 skills，而是约束 Coding Agent 在执行任务过程中的行为，使不同 Agent 在保证质量的同时，以更收敛、更高效、更可预测的方式完成任务。

---

## 2. 触发本计划的具体事件

### 2.1 事件概述

2026-08-18，一次针对 macOS Python 兼容性的最小范围修复，由 Codex 使用 Luna xhigh 模型执行。

本次修改的实际内容包括：

- `find_python.sh` 返回绝对 Python 解释器路径；
- Hook 中 Python 路径使用 shell-safe quoting；
- Makefile 的 `test` 和 `agent-sync-check` 支持路径中存在空格；
- 测试改为使用 `sys.executable`，避免再次调用 macOS 系统旧 Python；
- 增加解释器发现、路径转义和 Hook 功能测试；
- 更新 onboarding / 验证文档；
- 增加本轮 plan / changelog。

最终验证结果正常：

- `make test`：31/31 通过；
- Bash 语法检查：通过；
- Python parser compile：通过；
- Hook shell syntax：通过；
- 带空格路径 smoke test：通过；
- 隔离临时 HOME 双次 bootstrap：通过；
- 第二次 bootstrap 文件 hash 不变；
- `.githooks/pre-commit`：通过；
- `git diff --check`：通过。

从结果上看，本次修改质量是合格的。

但整个任务耗时约：

> **27 分钟**

考虑到修改范围较小、测试本身运行极快，这一耗时明显偏高，因此对完整执行历史进行了两轮复盘。

---

## 3. 调查与分析过程

### 3.1 第一轮调查

第一轮调查首先排除了“测试本身很慢”这一假设。

可观察到：

- `make test` 单次约 0.5 秒；
- 隔离 bootstrap 双跑约 4.4 秒；
- 大部分静态检查和普通读取低于 1 秒；
- 一次 Hook smoke test 因临时 HOME 环境触发完整状态检查，约等待 18 秒。

这些数据说明：

> 27 分钟不可能主要由 shell 命令、测试或 bootstrap 的实际执行时间构成。

第一轮调查进一步发现：

- patch 多次出现语法错误、hunk 错误；
- Python、Shell、Markdown 等内容混合在复杂工具调用中，导致反复修改；
- 一次性读取完整 diff 或大文件导致输出截断，随后再次局部读取；
- 完整测试、静态检查和 smoke test 在不同阶段重复执行；
- 为验证 Hook quoting，启动了完整 `workspace_status.py`，导致轻量验证进入了不必要的完整环境状态检查。

第一轮结论方向正确，但缺少 Agent round、patch failure、文件读取和完整测试次数等量化数据。

因此进行了第二轮调查。

---

### 3.2 第二轮调查

第二轮调查要求从完整“初始 review → 修改 → 验证完成”链路重新统计。

主要结果如下。

| 指标 | 本次实际值 |
|---|---:|
| 总 wall-clock | 27 分钟（用户观测） |
| 顶层 Agent/tool loop | 47 次 |
| 顶层 functions.exec | 46 次 |
| wait | 1 次 |
| review 阶段顶层 exec | 11 次 |
| 修改/验证阶段顶层 exec | 35 次 + 1 次 wait |
| review 阶段嵌套工具操作 | 42 次 |
| 修改/验证阶段嵌套工具操作 | 54 次 |
| 嵌套工具操作合计 | 96 次 |
| 显式文件读取 | 约 45 个路径级读取操作 |
| 全仓库/大范围扫描 | 至少 3 次 |
| Patch 尝试 | 28 次 |
| Patch 成功 | 17 次 |
| Patch 失败 | 11 次 |
| Patch 失败率 | 约 39% |
| 完整测试套件 | 7 次 |
| 聚焦测试 | 1 次（2 个测试） |
| agent-sync-check | 2 次 |
| 隔离 bootstrap | 2 次 |
| Hook smoke/syntax | 3 次 |
| 治理/架构规则文件 | 约 9 个唯一文件，存在部分重复读取 |
| plan 状态更新 | 3 次 |

### 3.3 第二轮调查结论

可以直接确认的事实：

1. 本次任务存在 47 个顶层 Agent/tool 回合；
2. 共有 28 次 patch 尝试，其中 11 次失败；
3. patch 失败率约为 39%；
4. 完整测试执行 7 次；
5. 文件读取约 45 次；
6. 至少出现 3 次大范围扫描；
7. 存在大范围输出截断后再次局部读取；
8. 存在“小型 Hook quoting 验证触发完整 workspace 状态检查”的情况；
9. 没有证据表明单次测试、bootstrap 或普通 shell 命令持续数分钟。

从这些事实可以较强地推断：

> 本次 27 分钟的主要性能问题来自 Agent 执行链路的过度迭代，而不是代码、测试或 shell 本身缓慢。

目前无法严谨恢复：

- 每一次模型推理耗时；
- 每一次 Agent round-trip 的 UI / 调度延迟；
- 上下文压缩时间；
- 每个嵌套命令完整 wall-clock；
- 工具调用之间模型停留的准确时间。

因此，本计划不会将 27 分钟机械拆分成某些未经证实的分钟比例，也不会直接承诺“规则加入后必然缩短到某个具体分钟数”。

本计划的目标是：

> **从结构上减少不必要的 Agent rounds，并建立可测量的执行纪律。**

---

## 4. 根因分析

本次事件不是单一原因造成，而是多个执行层问题叠加。

### 4.1 根因一：缺少明确的 Agent 执行纪律

当前 rules 更多关注“最终代码必须符合什么要求”，但没有充分规定：

- 开始任务时应该读多少上下文；
- 哪些读取是足够的；
- 什么时候应该停止继续扩展上下文；
- 什么情况下允许 repo-wide scan；
- 修改应该如何分批；
- patch 连续失败时应如何切换策略；
- 什么情况下必须 full test；
- 什么情况下禁止重复 full test；
- 验证一个局部性质时应该选择何种测试层级。

结果是 Agent 在面对不确定性时，容易采取“多读一点、多测一次、多确认一次”的保守策略。

这种策略提高了心理上的“稳妥感”，但不一定真正提高质量，反而增加：

- 上下文；
- token；
- tool round-trip；
- 失败机会；
- 重复工作；
- 总 wall-clock。

---

### 4.2 根因二：编辑失败缺少明确的 fallback policy

本次：

- 28 次 patch 尝试；
- 11 次失败；
- 失败率约 39%。

主要失败原因不是业务逻辑错误，而是：

- JS 字符串转义；
- shell quoting；
- patch hunk 不匹配；
- 多层语法嵌套导致工具调用构造错误。

问题不只是“某个 patch 失败”，而是：

> **失败后仍继续采用相近的复杂 patch 构造方式。**

如果 Agent 没有明确的失败升级策略，就可能出现：

1. 构造复杂 patch；
2. 失败；
3. 对复杂 patch 做小修；
4. 再失败；
5. 再增加 escaping；
6. 再尝试；
7. 再重新读取文件确认位置。

每次失败不仅增加一次工具调用，还会引发新的模型分析、文件读取和补丁重构。

因此，需要明确：

- 同一种失败策略最多允许尝试多少次；
- 失败后何时减小 patch 范围；
- 何时切换到 deterministic rewrite；
- 何时先精确重新读取目标片段；
- 何时停止在一条复杂命令里嵌套多语言内容。

---

### 4.3 根因三：Context acquisition 过宽

本次存在：

- 约 45 次文件读取；
- 至少 3 次大范围扫描；
- 大输出截断后重新读取；
- 已读取治理文件的部分重复读取。

Agent 常见的风险模式是：

> 为了避免遗漏上下文，先获取尽可能多的信息。

但对于小范围代码修改，这通常不是最优方法。

更合理的方法应是：

> **从最小充分上下文开始，只有当当前证据不足以继续时才扩展。**

例如：

优先：

```bash
git status --short
git diff --stat
git diff --unified=20 -- path/to/relevant/file
rg "target_symbol" relevant/path
sed -n '120,220p' file
```

避免无必要地：

```bash
git diff
cat large_file
rg ... entire_repository
```

如果输出已经截断，后续必须缩小范围，而不是重新执行同等规模甚至更大的读取。

---

### 4.4 根因四：验证过程没有收敛

本次完整测试执行：

> **7 次**

但 `make test` 单次约 0.5 秒。

因此问题不在测试 CPU 时间，而在重复制造 Agent cycle：

1. 模型决定运行完整测试；
2. 产生工具调用；
3. 工具返回；
4. 模型重新分析结果；
5. 后续有小修改；
6. 再次运行完整测试。

对于大多数代码修改，合理的验证过程应分为：

### 实现阶段

- syntax / parse check；
- focused unit test；
- 与当前修改直接相关的最小 smoke test。

### 稳定阶段

- 一次完整测试；
- 必要的 integration test；
- final diff / formatting / static check。

关键规则应是：

> **如果上一次完整测试之后没有发生会影响测试结果的相关代码变化，不应再次执行相同完整测试。**

而不是机械规定“最多只能跑一次”，因为真实任务中确实可能需要在最终改动后重新跑。

---

### 4.5 根因五：测试层级选择不当

本次为了验证一个非常局部的性质：

> Hook 中 Python 路径包含空格时，shell quoting 是否正确。

却实际启动了：

> `workspace_status.py`

这进一步进入：

- Git 状态；
- HOME；
- workspace；
- 可能的远端/环境检查；
- timeout / wait。

这属于典型的：

> **用 integration path 验证 unit-level property。**

更合适的验证方法是：

- `sh -n` 检查 shell syntax；
- stub Python executable；
- fake/status fixture；
- 最小命令验证包含空格路径；
- 将真实 `workspace_status.py` 放在独立 integration test 中。

---

## 5. 本 Plan 的目的

本计划的目的不是单纯“让 Codex 更快”。

如果只追求速度，很容易导致：

- 少读关键上下文；
- 不跑必要测试；
- 不做 final review；
- 跳过 integration verification；
- 以速度换正确性。

真正目标是：

> **建立一套统一、可解释、可验证的 Coding Agent 执行纪律，使 Agent 在保证正确性与质量的前提下，减少无效工作、重复工作和过度验证。**

具体目标包括：

### 5.1 统一 Codex 与 Claude 的执行原则

无论使用：

- Codex；
- Claude Code；
- Luna；
- GPT 系列；
- 其他未来接入 Coding Agent；

都应遵守相同的核心执行纪律。

---

### 5.2 减少无价值的 Agent/tool round-trip

通过规则约束：

- 读取；
- 编辑；
- 验证；
- fallback；
- review；

减少“工具本身很快，但 Agent 反复调用很多次”的问题。

---

### 5.3 提升修改流程的可预测性

让一个 Coding Agent 面对普通代码修改时，默认采用类似：

```text
Scope
→ Minimal Inspect
→ Edit
→ Focused Validate
→ Stabilize
→ Final Validate
→ Diff Review
```

而不是每次临时自由发挥。

---

### 5.4 保持质量优先

规则必须明确：

> Efficient ≠ fewer checks at all costs.

目标不是取消验证，而是：

> **选择最小但足以证明当前性质的验证方式。**

---

### 5.5 提供未来可度量的 Agent 性能基线

通过统一规则和后续 profiling，可以比较：

- 不同模型；
- 不同 Agent；
- 不同任务；
- 规则加入前后；

在：

- rounds；
- failed edits；
- reads；
- full tests；
- wall-clock；

上的差异。

---

## 6. 规则领域的职责边界

### 6.1 为什么这是一个独立领域

“Agent Execution / Efficient Coding Workflow”应被视为独立治理领域。

它不等于：

- coding style；
- test policy；
- review standard；
- security；
- skill；
- hook；
- sync。

它解决的是：

> **Coding Agent 在完成任务期间如何组织行为。**

---

### 6.2 Rules 与 Skills 的边界

该领域虽然独立，但其内容应按职责分层。

#### Rules 负责

> 任何 Coding Agent 在任何代码任务中都应遵守的执行约束。

例如：

- 最小充分上下文；
- 减少重复读取；
- patch fallback；
- progressive validation；
- 避免无必要 full integration；
- 避免重复 full suite；
- 优先 deterministic editing；
- 控制工具输出规模；
- 已知事实不重复确认。

#### Skills 负责

> 某一种任务应该怎样按步骤完成。

例如未来可以存在：

- `code-change`;
- `bugfix`;
- `refactor`;
- `review`;
- `portability-fix`;
- `ci-fix`.

Skill 可以定义：

```text
Scope
→ Inspect
→ Edit
→ Validate
→ Review
```

但这些 Skill 应共同受 Agent Execution Rules 约束。

---

### 6.3 Hooks 的职责

Hooks / sync infrastructure 继续负责：

- 从 GitHub source of truth 同步；
- 将 rules / skills 写入正确位置；
- 检查 drift；
- bootstrap；
- 必要的配置一致性验证。

Hooks 不应承担复杂的 Agent reasoning workflow。

即：

```text
GitHub Source of Truth
        │
        ├── Rules
        ├── Skills
        └── Config
              │
              ▼
        Sync / Hooks
              │
              ▼
      Codex / Claude runtime
              │
              ▼
      Agent follows Rules + Skills
```

---

## 7. 方案设计原则

本计划遵循以下设计原则。

### 7.1 Rule 应描述行为约束，而不是具体工具实现

例如推荐：

> Prefer the smallest sufficient context.

而不是把所有 Agent 强制绑定到：

```bash
sed -n
```

因为 Codex、Claude 或未来 Agent 的工具可能不同。

可以提供命令作为 example，但原则应独立于工具。

---

### 7.2 不使用僵硬的次数限制替代逻辑判断

不推荐：

> Full test 最多只能跑 1 次。

更推荐：

> Do not rerun an unchanged full validation unless relevant code changed, the previous result was incomplete, or a new risk requires revalidation.

因为真实任务存在例外。

---

### 7.3 Efficiency 必须服从 correctness

遇到以下情况应允许扩大范围：

- 问题根因不明确；
- 跨模块行为；
- API contract 改动；
- migration；
- security；
- build / CI 系统；
- unknown blast radius；
- 用户明确要求全仓库 review；
- focused test 无法证明正确性。

规则的目标是：

> 避免无必要扩大范围，而不是禁止扩大范围。

---

### 7.4 Agent 应有“停止继续调查”的条件

Coding Agent 常见问题之一是：

> 每次发现一个新信息，就继续再确认一次。

规则需要明确：

> 当已有信息足以安全执行下一步时，停止继续读取。

---

### 7.5 Agent 应优先缩小不确定性，而不是扩大上下文

如果某个 patch 失败，正确策略应是：

> 精确读取目标片段。

而不是：

> 再读整个文件或整个 diff。

---

## 8. 建议新增的 Rule 文件

建议新增：

```text
rules/agent-execution.md
```

建议正式名称：

> **Agent Execution & Efficient Coding Workflow**

它应成为所有 Coding Agent 的基础执行规则。

---

## 9. `agent-execution.md` 建议结构

### 9.1 Purpose

说明：

- 规则目的；
- 适用范围；
- correctness 与 efficiency 的关系；
- 本规则对 Codex / Claude 均适用。

---

### 9.2 Core Principles

核心原则建议包括：

1. Minimal sufficient context；
2. Minimize unnecessary tool round-trips；
3. Deterministic editing over fragile editing；
4. Fail fast and change strategy；
5. Progressive validation；
6. Test at the lowest sufficient layer；
7. Avoid duplicate verification；
8. Preserve correctness over speed；
9. Expand scope only with evidence；
10. Stop investigating when sufficient evidence exists.

---

## 10. 规则模块一：Context Acquisition

### 10.1 默认最小读取

开始修改任务时优先：

- repository status；
- relevant diff；
- target file / symbol；
- directly related tests；
- required governance rule。

不要默认：

- 全仓库 scan；
- 全量 diff；
- 大文件完整读取；
- 全量架构文档读取。

---

### 10.2 Progressive Context Expansion

建议规则：

> Start narrow. Expand only when current evidence is insufficient.

上下文扩展应有理由，例如：

- symbol definition 不在当前文件；
- test failure 指向其他模块；
- contract 跨文件；
- root cause 尚未定位；
- current diff 无法解释行为。

---

### 10.3 Avoid Duplicate Reads

如果：

- 文件未变化；
- 已经获得足够片段；
- 当前上下文仍存在；

不得仅为“再次确认”而重复读取。

允许重复读取的合理情况：

- 文件已修改；
- patch 失败，需要精确定位；
- 上次输出截断；
- 上次只读了部分内容，现在确实需要另一段；
- 工具上下文已丢失。

---

### 10.4 Large Output Policy

如果输出被截断：

> 下一次读取必须缩小范围。

不得重新执行同等或更大的输出。

例如：

```text
Bad:
git diff
→ truncated
git diff again

Good:
git diff
→ truncated
git diff -- path/to/file
→ still large
git diff --unified=20 -- path/to/file
```

---

## 11. 规则模块二：Tool Round-Trip Efficiency

### 11.1 合并独立只读操作

如果多个读取彼此独立，可以在工具支持的情况下批量执行。

例如：

- status；
- diff stat；
- 两个相关文件的小片段。

但不应为了减少 round 而把：

- 复杂 patch；
- 多语言字符串；
- destructive write；
- 多个高风险操作；

塞入一条极难维护的命令。

原则：

> **Batch safe reads; keep risky writes simple.**

---

### 11.2 每次工具调用必须有明确目的

Agent 在发起工具调用前，应能够回答：

> “这个结果会改变我下一步什么决策？”

如果不能，则该调用大概率是不必要的。

---

### 11.3 避免确认已经确认的事实

例如：

- test 已成功；
- 文件未再修改；
- 同一个 lint 已通过；
- git status 状态已知且无相关写操作；

不应机械重复检查。

---

## 12. 规则模块三：Editing Strategy

### 12.1 Prefer Simple, Deterministic Edits

优先：

- 小 patch；
- 单文件 patch；
- 清晰 hunk；
- deterministic rewrite；
- 结构化编辑工具。

避免：

- 多层 shell quoting；
- 在 JS / Python 字符串中嵌套复杂 patch；
- 一条命令同时修改大量异构文件；
- 为减少一次工具调用而增加大量 escaping 风险。

---

### 12.2 Edit Failure Policy

这是本次事件最重要的新规则之一。

建议：

#### 第一次 patch 失败

必须：

1. 阅读错误；
2. 判断失败属于：
   - hunk mismatch；
   - quoting；
   - syntax；
   - wrong context；
   - stale file；
   - tool limitation；
3. 缩小范围或修正明确原因。

不得无分析地直接重试。

#### 同一策略第二次失败

必须切换策略。

例如：

```text
large patch
→ fail

smaller patch
→ fail

switch to:
- exact localized rewrite
- structured editor
- deterministic script
```

不得持续增加 escaping 复杂度。

---

### 12.3 Failed Edit Must Not Trigger Unbounded Re-reading

失败后只读取：

> 足以重新定位该修改的最小上下文。

---

## 13. 规则模块四：Validation Strategy

### 13.1 Progressive Validation

建议固定成三个层次。

#### Level 1 — Immediate / Cheap

修改后立即：

- syntax；
- parser；
- compile；
- formatter；
- type check（若足够快）；
- focused unit test。

#### Level 2 — Relevant Functional

当修改稳定：

- related test module；
- local smoke；
- component test。

#### Level 3 — Final

在所有实现稳定后：

- full test suite；
- required integration test；
- pre-commit；
- diff check；
- final repository-specific checks。

---

### 13.2 Full Test Re-run Policy

只有以下情况才应再次执行 full suite：

- 上一次 full suite 后发生相关代码修改；
- 上一次结果不完整；
- 上一次运行失败；
- 新发现风险改变验证范围；
- repository policy 明确要求；
- 用户明确要求。

否则：

> 不重复执行相同 full test。

---

### 13.3 Test at the Lowest Sufficient Layer

验证一个属性时，使用能证明它的最低层级。

例如：

验证 shell quoting：

优先：

- `sh -n`；
- stub executable；
- fixture；
- fake path with spaces。

不应默认启动：

- 完整 workspace status；
- Git remote；
- 用户 HOME；
- 全部 bootstrap；
- 外部环境。

---

### 13.4 Integration Test Boundary

Integration test 应用于：

- 多组件协作；
- 实际 runtime contract；
- bootstrap 全流程；
- hooks 实际安装；
- end-to-end behavior。

不应用于单纯验证：

- quoting；
- path joining；
- parser function；
- isolated formatting。

---

## 14. 规则模块五：Governance File Reading

### 14.1 必须尊重治理规则

Efficiency 规则不能用于跳过：

- repository-required rules；
- safety；
- contribution policy；
- validation policy；
- explicit project instructions。

---

### 14.2 但不得重复读取已知治理文件

同一任务中，如果 governance file：

- 已经完整读取；
- 未发生改变；
- 内容仍在有效上下文中；

则不应再次读取。

---

### 14.3 Governance Loading 应按任务相关性

例如 portability fix：

应优先读取：

- coding rules；
- testing；
- portability；
- relevant runtime constraints。

不必仅因为文件存在就读取所有：

- deployment；
- release；
- unrelated security；
- unrelated architecture；

除非当前任务触发。

---

## 15. 规则模块六：Task Phase Discipline

建议 Coding Agent 将普通修改分为明确阶段：

```text
1. Scope
2. Inspect
3. Plan
4. Edit
5. Focused Validation
6. Stabilize
7. Final Validation
8. Diff Review
9. Report
```

### 15.1 Scope

目标：

- 明确要修改什么；
- 明确不修改什么；
- 获取最小必要状态。

---

### 15.2 Inspect

目标：

- 找到实现；
- 找到相关测试；
- 理解当前行为。

停止条件：

> 已经足以安全设计修改。

---

### 15.3 Plan

小任务保持简洁。

计划应重点说明：

- 修改点；
- 风险；
- 测试。

不得为了形式写过长 plan，从而增加治理成本。

---

### 15.4 Edit

使用最简单可靠方式。

每次失败触发 fallback policy。

---

### 15.5 Focused Validation

只验证当前改动。

---

### 15.6 Stabilize

确认：

- 实现是否完成；
- 是否仍需修改；
- focused test 是否稳定。

---

### 15.7 Final Validation

只在代码稳定后执行较重验证。

---

### 15.8 Diff Review

最终检查：

- unintended changes；
- formatting；
- missing files；
- untracked files；
- docs；
- tests；
- diff cleanliness。

---

## 16. 与现有 Skills 的关系

第一阶段不建议立即增加泛化的：

```text
skills/agent-execution/
```

因为容易与 rule 重复。

更合适的是：

```text
rules/
└── agent-execution.md
```

然后已有/未来 skills 引用它。

例如：

```text
skills/
├── review/
├── bugfix/
├── refactor/
├── ci-fix/
└── portability/
```

Skill 中只定义任务特定流程。

比如：

### Bugfix Skill

```text
Reproduce
→ Localize
→ Minimal Fix
→ Regression Test
→ Final Validation
```

### Refactor Skill

```text
Define invariant
→ Baseline tests
→ Structural change
→ Focused tests
→ Full validation
```

这些流程都受 `agent-execution.md` 约束。

---

## 17. 方案能够解决的问题

### 17.1 Patch 失败过多

通过：

- simple patch；
- single-file edit；
- failure fallback；
- 禁止重复同类失败策略；

降低工具层失败率。

---

### 17.2 Agent/tool round 过多

通过：

- minimal read；
- safe batching；
- 不重复确认；
- progressive validation；
- phase discipline；

减少不必要 round-trip。

---

### 17.3 重复文件读取

通过：

- read caching discipline；
- progressive context；
- truncated output narrowing；

减少重复 context acquisition。

---

### 17.4 完整测试重复执行

通过：

- focused test；
- final full test；
- rerun conditions；

减少无意义 full suite。

---

### 17.5 小验证启动完整系统

通过：

- lowest sufficient test layer；
- stub；
- fixture；
- smoke/integration boundary；

减少 timeout 和环境噪音。

---

### 17.6 不同 Agent 执行方式差异过大

Codex 和 Claude 即使推理模型不同，也会共享统一执行纪律。

这样统一的不只是：

- coding style；

还包括：

- working style；
- validation discipline；
- context discipline；
- failure recovery；
- efficiency expectations。

---

## 18. 方案不能保证解决的问题

规则设计必须明确边界。

该方案不能保证：

### 18.1 模型本身推理速度

如果 Luna xhigh 单轮 inference latency 本身较高，规则只能减少 round 数，不能改变单轮模型速度。

---

### 18.2 工具平台调度延迟

Codex runtime / Claude runtime 自身的调度延迟不由仓库规则控制。

---

### 18.3 网络与远程依赖

GitHub、CI、package registry、remote API 等真实等待仍可能存在。

---

### 18.4 本质复杂任务

大型 refactor、cross-module debug、migration、security audit 仍然可能需要大量读取和验证。

目标不是让所有任务都变短，而是：

> **避免任务规模之外的额外浪费。**

---

## 19. 基于本方案的额外思考

### 19.1 应将 Agent Efficiency 作为质量的一部分

传统软件工程通常把：

- correctness；
- maintainability；
- test coverage；

视为质量。

Agent 工程还应增加：

> **execution efficiency**

因为 Agent 的 tool round、token、上下文和 wall-clock 都是实际成本。

因此，一个“结果正确但用了 60 个无必要回合”的 Agent 工作流，不应被认为是完全优质的执行。

---

### 19.2 不应单纯追求最少 tool call

工具调用数只是代理指标。

例如：

一条巨大 shell command：

- 只算 1 个 tool call；
- 但难以 debug；
- escaping 脆弱；
- 一旦失败损失更大。

所以目标不是：

> Minimum tool calls.

而是：

> **Minimum unnecessary tool calls while preserving reliability.**

---

### 19.3 建议增加执行预算意识

未来可以在 rule 中加入软性 budget。

例如普通小修改可提醒 Agent：

- 优先在少量 inspect rounds 内完成定位；
- patch 连续失败需切换策略；
- full suite 不应在无代码变化时重复；
- 发现 rounds 明显增长时重新评估流程。

不建议一开始设死数字。

后续可基于真实数据建立：

- small task baseline；
- medium task baseline；
- large task baseline。

---

### 19.4 应区分“信息不足”与“缺乏信心”

Agent 有时继续读取不是因为信息真的不足，而是因为模型信心不足。

规则应鼓励 Agent 问：

> 当前缺少哪一个具体事实，导致我无法安全执行下一步？

如果无法指出具体缺失事实，就不应继续泛化读取。

---

### 19.5 应给不同 Agent 保留实现自由

Codex 与 Claude 的工具和强项不同。

例如：

- Codex 可能更擅长某类 patch；
- Claude Code 可能更擅长直接文件编辑；
- 未来 Agent 可能有 AST editor。

因此 rule 应定义：

- outcome；
- constraints；
- fallback logic；

而不是硬编码唯一工具。

---

## 20. 验证方案是否达到目标

这是本计划的重要部分。

不能仅凭主观感觉：

> “这次好像更快。”

需要建立可比较指标。

---

### 20.1 Baseline

本次事件可以作为初始 baseline：

| 指标 | Baseline |
|---|---:|
| wall-clock | 27 min |
| top-level rounds | 47 |
| nested tool ops | 96 |
| patch attempts | 28 |
| failed patches | 11 |
| patch failure rate | ~39% |
| file reads | ~45 |
| full test runs | 7 |
| focused test runs | 1 |
| wide scans | >=3 |

---

### 20.2 新规则上线后的核心指标

建议记录：

1. total wall-clock；
2. total Agent rounds；
3. tool calls；
4. read calls；
5. repeated reads；
6. patch attempts；
7. failed patch attempts；
8. full test runs；
9. focused test runs；
10. integration test runs；
11. timeout / wait；
12. final correctness；
13. regression / rework；
14. final diff quality。

---

### 20.3 最重要的评价原则

不能只看 wall-clock。

必须同时满足：

> **效率提升 + 质量不下降**

因此验证应包含两个维度。

#### Efficiency

是否减少：

- rounds；
- failed edits；
- repeated reads；
- unnecessary full tests；
- unnecessary integration paths；
- wall-clock。

#### Quality

是否保持：

- tests pass；
- expected behavior；
- no unintended diff；
- repository policy compliance；
- review quality；
- no missed regression。

---

### 20.4 A/B 对比方式

建议选取未来 5–10 个类似规模任务。

记录：

```text
Task
Model
Task size
Files changed
Lines changed
Rounds
Reads
Patch failures
Focused tests
Full tests
Wall-clock
Final result
```

然后与 baseline 对比。

不建议仅用单次任务判断规则有效性，因为：

- 模型随机性；
- 不同任务难度；
- runtime load；
- 上下文长度；

都会影响结果。

---

### 20.5 初始目标建议

第一阶段暂不规定硬性 wall-clock。

可以采用方向性目标：

- patch failure 显著低于本次 39%；
- full test 重复次数显著减少；
- 没有无理由的相同读取；
- 没有“局部属性验证触发完整集成流程”；
- Agent rounds 明显下降；
- 最终质量不下降。

收集足够数据后，再制定数字目标。

---

## 21. 建议增加轻量 Profiling

本次最大缺失数据是：

> 缺乏每个 Agent round 的时间轴。

未来如果工具允许，建议记录：

```text
timestamp
phase
agent action
tool
duration
result
```

例如：

```text
00:00 Scope
00:13 exec #1
00:14 result
00:27 exec #2
00:28 result
```

这样可以进一步拆分：

- shell execution；
- Agent inference；
- scheduling；
- timeout；
- context processing。

这将帮助回答：

> 是 workflow rounds 太多，还是 Luna xhigh 每轮本身太慢？

---

## 22. 建议的验证入口

未来可以考虑新增统一命令，例如：

```bash
make verify-portability
```

或更通用：

```bash
make verify-agent-change
```

但要避免把所有验证全部塞入一个“超级命令”。

统一入口的价值是：

- 减少 Agent 手工编排；
- 避免漏项；
- 减少重复运行；
- 保证 Codex / Claude 一致。

但内部仍应分层：

```text
verify-fast
verify-focused
verify-full
```

例如：

```bash
make verify-fast
make test-focused
make verify-full
```

让 Agent 根据阶段选择。

---

## 23. 实施步骤

### Phase 1 — 创建规则

新增：

```text
rules/agent-execution.md
```

至少包含：

- Purpose；
- Context Acquisition；
- Tool Efficiency；
- Editing Strategy；
- Edit Failure Policy；
- Validation Strategy；
- Integration Boundary；
- Governance Read Policy；
- Task Phase Discipline；
- Exceptions。

---

### Phase 2 — 接入同步系统

确保新 rule 被：

- GitHub source of truth 管理；
- bootstrap / sync 正确同步；
- Codex 加载；
- Claude Code 加载；
- drift check 覆盖。

---

### Phase 3 — 检查已有 Rules 重复

review：

- testing rules；
- review rules；
- runtime rules；
- capabilities；
- coding rules。

避免同一要求在多个文件中以不同表述重复。

如果 testing rule 已经规定：

> 必须跑哪些测试，

agent-execution 应只规定：

> 什么时候跑、如何避免重复、如何选择层级。

---

### Phase 4 — 检查已有 Skills

检查：

- review；
- refactor；
- bugfix；
- CI；
- portability；

是否存在与新 rule 冲突的步骤。

必要时：

- 引用新 rule；
- 删除重复 execution policy；
- 保留任务特定 procedure。

---

### Phase 5 — 执行实际任务验证

使用真实 Codex / Claude coding task，而不是只做静态规则 review。

至少测试：

1. 小 bugfix；
2. 多文件修改；
3. portability；
4. refactor；
5. failing test debug。

---

### Phase 6 — 收集指标

记录：

- rounds；
- reads；
- failed edits；
- test count；
- wall-clock；
- final quality。

---

### Phase 7 — 调整规则

根据真实行为调整：

- 过严的限制；
- Agent 容易误解的措辞；
- 缺失 fallback；
- 与某些 skill 的冲突；
- Codex / Claude 行为差异。

---

## 24. 后续改进方向

### 24.1 建立 Task Size 分类

未来可定义：

- Small；
- Medium；
- Large；
- Investigation。

不同规模采用不同 execution expectation。

---

### 24.2 建立 Agent Execution Metrics

可以增加自动 summary：

```text
Agent Execution Summary

Rounds: 18
Reads: 7
Edits: 4
Failed edits: 1
Focused tests: 2
Full tests: 1
Integration tests: 1
```

用于长期观察。

---

### 24.3 自动检测重复验证

未来 hooks / wrapper 可以检测：

- 同一测试；
- 文件无变化；
- 短时间重复执行；

并提示 Agent：

> No relevant changes since previous successful full validation.

---

### 24.4 自动缓存治理文件

如果 runtime 允许，可以减少同一任务重复加载相同 governance 文件。

---

### 24.5 建立编辑工具优先级

根据 Codex / Claude 的真实成功率，形成：

```text
preferred edit strategy
fallback 1
fallback 2
```

而不是完全让模型自由尝试。

---

### 24.6 针对不同 Agent 做兼容层

核心 rule 保持一致。

如果发现：

- Codex 对 patch 更敏感；
- Claude 对某类 command 更稳定；

可以增加 Agent-specific implementation note，但不改变核心 execution policy。

---

### 24.7 建立回归样例

将本次事件抽象成 regression scenario：

> 修改一个支持路径带空格的 Python/Hook portability issue。

未来 rules 改动后，用相似任务观察：

- 是否还会出现 >10 failed patches；
- 是否重复 full test；
- 是否触发无必要 integration；
- 是否大范围重读。

---

## 25. 风险与注意事项

### 25.1 过度优化导致漏检

最大风险是 Agent 为减少 rounds：

- 少读关键文件；
- 少跑必要测试；
- 过早结束调查。

因此规则必须始终强调：

> correctness has priority over efficiency.

---

### 25.2 Rules 过长导致自身成为上下文负担

这是非常重要的二阶风险。

如果 `agent-execution.md` 写成数千行，Agent 每次都必须读取，也会增加上下文成本。

因此最终正式 rule 应：

- concise；
- high signal；
- clear MUST / SHOULD / MAY；
- 将背景和长解释保留在本 Plan；
- rule 本体只保留可执行原则。

本 Plan 可以很详细。

正式 Rule 应明显短于本 Plan。

---

### 25.3 Rules 与 Skills 重复

如果同一流程同时写在：

- rule；
- bugfix skill；
- refactor skill；
- review skill；

会导致维护困难。

应坚持：

> Rule = cross-task constraint  
> Skill = task-specific procedure

---

### 25.4 过度依赖固定数字

现阶段不应规定：

- 最多 10 rounds；
- 最多 2 reads；
- 必须 5 分钟完成。

因为任务复杂度差异太大。

优先使用行为型规则和 rerun condition。

---

## 26. 预期最终架构

建议长期形成：

```text
GitHub Agent Governance Repository
│
├── rules/
│   ├── coding-style.md
│   ├── testing.md
│   ├── review.md
│   ├── security.md
│   └── agent-execution.md
│
├── skills/
│   ├── bugfix/
│   ├── refactor/
│   ├── review/
│   ├── ci-fix/
│   └── ...
│
├── hooks/
│   └── sync/bootstrap/drift checks
│
├── docs/
│   ├── architecture/
│   ├── reviews/
│   └── plans/
│
└── metrics/
    └── future agent execution profiling
```

其中：

- **Rules** 统一“必须遵守什么”；
- **Skills** 统一“某类任务如何做”；
- **Hooks** 统一“如何同步到 Agent runtime”；
- **Agent Execution Rule** 统一“Agent 如何高效而可靠地执行”；
- **Metrics** 负责验证规则是否真正有效。

---

## 27. 本计划的最终判断

本次 27 分钟事件说明：

> 当前系统已经能够统一 Codex / Claude 的配置和质量要求，但还缺少一层针对 Agent 自身执行行为的统一治理。

新增 **Agent Execution / Efficient Coding Workflow Rules** 的价值，不只是解决一次任务过慢的问题。

它将补齐整个 Agent Governance 架构中此前缺失的一层：

```text
What to produce
→ coding/testing/review rules

How to perform task-specific work
→ skills

How to distribute governance
→ hooks/sync

How to execute efficiently and reliably
→ Agent Execution Rules
```

这一层加入后，系统的目标将从：

> “让 Codex 和 Claude 使用同一套规范”

进一步升级为：

> **“让 Codex 和 Claude 在同一套规范下，以一致、可靠、可验证、可持续优化的执行方式完成 Coding 工作。”**

---

## 28. 下一步建议

建议按以下顺序执行：

1. 以本 Plan 为设计依据；
2. 新增 `rules/agent-execution.md`；
3. 将正式 Rule 控制为高信号、短文本；
4. review 现有 testing / review / runtime rules，避免重复；
5. review 已有 skills，只保留 task-specific workflow；
6. 接入现有 sync / bootstrap；
7. 使用 Codex 和 Claude 各执行若干真实任务；
8. 记录 Agent rounds、reads、failed edits、test runs 和 wall-clock；
9. 对比本次 27 分钟 baseline；
10. 根据数据进行第二轮规则迭代。

---

## 29. 成功标准

当以下条件持续成立时，可以认为本方案达到了第一阶段目标：

- Codex 与 Claude 都能加载同一 Agent Execution Rule；
- 普通代码修改默认从最小上下文开始；
- 不再频繁出现无目的 repo-wide reading；
- patch 失败后能主动切换策略；
- failed edit rate 明显下降；
- focused test 成为实现阶段默认验证方式；
- full test 不再无变化重复执行；
- unit-level property 不再默认触发 full integration path；
- Agent/tool rounds 相较同规模 baseline 明显下降；
- wall-clock 有改善；
- 最终测试、行为和 diff 质量没有下降；
- 开发者能够从 execution summary 中解释 Agent 为什么进行了主要工具操作。

最终目标不是追求一个绝对最短的任务时间。

最终目标是：

> **让 Coding Agent 的每一次读取、编辑和验证都具有明确价值，让执行过程与最终代码质量一样受到治理。**
