# 智慧租房系统

基于 Vue 3、Flask 和 MySQL 的租房管理系统，覆盖房源发布、房源搜索、看房预约、合同、支付、消息、维修投诉、公告和后台管理。

## 项目结构

```text
backend/        Flask API、数据模型、Alembic 迁移和后端测试
frontend/       Vue 3 + Vite 前端应用
deploy/         Nginx 等部署参考配置
scripts/        迁移、启动、备份和验收脚本
docs/           核心技术文档
requirement.md  原始需求说明
```

## 后端启动

先安装依赖并创建本地环境文件：

```powershell
python -m venv .venv
.\.venv\Scripts\pip.exe install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
```

修改 `backend\.env` 中的 `DATABASE_URI`，指向你自己的 MySQL 数据库。首次初始化或拉取新迁移后执行：

```powershell
Set-Location backend
$env:FLASK_CONFIG = "production"
$env:AUTO_CREATE_DB = "false"
..\.venv\Scripts\flask.exe --app run:app db upgrade
..\.venv\Scripts\flask.exe --app run:app seed-admin
```

启动后端：

```powershell
Set-Location backend
..\.venv\Scripts\flask.exe --app run:app run
```

完整数据库迁移流程见 [数据库迁移](docs/database-migration.md)。

## 前端启动

```powershell
Set-Location frontend
npm install
npm run dev
```

前端环境变量参考 `frontend\.env.example`。默认同源访问 `/api` 和 `/uploads`；前后端分离部署时调整 `VITE_API_BASE_URL` 和 `VITE_ASSET_BASE_URL`。

## 常用验证

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests

Set-Location frontend
npm run build
```

## 文档

- [数据库迁移](docs/database-migration.md)
- [数据库设计](docs/database-design.md)
- [API 设计](docs/api-design.md)
- [部署说明](docs/deployment.md)
- [文档索引](docs/README.md)
