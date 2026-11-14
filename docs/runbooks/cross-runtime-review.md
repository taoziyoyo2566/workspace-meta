# 跨运行时审阅：请求模板与输出格式

什么时候要请另一家运行时的 AI 审阅，见
[`review.md` Independent Review](../../.agents/rules/review.md#independent-review)；
怎样以只读方式运行审阅方，见它所属 runtime 模块的 Read-Only Review Runs 一节
（[Codex](../../.agents/rules/codex-runtime.md#read-only-review-runs)、
[Claude](../../.agents/rules/claude-runtime.md#read-only-review-runs)）。
本 runbook 只给表单：第一轮请求、针对性复审请求，以及两份输出格式
[`cross-runtime-review.schema.json`](cross-runtime-review.schema.json) 和
[`cross-runtime-recheck.schema.json`](cross-runtime-recheck.schema.json)。
表单和规则不一致时，以规则为准。

## 1. 用法

- 每用一次，把填好的请求和对应的输出格式复制进证据库
  （[`documentation.md` Committed And Temporary Records](../../.agents/rules/documentation.md#committed-and-temporary-records)）。
- 填好所有 `<…>`，删掉不适用的内容；Q1 到 Q5 都保留，用不上的那题答"不适用"。
- 审阅方的版本变了，先按它的 runtime 模块做一次带记录的试跑，再用它审阅。
- 审阅方用配置的模型和推理强度
  （[`capabilities.md` Delegation](../../.agents/rules/capabilities.md#delegation)）。
- 跑完先检查：答案符合输出格式；条数没超过请求里写的上限；每题只答一次；
  在审阅方 runtime 模块指明的完整记录里，没有成功的写入，只读设定确实生效。
  答案里关于"运行了什么命令"的描述，要和这份记录对得上。
- 逐条核对每条意见的证据
  （[`review.md` Problem Reports](../../.agents/rules/review.md#problem-reports)），
  分成接受、不接受、由 operator 决定三类，各附建议，交给 operator。
- 请求、输出格式、答案、事件日志、实际运行的命令行、起止时间和退出码，以及审阅方
  runtime 模块指明的完整记录的摘录（附来源路径和 sha256），都留在证据库。
- 改完后做一次针对性复审（第 3 节），然后停止
  （[`review.md` Completion](../../.agents/rules/review.md#completion)）。

## 2. 第一轮请求

输出格式用 `cross-runtime-review.schema.json`，字段：`verdict`（proceed、
proceed_with_changes 或 rethink）、`verdict_reason`、`answers`（每题一条）、
`findings`、`facts_checked`、`notes`。

````text
# 审阅请求：<对象>，第 1 轮

你是独立审阅者，只读。被审对象由另一个 AI（<作者所用的运行时>）写成。operator
会根据你的意见和作者逐条核对的结果作决定。

## 审阅目标

只回答一个问题：<问题>。你的意见用来支持这些待定的决定：<决定>。
<operator 已定或保留的事项> 不在审阅范围内，除非它所依据的事实有错。

## 材料

- 被审对象：<路径>（<提交号或 sha256>）。
- 官方文档或其副本：<路径或链接>。
- 需要时可读的规则：<路径>。
- 本机已装的版本：<版本>。你可以运行自己的 --version 和 --help 来核对。

## 问题

- Q1 方向：<问题>
- Q2 你所属运行时的自身事实：用本机程序、它的帮助和官方文档核对；没有就答"不适用"。
- Q3 其他事实：只抽查决定所依据的那些。
- Q4 步骤与检查：能不能执行、能不能验证，有没有明显做过头的地方。
- Q5 风险：没列出的风险，或与规则冲突的地方。

## 审阅标准

- 只报会改变决定、阶段、检查或所依据事实的问题；不报措辞、风格和"还可以考虑"。
- 严重度：<粘贴 review.md Severity 中 P0 到 P2 的定义>。
- 每条附证据，并分清缺陷（现在就成立）和风险（有发生的机制）。
- 最多 <10> 条，其中 P2 最多 <3> 条；省略了多少条写在 notes 里。
- 没有问题也是有效结论，但要写明查了什么。
- <记录位置> 中已定的决定照旧，除非它所依据的事实有错。

## 防止跑题

- 每条意见只对应一题，只提最小修改。
- 看起来会推翻方向的问题，按 P0 或 P1 记下证据和最小的替代做法，其余各题照常回答。
- 不审其他工作树、方案或规则本身；只在被审对象与规则冲突时指出。
- 每题的证据够了就停。

## 限制

不改任何文件；不改 Git 状态，fetch 也不做；不安装；不做网络写入；不启动其他
代理。不读凭据文件，答案里不出现密钥。按输出格式给出 JSON，用 <语言> 写，技术
名词保留原文。
````

## 3. 针对性复审请求

输出格式用 `cross-runtime-recheck.schema.json`，字段：`verdict`（review_closed
或 fix_needed）、`verdict_reason`、`resolutions`（上一轮每条意见一条）、
`new_findings`、`notes`。复审接着第一轮的审阅会话进行时，它保留第一轮的上下文。

````text
# 针对性复审：<对象>，第 2 轮

## 目标

逐条判断上一轮的意见是否已解决（resolved、partially_resolved 或
not_resolved），并指出这次改动新引入的 P0 或 P1 问题。

## 范围

<改动的 diff>、<改动前的文本>、<改动后的文本>、上一轮的答案和作者的核对结果。
没改的部分和已定的决定不在范围内。

## 标准

- 每条结论附证据和剩下的缺口。
- 新问题最多 <3> 条，只限 P0 和 P1，只提最小修改，不提新方向。

## 限制

同第一轮。
````
