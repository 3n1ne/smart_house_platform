# 智能房屋租赁系统

基于 Vue 3、Flask 和 MySQL 的房屋租赁管理系统，覆盖房源发布、房源搜索、预约看房、合同签署、租金支付、消息沟通、维修投诉、新闻公告、管理员报表和系统监控。

## 项目结构

```text
backend/        Flask API、数据模型、迁移脚本和后端测试
frontend/       Vue 3 + Vite 前端应用
deploy/         生产反向代理参考配置
scripts/        部署、备份、性能、安全和兼容性验收脚本
docs/           API、数据库、部署与验收文档
requirement.md  原始需求说明
```

主应用只有 `backend/` 和 `frontend/` 两个工程。测试缓存、构建产物、依赖目录和旧 React 原型不属于源码结构。

## 后端运行

后端默认读取 MySQL 连接。开发前先创建虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\pip.exe install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
```

按本机数据库修改 `backend\.env` 中的 `DATABASE_URI` 后启动：

```powershell
Set-Location backend
..\.venv\Scripts\flask.exe --app run:app run
```

生产或生产等价环境不要依赖自动建表，应执行 Alembic 迁移：

```powershell
Set-Location backend
$env:FLASK_CONFIG = "production"
$env:AUTO_CREATE_DB = "false"
..\.venv\Scripts\flask.exe --app run:app db upgrade
..\.venv\Scripts\flask.exe --app run:app seed-admin
```

## 前端运行

```powershell
Set-Location frontend
npm install
npm run dev
```

前端环境变量在 `frontend\.env.example` 中。默认同源访问 `/api` 和 `/uploads`；前后端分离部署时调整 `VITE_API_BASE_URL` 和 `VITE_ASSET_BASE_URL`。

## 验证命令

后端回归测试使用 SQLite 测试库：

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests
```

前端生产构建：

```powershell
Set-Location frontend
npm run build
```

生产验收脚本集中在 `scripts/`，包括数据库迁移、后端启动、MySQL 备份、性能压测、安全回归和页面可达性检查。详细说明见 [部署与验收](docs/deployment.md)。

## 主要能力

系统已实现三类角色权限控制、JWT 登录注册、动态验证码/MFA、敏感资料加密与脱敏、房源媒体上传、智能搜索聚合和推荐、租赁流程闭环、操作日志、管理员引导、报表监控和后端回归测试。

剩余工作主要依赖真实部署环境：2 秒响应和 1000 并发压测记录、HTTPS 证书部署、防火墙/IDS/WAF 配置、漏洞扫描报告，以及 Chrome、Firefox、Edge、360 和移动端兼容性人工验收记录。

## 文档

- [API 设计](docs/api-design.md)
- [数据库设计](docs/database-design.md)
- [部署与验收](docs/deployment.md)
- [文档索引](docs/README.md)
