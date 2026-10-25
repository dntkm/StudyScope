# StudyScope

一次弄懂一个真想了解的问题。StudyScope 是可逐步涵盖不同领域的对话式学习档案；家教会话用于学习，网站只展示“现在 / 计划 / 足迹”。

当前仅有一个真实领域：**机器学习 / AI Agent**。只有这个领域以 CS329Z 为方向目标；以后其他领域可以有自己的目标和学习方式。

仓库：[dntkm/StudyScope](https://github.com/dntkm/StudyScope)。Pages 的实际启用状态与步骤见 [PUBLISH.md](PUBLISH.md)，不要把仓库已上传误认为网页已上线。

## 从这里接续

依次读取：

1. [通用学习约定](learning/agreement.md) 与 [当前领域索引](learning/scopes.json)。
2. 索引 `active_scope` 所对应目录的 `profile.md`、`map.json` 与最新 `checkpoints/*.json`。

当前为 [ML 领域画像](learning/scopes/ml-ai/profile.md)、[问题地图](learning/scopes/ml-ai/map.json) 与 [初始化记录](learning/scopes/ml-ai/checkpoints/2026-10-25-setup.json)。状态仍是：**目标与学习方式已对齐，待首次家教学习。**

首个建议问题：**同一份数据，为什么不同损失会学到不同结果？** 可以随时换题。

新会话可以直接说：

> 请在 StudyScope 仓库中按 AGENTS.md 读取通用约定、领域索引和当前领域的画像、问题地图及最新 checkpoint，简短接续上次停留。不要假设拥有其他聊天上下文。

## 日常更新

一次真实教学结束后，先展示短总结并接受纠正，再在当前领域 `checkpoints/` 新增一份 JSON：

```json
{
  "schema_version": 1,
  "date": "YYYY-MM-DD",
  "kind": "learning",
  "title": "本次问题",
  "resolved": ["今天实际解决的问题"],
  "evidence": ["基于讨论的可修订观察，不是分数"],
  "open_questions": ["尚未解决的问题"],
  "next_step": "一个下一步",
  "source_ids": ["本领域 sources.json 中的来源 id"],
  "source_note": "必要的引用范围说明"
}
```

同步更新该领域问题地图中的当前停留、一个下一步与更新时间；来源按需加入本领域 `sources.json`。切换领域时才改 `scopes.json`；用户真正提出新领域后再建立对应档案，不预生成课程。

```powershell
python scripts/build.py
python scripts/check.py --flow
```

可双击 `dist/index.html` 查看本地预览，也可运行 `python -m http.server 8000 --directory dist --bind 127.0.0.1`。本地地址不是跨设备发布链接。

使用 `main/docs` 分支静态发布时，更新档案后再运行：

```powershell
python scripts/build.py --docs
python scripts/check.py --docs
git add learning scripts web docs
git commit -m "Update learning checkpoint"
git push
```

`docs/` 是生成产物，不手工修改。路径全部相对当前页面，兼容 GitHub Pages 的项目子路径 `/StudyScope/`，无需前端路由或脚本。

Python 3.10+，仅标准库，无第三方依赖。源内容指纹用于核对实际展示版本，`version.json` 同时记录构建时间和源提交；分支预构建的源提交与包含产物的发布提交可能不同。检查范围见 [VALIDATION.md](VALIDATION.md)。

公开内容仅限学习档案。原始聊天、私人信息、其他项目数据与内部助手笔记不入库。
