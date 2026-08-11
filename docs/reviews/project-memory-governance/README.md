# project-memory-governance 文档索引

Status: Active navigation
Date: 2026-08-11

本目录保存 Memory Governance 从需求、方案、审查到协议草案的形成证据。目录中
只有当前 Protocol Draft 可以作为后续协议起草的工作来源；其他文档必须按照下面
的状态读取。

## 首先阅读

1. [后续实施与文档治理计划 v0.1.2](plan-memory-governance-v0.1.2-2026-08-11.zh-CN.md)
2. [Memory Governance Protocol v0.1.2 草案](memory-governance-protocol-v0.1.2-2026-08-11.zh-CN.md)
3. [Memory Governance v0.1.2 变更记录](changelog-memory-governance-v0.1.2-2026-08-11.zh-CN.md)
4. [对话需求与决策记录](conversation-requirements-2026-08-07.zh-CN.md)
5. [最新复审备忘录](review-response-review-analysis-design-memory-governance-v0.1-2026-08-08.zh-CN.md)
6. [Protocol 与实施计划审查](review-protocol-and-plan-memory-governance-v0.1-2026-08-09.zh-CN.md)
7. [该审查的复审结果](review-result-review-protocol-and-plan-memory-governance-v0.1-2026-08-09.zh-CN.md)
8. [方向与可行性审查 2026-08-11](review-direction-memory-governance-2026-08-11.zh-CN.md)
9. [方向审查的独立调查结果 2026-08-11](investigation-direction-memory-governance-2026-08-11.zh-CN.md)
10. [对该独立调查的响应 2026-08-11](response-investigation-direction-memory-governance-2026-08-11.zh-CN.md)

如果需要核查某项结论，再按时间顺序读取审查和响应文档；不要从历史方案或旧计划
直接开始实施。

## 当前工作来源

| 状态 | 文档 | 用途 |
|---|---|---|
| Active plan | plan-memory-governance-v0.1.2-2026-08-11.zh-CN.md | 当前阶段、出口、风险和文档处置 |
| Active working source | memory-governance-protocol-v0.1.2-2026-08-11.zh-CN.md | Protocol v0.1.2 freshness MVP 候选规范 |
| Active navigation | 本 README | 文档发现和状态路由 |

当前 Protocol v0.1.2 是 Draft，尚未安装到 .agents/rules/memory-protocol.md，也不授权
运行时修改、项目迁移或 Git 发布。当前工作区没有可定位的 v0.0.1；v0.1.1 是直接前版，
已转为 reference-only。

## 当前轮修订记录

- [Memory Governance v0.1.2 本轮变更记录](changelog-memory-governance-v0.1.2-2026-08-11.zh-CN.md)
- [Memory Governance v0.1.1 本轮变更记录](changelog-memory-governance-v0.1.1-2026-08-09.zh-CN.md)

## 历史需求和审查证据

以下文档保留，因为它们能解释用户意图、被否决的解释、审查发现和设计演进：

- [Conversation Requirements 英文记录](conversation-requirements-2026-08-07.md)
- [对话需求与决策记录中文版](conversation-requirements-2026-08-07.zh-CN.md)
- [初始阻塞审查英文版](review-project-workspace-memory-2026-08-08.md)
- [初始阻塞审查中文版](review-project-workspace-memory-2026-08-08.zh-CN.md)
- [设计深度分析](analysis-design-memory-governance-v0.1-2026-08-08.zh-CN.md)
- [对分析的复审](review-analysis-design-memory-governance-v0.1-2026-08-08.zh-CN.md)
- [对复审的响应](response-review-analysis-design-memory-governance-v0.1-2026-08-08.zh-CN.md)
- [对响应的最新复审](review-response-review-analysis-design-memory-governance-v0.1-2026-08-08.zh-CN.md)

这些文档是 Evidence / historical，不是当前协议来源。

## 已替代的方案和计划

以下文档仍保留用于历史参考，但已经不能直接执行：

- [Protocol v0.1 历史稿](memory-governance-protocol-v0.1-2026-08-08.zh-CN.md)
- [旧实施计划 v0.1](plan-memory-governance-v0.1-2026-08-09.zh-CN.md)
- [Protocol v0.1.1 直接前版（reference-only）](memory-governance-protocol-v0.1.1-2026-08-09.zh-CN.md)
- [实施计划 v0.1.1 直接前版（reference-only）](plan-memory-governance-v0.1.1-2026-08-09.zh-CN.md)
- [设计基线](design-memory-governance-v0.1-2026-08-08.zh-CN.md)
- [架构方案英文版](solution-project-workspace-memory.md)
- [架构方案中文版](solution-project-workspace-memory.zh-CN.md)
- [旧实施计划英文版](plan-project-workspace-memory-2026-08-07.md)
- [旧实施计划中文版](plan-project-workspace-memory-2026-08-07.zh-CN.md)

它们的所有权模型和部分原则已经进入 Protocol Draft，但旧路径、阶段和验收条件
不应被继续当作当前计划。

## 废止底稿

[memory-plan.md](memory-plan.md) 是早期混合底稿。它包含需求、方案、多个协议草稿
和阶段计划，内部存在冲突，已经标记为 Deprecated / do-not-use。它只用于追溯早期
思路，不得作为规范、计划或实现依据。

## 文档治理规则

- 新的协议规则只能进入 Protocol Draft 或其后续唯一规范来源；
- 新的阶段工作只能进入当前计划或其明确的 superseding plan；
- 新增审查、证据或计划文件时，产出该文件的同一轮必须同步更新本 README，并重新核对相对链接；
- 历史文档不得静默改写为当前规范；
- 译文（任何语言）必须标明对应源版本和翻译属性；
- Reality Ops 的项目文档、checker 和迁移记录属于独立 Git 仓库；
- 文档版本轮次只做有记录的本地修订和导航维护，不物理删除历史文件；
- 任何 Git stage、commit、push 或 PR 都需要单独授权。
