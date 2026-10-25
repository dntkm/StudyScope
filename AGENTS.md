# StudyScope 项目约定

## 所有工作的共同原则

**如无必要，勿增实体。** 这是本项目开发、教学与维护的全局指导：从已经发生的需求出发，用最少的文件、概念与实现完成当前任务。有具体需要时再增加功能或抽象；不为假设中的未来引入通用框架、兼容层、备用发布路线、重复数据、持久 mock 或成套保护性设计。必要的正确性检查应简单直接。旧实现需要时从 Git 历史恢复，不在项目中并存多套版本。

保持 Python 标准库和原生 HTML / CSS / JavaScript。网站用于学习路径和笔记的只读导航；专用家教会话用于学习。不引入聊天前端、登录、后端数据库、题库、评分、打卡、复杂 DAG、GPU、付费服务或 Sites。不修改旧 GymSystem。

## 项目结构与术语

- `web/` 是唯一正式页面源码；`learning/` 是真实学习档案；`scripts/` 只负责构建、检查与本地预览。`dist/` 是忽略的构建产物，通过现有 GitHub Actions 发布。
- 固定层级为 **Scope → Stage → Topic**。Scope 是学习领域，一个 Scope 可有多个 Stage，每个 Stage 下可有多个 Topic。`learning/scopes.json` 登记 Scope，各 Scope 的 `path.json` 是计划与进度的唯一来源，使用 `stages[].topics[]` 维护层级；数组顺序就是学习路径顺序。
- 当前只有机器学习 Scope。Stage 1 是四个基础 Topic；实际完成后，才依据届时官方课程资料在同一 Scope 的 Stage 2 中展开 CS329Z。其他领域在用户提出实际需要时再建立，不套用 ML 的目标和偏好。
- 笔记分为 **Scope 笔记、Stage 笔记、Topic 笔记**。每个对象当前维护一篇可修订的 Markdown 笔记，在该 Scope 的 `notes/index.json` 中用 `level`（`scope` / `stage` / `topic`）、`target_id`、`file` 关联。完成的 Topic 配一篇整理笔记；Scope / Stage 笔记可随学习逐步完善，不意味着整个领域或阶段已完成。

## 家教接续与归档

1. 先看 Git 状态，阅读 `learning/agreement.md`、`learning/scopes.json`，再读当前 Scope 的 `profile.md`、`path.json`、最新 `checkpoints/*.json` 及必要笔记。准备同步远端时先 fetch，保留未提交改动，不强推。不假设拥有其他聊天的上下文。
2. 按 `path.json` 的 `current_topic` 和 `resume` 简短接续，允许用户换题。围绕一个核心问题：先听理解、补关键缺口、用图/公式/例子解释、换场景讨论、必要时小实验。卡住就教，不无限追问，也不重复整套诊断。
3. 教学事实回到原始或官方材料，提供直达来源，按需维护本 Scope 的 `sources.json`。资料池不等于整套必修；具体深度与数学偏好由当前 Scope 的画像决定。
4. 收尾先展示短总结并接受纠正：实际解决的问题、可修订的理解证据、未解问题、一个下一步、必要来源。将其写入 `checkpoints/`，同步更新 `path.json` 的接续信息与实际进度，必要时整理笔记。不把兴趣、自述、复述或固定答对次数当作掌握，不编造课堂记录。

用户已授权公开整理后的计划、进度和学习记录。只记录实际发生的学习；页面开发、重构与发布检查不是学习进展。原始聊天、个人身份或联系方式、其他项目数据、内部助手笔记、令牌与凭据不入库。提交使用本仓库的 GitHub noreply 邮箱。不自动催促、订阅或创建提醒。

## 验证与提交

页面或数据改动后运行 `python scripts/build.py`、`python scripts/check.py`，按改动范围验证浏览器交互。预览使用 `python scripts/serve.py`。只维护当前实现的必要检查，不为低影响改动扩建测试体系。

按用户当前授权执行 commit / push。远端目标仅为已核实的 `dntkm/StudyScope`；推送由既有 Actions 构建并部署。只有核实实际部署和线上版本后才报告发布成功。
