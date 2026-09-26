# 社区依据与本地取舍

本资料选取原作者、官方文档和研究机构的一手材料。它们不是一套统一的强制标准：Google 文档是工程实践，arc42 与 C4 是表达方法，DORA 是交付能力研究，NIST SSDF 是安全开发框架。这里给出适用于本工作区的裁剪，不宣称认证或完整实施任何框架。

## 采用了什么

| 来源 | 原资料支持的做法 | 本地应用与边界 |
|---|---|---|
| [Google：评审标准](https://google.github.io/eng-practices/review/reviewer/standard.html) | 持续改善代码健康度，区分必要修改与细节建议 | 评审基于正确性、影响和证据，不要求达到个人理想中的完美 |
| [Google：小型变更](https://google.github.io/eng-practices/review/developer/small-cls.html) | 保持变更集中、自包含，连同相关测试交付 | 按目的拆分，不设统一行数上限 |
| [Google：评审关注点](https://google.github.io/eng-practices/review/reviewer/looking-for.html) | 评审设计、行为、复杂度、测试等，判断测试能否发现错误 | 对实质行为缺陷检查回归用例的检出能力；不为简单文案新增行为测试 |
| [Software Engineering at Google：Documentation](https://abseil.io/resources/swe-book/html/ch10.html) | 设计文档说明目标、策略、关键选择与取舍；文档围绕读者需要 | 按决策需要写设计，不复制完整实现或强制固定篇幅 |
| [arc42：质量要求](https://docs.arc42.org/section-10/) | 用具体、可衡量的场景表达质量；已有表达足够时可省略额外展开 | 验收写条件、动作、结果和证明方式，不要求十二章全部填写 |
| [C4：图的选择](https://c4model.com/diagrams)与[图示说明](https://c4model.com/diagrams/notation) | 按价值选择架构层次，关系应有具体含义 | 需要时画局部边界或时序，不要求所有项目画四层图 |
| [Michael Nygard：ADR](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) | 为重要架构选择保留简短背景、决定、后果和状态 | 是否独立成文按长期检索需要决定；已有方案能承载时不重复 |
| [Diátaxis](https://diataxis.fr/) | 区分学习、完成任务、查阅和理解四种读者需求 | 用来判断内容归属；不要求每个项目建立四套文档目录 |
| [The Twelve-Factor App：Config](https://12factor.net/config) | 将部署间变化的配置与代码分离 | 配置与代码分离是依据；把所有运营可调策略作为数据，是本工作区进一步选择，不等于原文要求所有数据放环境变量 |
| [NIST SSDF 1.1](https://csrc.nist.gov/pubs/sp/800/218/final)，[PW.4 原文](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf) | 将安全实践纳入开发流程，核查复用组件来源、维护、漏洞和完整性 | 对变动依赖及相关传递依赖应用检查，复用锁文件和工具，不要求逐包审批或另建清单 |
| [OWASP：威胁建模](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html) | 识别设计、威胁、应对与验证，关注边界和数据流 | 安全相关设计展开受影响的资产、角色和失败场景；不让每次修改都填写大型模型 |
| [OWASP WSTG：授权绕过测试](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/05-Authorization_Testing/02-Testing_for_Bypassing_Authorization_Schema/) | 检查未认证访问、水平越权和垂直越权 | 权限变更验证相关允许及拒绝路径，具体角色矩阵由项目维护；预期的审计、失败计数等副作用仍需验证，参见 [OWASP 认证防护](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html#account-lockout) |
| [DORA：部署自动化](https://dora.dev/capabilities/deployment-automation/) | 环境配置与制品分离，各环境使用同一包，部署后检查功能 | 验证结果关联实际发布对象；源码部署记录可追溯输入，不强制引入制品平台 |
| [DORA：简化变更审批](https://dora.dev/capabilities/streamlining-change-approval/) | 开发过程中的评审和自动检查支持有效变更管理 | 质量要求放进已有工作流，不新增通用审批层；保留用户授权和项目规定的实际操作边界 |
| [Google SRE：Canarying Releases](https://sre.google/workbook/canarying-releases/) | 用有限范围的发布、观察和判断降低风险 | 有条件时渐进发布；单节点采用与风险相称的验证和恢复方案，不强制复杂平台 |

## 哪些是本地约定

以下选择是结合工作区需求作出的判断，不能归为上述社区来源的统一要求：

- 通用方法归 workspace-meta，项目架构、命令、设定和操作结果归项目仓库。
- 可调整的运行设定和策略选择以数据管理；代码负责逻辑、校验与执行。具体存储及生效机制由项目设计。
- 沿用现有 Plan、Changelog 和授权规则，不从外部框架引入新的审批层级。
- 使用简短任务清单；只有用户需要或操作可追溯性确有需要时保存操作记录。
- 手册面向阅读与示例，共享规则保留唯一规范归属。模板和图表帮助表达，不以数量判断设计质量。

## 如何维护

发现实际失败或有新的能力需求时，先定位现有规则或项目约定，再决定修改。外部工具能力、版本支持和安全行为成为关键依据时，应重新查证相关一手资料。本页保留方法的来源，不充当某个产品版本的兼容性或安全认证清单。
