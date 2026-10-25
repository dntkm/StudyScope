# 发布与版本核对

目标仓库：[dntkm/StudyScope](https://github.com/dntkm/StudyScope)，公开，默认分支 `main`。初始化前已核实仓库为空；不覆盖其他项目。

## 一次性开启 Pages

文件上传成功后，打开该仓库 **Settings → Pages**：

- 如果仓库已有可运行的 `Publish learning archive` 工作流，将 Source 设为 **GitHub Actions**，再在 Actions 中运行一次该工作流；以后 `main` 更新自动构建和发布。
- 如果工作流写入不受支持，使用已构建并提交的 `docs/`：Source 选择 **Deploy from a branch**，Branch 选 **main**，目录选 **/docs**，点击 **Save**。以后提交更新后的 `docs/` 即可自动发布。

这里只选择其中一条路线。此项目无需个人访问令牌、登录功能、数据库或其他托管平台。

## 验证

未确认 Pages 配置及构建成功之前，不声称页面已上线，也不猜线上 URL。实际地址从 Pages 设置或成功部署的 environment 取得。

检查“现在 / 计划 / 足迹”导航、来源与归档链接、刷新和直接打开锚点；桌面与手机下确认文字清晰且无横向溢出。读取线上 `version.json`，将 `content_version` 与本次构建的内容指纹对照。

Actions 构建的 `commit` 是实际 workflow head。`main/docs` 预构建中的 `commit` 是内容源提交，包含 `docs/` 的发布提交会不同；以成功 Pages build 的 commit 标识部署，以 `content_version` 标识实际页面内容，不能混为同一个 Git SHA。

## 本地与远程历史

首次本地项目的历史已保留。通过仓库内容 API 上传会产生独立的远程 Git 提交，不保证与本地提交号相同。接续时先保存本地历史分支 / bundle，再 fetch 远程分支；不要强推覆盖任一历史。

日常档案更新流程：领域文件 → Python 构建与检查 → 提交 / 内容 API 上传 → Pages 自动发布 → 对照线上版本。若使用 `main/docs`，必须一起上传更新后的 `docs/`；若使用 Actions，服务器会从源文件重新构建。

GitHub 官方说明：[从分支或 Actions 配置发布来源](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。
