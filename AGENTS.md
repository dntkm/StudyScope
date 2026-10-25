# StudyScope 项目约定

## 所有工作的共同原则

**如无必要，勿增实体。** 这是本项目开发、教学与维护的全局指导：从已经发生的需求出发，用最少的文件、概念与实现完成当前任务。有具体需要时再增加功能或抽象；不为假设中的未来引入通用框架、兼容层、备用发布路线、重复数据、持久 mock 或成套保护性设计。必要的正确性检查应简单直接。旧实现需要时从 Git 历史恢复，不在项目中并存多套版本。

保持 Python 标准库和原生 HTML / CSS / JavaScript；公式使用随站点提供的 KaTeX，不引入前端构建工具。网站用于学习路径和笔记的只读导航；专用家教会话用于学习。不引入聊天前端、登录、后端数据库、题库、评分、打卡、复杂 DAG、GPU、付费服务或 Sites。不修改旧 GymSystem。

## 项目结构与术语

- `web/` 是唯一正式页面源码；`learning/` 是真实学习档案；`scripts/` 只负责构建、检查与本地预览。`dist/` 是忽略的构建产物，通过现有 GitHub Actions 发布。
- 固定层级为 **Scope → Stage → Topic**。Scope 是学习领域，一个 Scope 可有多个 Stage，每个 Stage 下可有多个 Topic。`learning/scopes.json` 登记 Scope，各 Scope 的 `path.json` 是计划与进度的唯一来源，使用 `stages[].topics[]` 维护层级；数组顺序就是学习路径顺序。
- 当前只有机器学习 Scope。Stage 1 的基础 Topic 与顺序以当前 Scope 的 `path.json` 为准；实际完成后，才依据届时官方课程资料在同一 Scope 的 Stage 2 中展开 CS329Z。其他领域在用户提出实际需要时再建立，不套用 ML 的目标和偏好。
- 笔记分别对应 **Scope、Stage、Topic**，每个对象维护一篇可修订的 Markdown 笔记，在该 Scope 的 `notes/index.json` 中用 `level`（`scope` / `stage` / `topic`）、`target_id`、`file` 关联。Scope 笔记简述领域范围与学习目标；Stage 笔记简述阶段目标及其 Topic 之间的关系；Topic 笔记承载该主题的知识总结、符号、公式、例子与未解问题，不把多个 Topic 的详细内容汇总到 Scope 或 Stage 概述中。
- Topic 进行中即可创建对应笔记并持续修订；已完成的 Topic 必须有整理笔记。笔记的存在不代表掌握或完成，进度仍按实际学习独立记录在 `path.json` 中。
- 笔记文件目录与 Scope → Stage → Topic 一致：Scope 笔记为 `notes/index.md`，Stage 笔记为 `notes/<stage-id>/index.md`，Topic 笔记为 `notes/<stage-id>/<topic-id>.md`。`notes/index.json` 的 `file` 相对于 `notes/`；只为实际已有笔记建立目录，层级与顺序仍以 `path.json` 为准。调整页面、目录或渲染时，保留知识正文和学习进度，不顺带改写总结或学习记录。
- 文档中的数学符号与公式尽量使用规范 LaTeX：行内公式用 `$...$`，独立公式用 `$$...$$`；矩阵、上下标、分式和偏导数使用相应 LaTeX 写法，避免用纯文本拼接或普通代码块模拟数学排版。实际程序代码、命令、路径和标识符仍使用代码格式。符号先解释含义，全文保持一致。

## 家教接续与归档

1. 先看 Git 状态，阅读 `learning/agreement.md`、`learning/scopes.json`，再读当前 Scope 的 `profile.md`、`path.json`、最新 `checkpoints/*.json` 及必要笔记。准备同步远端时先 fetch，保留未提交改动，不强推。不假设拥有其他聊天的上下文。
2. 按 `path.json` 的 `current_topic` 和 `resume` 简短接续，允许用户换题。围绕一个核心问题：先听理解、补关键缺口、用图/公式/例子解释、换场景讨论、必要时小实验。卡住就教，不无限追问，也不重复整套诊断。
3. 教学事实回到原始或官方材料，提供直达来源，按需维护本 Scope 的 `sources.json`。资料池不等于整套必修；具体深度与数学偏好由当前 Scope 的画像决定。
4. 收尾先展示短总结并接受纠正：实际解决的问题、可修订的理解证据、未解问题、一个下一步、必要来源。将其写入 `checkpoints/`，同步更新 `path.json` 的接续信息与实际进度，必要时整理笔记。不把兴趣、自述、复述或固定答对次数当作掌握，不编造课堂记录。

用户已授权公开整理后的计划、进度和学习记录。只记录实际发生的学习；页面开发、重构与发布检查不是学习进展。原始聊天、个人身份或联系方式、其他项目数据、内部助手笔记、令牌与凭据不入库。提交使用本仓库的 GitHub noreply 邮箱。不自动催促、订阅或创建提醒。

## 验证与提交

页面或数据改动后运行 `python scripts/build.py`、`python scripts/check.py`，按改动范围验证浏览器交互。预览使用 `python scripts/serve.py`。只维护当前实现的必要检查，不为低影响改动扩建测试体系。

按用户当前授权执行 commit / push。远端目标仅为已核实的 `dntkm/StudyScope`；推送由既有 Actions 构建并部署。只有核实实际部署和线上版本后才报告发布成功。
