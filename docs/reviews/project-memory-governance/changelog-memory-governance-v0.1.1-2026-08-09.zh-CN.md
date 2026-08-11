# Memory Governance v0.1.1 本轮变更记录

Status: Evidence / historical；记录 v0.1.1 文档修订轮次，不构成 Protocol 批准或 Git 发布。

Date: 2026-08-09

## 1. 本轮目的

根据 [复审结果](review-result-review-protocol-and-plan-memory-governance-v0.1-2026-08-09.zh-CN.md)，
将三个 P1 和直接关联的 P2/P3 问题落实到新的 v0.1.1 Draft，并使关联 Active
plan 与 Protocol 版本一致。

## 2. 变更清单

| 文件 | 变更 |
|---|---|
| [Protocol v0.1.1](memory-governance-protocol-v0.1.1-2026-08-09.zh-CN.md) | 新建修订候选稿；落实阶段编号、D09、`operation_key` 三个 P1 的文本修订 |
| [Protocol v0.1 历史稿](memory-governance-protocol-v0.1-2026-08-08.zh-CN.md) | 仅增加 superseded 状态横幅和新来源链接 |
| [Active plan v0.1.1](plan-memory-governance-v0.1.1-2026-08-09.zh-CN.md) | 新建与 Protocol 对齐的计划，本文唯一维护数字 Phase |
| [旧计划 v0.1](plan-memory-governance-v0.1-2026-08-09.zh-CN.md) | 仅增加 superseded 状态横幅和新计划链接 |
| [README](README.md) | 将 Active source/plan 路由到 v0.1.1，并登记本轮文件 |
| 本记录 | 记录范围、验证、未执行项和未授权边界 |

## 3. 规范修订摘要

- Protocol §14 不再定义独立数字 Phase，实施阶段由 v0.1.1 Active plan 统一维护；
- D09 统一为「应尽早持久化；写入并验证成功后方可提升为已确认」；
- `operation_key` 固定规范化输入、SHA-256 格式、运行实例字段排除和冲突停止语义；
- `claim_id` 固定作用域、ULID、碰撞检查、替代关系和重试复用；
- D01–D12 增加状态列和 v0.1→v0.1.1 变更映射，D11 保持 deferred；
- 官方引用补充定位和 2026-08-08 访问核验日期；
- 统一 history 文件名和 event_id 时间格式；
- 增加 MGP-14 符号链接越界场景；
- 修正 README 的新增文件维护规则和译文表述。

## 4. 验证

- `make test`：28 项测试通过；
- `bash -n scripts/*.sh .githooks/pre-commit`：通过；
- `python3 -m py_compile scripts/*.py tests/*.py`：通过；
- 新增/更新文档的链接、文件状态和空白检查：通过。

## 5. 未执行和未授权事项

- 未执行 `make bootstrap`、隔离 HOME 双跑或 fixture 场景；
- 未安装 `.agents/rules/memory-protocol.md`；
- 未修改运行时、hook、主机配置或 Reality Ops；
- 未执行 Git stage、commit、push 或 PR；
- v0.1.1 仍是 Draft，下一步为 Phase 1 定向复审。
