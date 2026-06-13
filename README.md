# 智慧租房系统

基于 Vue 3、Flask 和 MySQL 的租房管理系统，包含房源发布、房源搜索、看房预约、合同、支付、站内消息、维修投诉、公告和后台管理。

## 项目结构

```text
backend/    Flask API、数据模型、Alembic 迁移和上传目录
frontend/   Vue 3 + Vite 前端应用
deploy/     Nginx 部署参考配置
scripts/    后端迁移、启动和 MySQL 备份脚本
```

## 环境要求

后端需要 Python 3.10+、MySQL 8.x 或兼容版本。前端需要 Node.js 18+ 和 npm。生产部署建议使用 Nginx 托管前端静态文件并反向代理后端 API。

## 后端配置

创建虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\pip.exe install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
```

在 MySQL 中创建数据库：

```powershell
mysql -u root -p -e "CREATE DATABASE rent_house CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

修改 `backend\.env`，至少确认这些配置：

```env
FLASK_CONFIG=production
AUTO_CREATE_DB=false
DATABASE_URI=mysql+pymysql://user:password@127.0.0.1:3306/rent_house
SECRET_KEY=replace-with-random-secret
JWT_SECRET_KEY=replace-with-random-secret
SENSITIVE_DATA_KEY=replace-with-random-secret
UPLOAD_FOLDER=D:\PythonProject\rent_house\backend\uploads
MFA_CODE_VISIBLE=false
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-admin-password
```

同步数据库表结构并初始化管理员：

```powershell
Set-Location backend
$env:FLASK_CONFIG = "production"
$env:AUTO_CREATE_DB = "false"
..\.venv\Scripts\flask.exe --app run:app db upgrade
..\.venv\Scripts\flask.exe --app run:app seed-admin
```

本地启动后端：

```powershell
Set-Location backend
..\.venv\Scripts\flask.exe --app run:app run
```

也可以在根目录使用脚本：

```powershell
.\scripts\backend_migrate.ps1
.\scripts\backend_start.ps1
```

## 前端配置

安装依赖并启动开发服务：

```powershell
Set-Location frontend
npm install
npm run dev
```

`frontend\.env.example` 默认同源访问：

```env
VITE_API_BASE_URL=/api
VITE_ASSET_BASE_URL=
```

前后端分离部署时，将 `VITE_API_BASE_URL` 改为后端 API 地址，例如 `https://example.com/api`；上传资源使用独立域名时配置 `VITE_ASSET_BASE_URL`。

## 部署

后端生产入口为 `backend\wsgi.py`，可交给 systemd、Supervisor、Gunicorn/uWSGI 或同类进程管理器托管。生产环境必须设置 `FLASK_CONFIG=production`、`AUTO_CREATE_DB=false`，并使用独立强随机值配置 `SECRET_KEY`、`JWT_SECRET_KEY` 和 `SENSITIVE_DATA_KEY`。

前端构建：

```powershell
Set-Location frontend
npm install
npm run build
```

将 `frontend\dist` 交给 Nginx 或静态资源服务托管。仓库提供 `deploy\nginx-rent-house.conf` 作为参考，上线前替换域名、证书路径、前端 `dist` 目录、上传目录和后端 upstream。单页应用需要配置 history fallback，并代理 `/api` 与 `/uploads`。

MySQL 备份示例：

```powershell
.\scripts\mysql_backup.ps1 -Database rent_house -User root -OutputPath .\backups\rent_house.sql
```

## 数据库迁移

迁移脚本位于 `backend\migrations\versions`。拉取新代码后，如果该目录有新增迁移文件，执行：

```powershell
.\scripts\backend_migrate.ps1
```

创建新迁移时在 `backend` 目录执行：

```powershell
$env:FLASK_CONFIG = "production"
$env:AUTO_CREATE_DB = "false"
..\.venv\Scripts\flask.exe --app run:app db migrate -m "describe schema change"
..\.venv\Scripts\flask.exe --app run:app db upgrade
```

生成迁移后需要人工检查迁移文件，确认不会误删业务表或修改无关字段。提交模型变更时必须同时提交对应迁移文件。

## 上线检查

1. 生产密钥、数据库密码和 `.env` 未提交到 Git。
2. 目标环境已完成数据库备份，并成功执行 `flask db upgrade`。
3. 管理员账号已初始化，上线后立即修改初始密码。
4. 后端使用 `backend\wsgi.py` 启动，上传目录已持久化并设置正确权限。
5. 前端 `npm run build` 通过，Nginx 正确代理 `/api` 和 `/uploads`。
6. HTTPS、数据库端口访问控制、日志保存、备份和日志轮转已配置。
7. 生产环境保持 `MFA_CODE_VISIBLE=false`，真实验证码和支付能力按实际部署接入或明确作为演示功能。

## 常用验证

```powershell
.\.venv\Scripts\python.exe -m py_compile backend\run.py backend\wsgi.py backend\app\config.py

Set-Location frontend
npm run build
```
