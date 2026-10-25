# StudyScope

对话式学习档案。家教会话用于学习，页面用于查看学习路径与整理后的笔记。当前只有机器学习领域，已开始家教学习；当前路线与接续位置见 `learning/scopes/ml-ai/path.json`。

## 结构

```text
web/                       唯一正式页面：HTML、CSS、JavaScript
learning/
  agreement.md             通用学习约定
  scopes.json              Scope 索引
  scopes/ml-ai/
    profile.md             本领域目标与学习画像
    path.json              Stage / Topic、问题、实际进度与接续信息
    sources.json           来源索引
    notes/index.json       Scope / Stage / Topic 笔记索引
    checkpoints/           每次学习的短记录
scripts/
  build.py                 构建正式静态页面
  check.py                 检查档案关联、产物与资源路径
  serve.py                 本地预览正式源码
.github/workflows/pages.yml GitHub Pages 发布
AGENTS.md                  项目全局原则与家教工作约定
dist/                      构建产物，不提交
```

Python 3.10+，仅标准库；前端无第三方依赖。

## 本地查看与构建

```powershell
python scripts/serve.py
```

打开 `http://127.0.0.1:8765/`。预览直接读取 `web/` 和真实 `learning/`，修改文件后刷新即可。它只在本机提供静态文件，没有写入接口。

```powershell
python scripts/build.py
python scripts/check.py
```

构建把 `web/` 与 `learning/` 复制到 `dist/`，生成 `version.json`；页面信息显示内容版本、更新时间和源提交，提交号后 `*` 表示本地含未提交改动。资源使用相对路径，兼容 Pages 的 `/StudyScope/` 子路径。检查覆盖实际档案与笔记关联、复制后的文件和内容版本；页面交互仍需浏览器验证。

## 维护学习档案

固定层级为 **Scope → Stage → Topic**。磁盘按 Scope 分目录，Stage 和 Topic 在 `path.json` 中嵌套维护，不另建目录。阶段及主题数组的顺序直接决定路径和箭头；只保留这一份计划与进度。

- `stages[].topics[]`：Topic 标题、摘要、要理解的问题与实际状态（`not_started` / `in_progress` / `completed`）。
- `current_topic`：当前 Topic 的 id；位置不代表掌握。
- `resume`：当前问题、上次停留和一个下一步。
- `notes/index.json`：每篇笔记的 `level`、`target_id`、`title`、`file`、`updated_at`；Markdown 文件与索引放在同一 `notes/` 目录。

Scope 笔记包含 Stage 子笔记，Stage 笔记包含 Topic 子笔记。点击标题阅读，旁边箭头展开/收起子笔记；目录整栏也可收起。Scope 笔记简述领域，Stage 笔记概述阶段，具体知识总结放在各自的 Topic 笔记中。进行中的 Topic 也可以有笔记，已完成的 Topic 必须有笔记；笔记存在不代表完成。当前已登记 ML 领域、Stage 1、Topic 1 和 Topic 2 四篇笔记。

每次真实学习结束后，先展示短总结并接受纠正，再写一份 checkpoint：解决的问题、理解证据、未解问题、一个下一步和来源。同步更新路径；有价值的内容整理为笔记。不要把开发或部署当作学习进展。

新会话从 `AGENTS.md`、通用约定、Scope 索引、当前画像/路径与最新 checkpoint 接续，不假设继承其他聊天上下文。

## 发布与恢复

目标仓库：[dntkm/StudyScope](https://github.com/dntkm/StudyScope)。Pages 使用已经配置的 **GitHub Actions**；推送到 `main` 会构建、检查并部署 `dist/`，不提交构建产物。

发布后检查 Actions 的部署结果和线上 `version.json`，再确认页面导航、笔记、资源与版本一致。本地构建成功不等于线上已更新。

旧版页面、旧构建脚本与 `docs/` 保留在 Git 历史（本轮清理前为 `90b5e0d`）；需要时从对应 commit 恢复，不在当前目录维护兼容版本。

公开内容限于学习计划、进度和整理后的记录。原始聊天、私人信息、其他项目数据、内部助手笔记与凭据不入库。开发与维护遵循 **如无必要，勿增实体**，具体约定见 `AGENTS.md`。
