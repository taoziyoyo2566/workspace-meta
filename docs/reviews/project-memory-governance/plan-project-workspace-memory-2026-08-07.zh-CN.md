# 项目与工作区 Memory 治理实施计划

状态：供操作者审阅的草案；尚未开始实施。

日期：2026-08-07

处置状态：Superseded / reference-only；已被 plan-memory-governance-v0.1-2026-08-09.zh-CN.md 替代。
不得将本文阶段作为当前实施计划执行。

相关设计：[solution-project-workspace-memory.zh-CN.md](solution-project-workspace-memory.zh-CN.md)

## 1. 目标

引入一个由 AI 主导的 memory 协议，包含两个范围：

- 当前项目仓库的项目 memory；
- 由 workspace-meta 维护的项目地图型工作区 memory。

提供模板、路由、审计行为、来源历史、迁移指导和验证方式，同时不让固定脚本负责理解所有项目的代码或工具链。

## 2. 范围

### 包含

- workspace-meta 中关于项目 memory 的自然语言规则；
- workspace-meta 中关于工作区 memory 的自然语言规则；
- 项目和工作区模板；
- Codex 与 Claude 的全局适配器路由；
- Reality Ops 从当前项目 memory 原型迁移；
- 手动快速/完整项目审计；
- 明确的工作区 memory 刷新；
- 仅限路径、链接、语法和明显安全问题的机械检查；
- 验证 fixture 和文档。

### 不包含

- 部署或 live 基础设施变更；
- 自动 Git stage、commit、push、merge 或创建 PR；
- SessionStart 自动写入；
- 第一版作为事实源的中心数据库；
- 普通项目任务中的自动跨项目 memory 修改；
- 保存 secrets、原始聊天记录或未经脱敏的命令输出；
- 与 memory 治理无关的 Reality Ops 应用行为变更。

## 3. 仓库事实与前置条件

### 当前 workspace-meta 事实

- 工作区根目录是 workspace-meta Git 仓库。
- 独立项目位于 ~/workspace/projects/<project>，并保留独立 Git 根目录。
- make bootstrap 会同步标记的 Codex/Claude 配置面。
- make agent-sync-check 在不写入的情况下报告托管配置漂移。
- 当前 SessionStart 评估器检查 workspace-meta 的 Git/环境状态，不是项目 memory 写入器。
- 工作区使用反向白名单 .gitignore；新增 review 目录需要显式 allow 规则。

### 当前 Reality Ops 事实

- AGENTS.md 将任务路由到 docs/project-memory.md。
- docs/project-memory.md 记录 Ansible venv、setup、syntax-check 和运维交接事实。
- scripts/check-project-memory.sh 是项目专用 freshness gate，根据项目路径判断是否需要 memory。
- CI 会对变更 Git 范围运行该 checker。
- Reality Ops 工作树已经有无关且未发布的改动；实施必须保留这些改动，避免广泛清理。

### 前置条件

- 操作者批准相关设计文档。
- 确认默认路径和历史格式。
- 文档阶段不需要修改主机凭据、hook 信任状态或项目运行时状态。

## 4. 阶段计划

### Phase 0 — 批准契约

#### 操作

1. 审阅 solution-project-workspace-memory.md。
2. 确认项目/工作区所有权和默认路径。
3. 确认“第一次可写项目任务”是初始化边界。
4. 确认工作区刷新默认不修改项目 memory。
5. 确认第一版使用 Markdown 历史。

#### 预期效果

实施拥有稳定范围，不会漂移为中心项目数据库或隐式跨仓库写入器。

#### 退出证据

- 操作者决策记录在计划或后续 superseding review note 中；
- 任何改变的方向在 Phase 1 开始前明确标记。

### Phase 1 — 增加 workspace-meta 协议和模板

#### 预期文件

~~~text
.agents/rules/project-memory.md
.agents/rules/workspace-memory.md
.agents/templates/project-memory.md
.agents/templates/workspace-memory.md
docs/architecture/memory-governance.md
.agents/host-templates/codex-AGENTS.md
CLAUDE.md
~~~

如果现有 workspace 模板约定更适合使用 host-template 命名，可以调整模板位置，但不能改变所有权。

#### 操作

1. 将项目 memory 协议写成自然语言指令。
2. 单独写出工作区 memory 协议。
3. 在 Codex 和 Claude 全局适配器中增加简洁触发路由。
4. 保持适配器紧凑；详细行为放在共享规则所有者中。
5. 增加带有明确 unverified 和 gap 字段的稳定最小模板。
6. 说明脚本不能替代 AI 的语义判断。
7. 说明 SessionStart 仍然是状态/上下文机制。

#### 预期效果

执行 make bootstrap 后打开新项目，即使项目还没有专用 AGENTS.md，也能获得同一套协议。项目仍然拥有自己的事实。

#### 验证

~~~bash
make agent-sync-check
make test
git diff --check
~~~

还要检查渲染后的适配器，确认它路由到新规则，并没有重复授权、Git 或运行时所有权。

### Phase 2 — 迁移 Reality Ops 原型

#### 预期文件

~~~text
projects/reality-ops/AGENTS.md
projects/reality-ops/docs/project-memory.md
projects/reality-ops/docs/project-memory/history/
~~~

#### 操作

1. 将 Reality Ops 专用的 Ansible 和运维约束保留在其 AGENTS.md 中。
2. 删除重复的通用 memory 生命周期文字，改为路由到 workspace 所有者，并保留项目专用补充。
3. 保留当前 Ansible 事实和验证缺口。
4. 添加第一条迁移/历史记录，说明原有 memory 状态和新的所有权模型。
5. 记录当前 checker 是 Reality Ops 的次级防护，而不是工作区级语义实现。
6. 除非有单独批准的决定，否则不要在同一变更中删除 checker 或 CI gate。

#### 预期效果

Reality Ops 继续拥有可用的项目 memory 和 CI 保护，同时通用生命周期迁移到 workspace-meta。现有未提交改动保持不变。

#### 验证

~~~bash
cd ~/workspace/projects/reality-ops
bash -n scripts/check-project-memory.sh
scripts/check-project-memory.sh --working-tree
git diff --check
./setup --check
./ansible-playbook deploy --syntax-check
~~~

Ansible 检查只用于验证已纳入范围的 Reality Ops 工具链事实，不是仅修改 workspace-meta 文档的必需条件。

### Phase 3 — 增加 AI 审计工作流

定义并测试三种自然语言操作：

~~~text
快速审计当前项目 memory，范围是 <section/claim/topic>。
~~~

~~~text
完整审计当前项目 memory，先列出审计范围和排除项，再执行并更新历史。
~~~

~~~text
只审计并报告，不修改项目文件。
~~~

共享规则必须要求 AI：

1. 读取当前 memory 和历史；
2. 根据项目选择证据搜索计划；
3. 选择适合项目的工具和命令；
4. 将声明分类为已验证、推断、未验证、过期或矛盾；
5. 只在声明范围内更新当前 memory；
6. 追加包含原因、证据、结果和缺口的审计记录；
7. 提供最终 memory disposition。

#### 预期效果

协议能够适应新的项目类型和变化中的 AI 能力，不需要 workspace-meta 为每种新的构建系统或目录布局更新脚本。

#### 验证 fixture

使用临时本地 fixture 仓库，至少包括：

1. 没有 memory；
2. 包含未验证声明的 memory；
3. 被当前代码推翻的 memory 声明；
4. 包含无关脏工作树改动；
5. 只读审计请求；
6. 使用非默认 memory 路径的项目。

对每个 fixture 验证 AI 保留无关工作、说明证据和缺口，且不会静默扩大范围。

### Phase 4 — 增加工作区 memory

#### 预期文件

~~~text
docs/workspace-memory.md
docs/workspace-memory/history/
~~~

#### 操作

1. 增加工作区 memory 模板和第一份工作区清单。
2. 增加描述项目枚举和摘要字段的 workspace-memory 规则。
3. 定义明确的“刷新 workspace memory”操作。
4. 规定默认输出只更新工作区项目地图，不修改项目。
5. 记录项目 memory 链接、最近审查日期、观察到的项目版本、阶段、TODO 和阻塞项。
6. 将缺失或过期的项目 memory 记录为工作区 TODO。
7. 每次刷新追加一条工作区历史记录。

#### 预期效果

工作区拥有持久、可审查的项目地图，同时不集中项目实现事实，也不产生隐藏的跨仓库写入。

#### 验证

使用至少两个独立项目仓库测试：

- 增加项目；
- 移除或归档项目；
- 修改项目高层阶段；
- 保留一个没有 memory 的项目；
- 刷新 workspace memory 两次。

第二次刷新不得复制当前项目条目，也不得改写无关项目仓库。

### Phase 5 — 增加窄化的机械防护

#### 操作

只为非语义不变量增加检查，例如：

- workspace memory 链接指向存在的项目路径；
- 项目 memory 链接可以解析；
- 历史记录包含必需的 ID 和日期；
- Markdown/模板仍然可读；
- 明显的 secret 模式没有被复制到历史中。

不要在 workspace-meta 中增加通用的硬编码项目触发列表。

Reality Ops 可以保留当前项目专用 checker，同时单独评估其价值。如果以后要删除，需要单独的迁移决定和 CI 验证。

#### 预期效果

在不让静态脚本成为 memory 语义质量所有者的前提下，检测基本损坏和明显遗漏。

### Phase 6 — 评估历史索引

#### 初始实现

使用 Git 中的 Markdown 历史。暂不增加 SQLite 或其他数据库。

#### 仅在以下情况重新考虑

- 项目数量很多，导致历史查找变慢；
- 跨项目查询成为日常操作；
- 用户需要按生命周期、阶段、声明状态或日期筛选；
- 可以维护一个不会成为权威来源的可重建索引。

如果增加索引，事实源规则仍然是：

~~~text
Git 可读的当前视图和历史 = 权威来源
SQLite/本地索引 = 可重建的查询加速层
~~~

### Phase 7 — 最终迁移审查

#### 操作

1. 将最终文件与已批准的设计比较。
2. 检查项目和工作区范围仍然分离。
3. 确认没有引入 SessionStart writer。
4. 确认没有引入通用语义 checker。
5. 确认 secrets、主机状态、信任状态和原始聊天记录被排除。
6. 在实施 changelog 中记录偏差和证据。
7. 将所有 Git 发布决定与实施完成保持分离。

#### 预期效果

仓库中形成的是可审查的治理变更，而不是隐含的部署或发布事务。

## 5. 验收标准

只有满足以下全部条件，实施才可接受：

1. 没有 memory 时，新的可写项目任务会创建最小项目 memory。
2. 初始化不包含虚构的已验证事实。
3. 只读任务不修改项目，并报告 memory 缺失。
4. 项目快速审计只修改声明范围，并写入历史。
5. 项目完整审计记录范围、证据、排除项和缺口。
6. 普通项目任务默认不更新工作区 memory。
7. 工作区刷新默认只更新工作区项目地图。
8. 工作区范围的深度审计要求明确范围，并逐个项目执行。
9. 每次持久变更记录原因、时间、证据、结果和未解决的不确定性。
10. 重复刷新不会复制当前条目或历史事实。
11. 现有无关工作树改动保持不变。
12. 任何 memory 或历史产物都不包含 secrets 或原始敏感输出。
13. 实施过程中不发生 Git 发布或 live mutation。

## 6. 风险与缓解

| 风险 | 缓解措施 |
|---|---|
| AI 忘记 memory reconciliation | 强制收尾 disposition 和审计 fixture |
| AI 编造事实 | 证据字段和明确的未验证/过期状态 |
| 工作区范围泄漏到项目任务 | 明确范围表和分离的规则 |
| 静态脚本过期 | 保持脚本机械化，并在需要时保留项目专用脚本 |
| 历史无限增长 | 保存证据摘要而非聊天记录，后续评估保留策略 |
| 多个 agent 修改同一 memory | 更新前重新读取、保留无关改动、历史采用追加方式 |
| live 事实过期 | 记录范围和验证时间，承载关键事实前要求重新检查 |
| 工作区索引过期 | 记录最近刷新时间，明确标记缺失/过期的项目 memory |
| 敏感证据被持久化 | 脱敏摘要，禁止原始 secrets/输出 |

## 7. 回滚与恢复

- 文档阶段可以通过移除新增 review 文档及对应 .gitignore allow 条目回滚。
- 规则/适配器变更可以通过托管标记块和批准的 workspace-meta 修订恢复；托管标记之外的主机内容保持不变。
- 项目 memory 迁移必须在 Git 历史中保留原有内容，且不能改写无关项目文件。
- 如果 AI 审计产生错误声明，应通过正常审查的 Git 变更恢复当前视图，并追加一条纠正历史；除非需要删除 secret，否则不要抹除来源记录。

## 8. 验证矩阵

| 范围 | 检查 | 预期结果 |
|---|---|---|
| 工作区文档 | git diff --check | 没有空白错误 |
| 工作区白名单 | pre-commit/git check-ignore 审查 | 新 review 文档可被跟踪 |
| 适配器路由 | make agent-sync-check | 托管输出保持一致 |
| 工作区测试 | make test | 现有测试通过 |
| 项目迁移 | 项目 memory checker | 当前项目 gate 的范围和含义仍清楚 |
| AI 协议 | fixture 任务 | 初始化、审计、缺口和范围行为正确 |
| 工作区刷新 | 双项目 fixture | 只修改工作区摘要 |
| 安全 | 携带 secret 的 fixture | 敏感内容不会进入历史 |
| 发布边界 | git status 和 diff 审查 | 没有 stage/commit/push |

## 9. 实施后的交接

最终实施报告必须说明：

- 完成了哪些阶段；
- 修改了哪些文件；
- 验证结果和缺口；
- 是否迁移了项目和工作区 memory；
- 当前项目 checker 是否保留；
- 本地未提交状态；
- 延期的数据库/索引或 AI 审查工作。

实施完成不等于 Git 发布、集成、发布版本或 live 部署完成。
