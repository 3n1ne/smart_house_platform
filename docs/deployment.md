# 部署说明

本文只保留上线必须关注的配置、步骤和检查项。数据库迁移的完整流程见 [数据库迁移](database-migration.md)。

## 环境变量

后端复制 `backend/.env.example` 为 `backend/.env`，生产环境至少确认：

| 变量 | 要求 |
| --- | --- |
| `FLASK_CONFIG` | `production` |
| `AUTO_CREATE_DB` | `false` |
| `DATABASE_URI` | 指向生产 MySQL，不使用个人本机地址 |
| `SECRET_KEY` / `JWT_SECRET_KEY` | 独立强随机值 |
| `SENSITIVE_DATA_KEY` | 独立强随机值，优先托管到服务器密钥管理 |
| `UPLOAD_FOLDER` | 持久化上传目录 |
| `MFA_CODE_VISIBLE` | 生产保持 `false` |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | 首次初始化管理员使用 |

前端复制 `frontend/.env.example`，按部署方式配置：

| 变量 | 说明 |
| --- | --- |
| `VITE_API_BASE_URL` | API 基础地址，同源部署默认 `/api` |
| `VITE_ASSET_BASE_URL` | 上传资源基础地址，同源部署可留空 |

## 后端

```powershell
Set-Location backend
$env:FLASK_CONFIG = "production"
$env:AUTO_CREATE_DB = "false"
..\.venv\Scripts\flask.exe --app run:app db upgrade
..\.venv\Scripts\flask.exe --app run:app seed-admin
```

生产服务使用 `backend/wsgi.py` 作为 WSGI 入口，由 systemd、Supervisor、Gunicorn/uWSGI 或等价进程管理器托管。

## 前端

```powershell
Set-Location frontend
npm install
npm run build
```

将 `frontend/dist` 交给 Nginx 或静态资源服务托管。单页应用需要 history fallback。仓库提供 `deploy/nginx-rent-house.conf` 作为参考，上线前替换域名、证书路径、前端 `dist` 目录、上传目录和后端 upstream。

## 运维脚本

| 脚本 | 用途 |
| --- | --- |
| `scripts/backend_migrate.ps1` | 执行 Alembic 迁移 |
| `scripts/backend_start.ps1` | 通过 `backend/wsgi.py` 启动后端 |
| `scripts/mysql_backup.ps1` | 使用 `mysqldump` 导出 MySQL 备份 |
| `scripts/security_acceptance.ps1` | 安全回归和依赖审计 |
| `scripts/performance_acceptance.ps1` | 性能验收 |
| `scripts/compatibility_acceptance.ps1` | 前端页面可达性检查 |

备份示例：

```powershell
.\scripts\mysql_backup.ps1 -Database rent_house -User root -OutputPath .\backups\rent_house.sql
```

## 上线检查

1. 生产密钥和数据库密码未提交到 Git。
2. 数据库已备份，且 `flask db upgrade` 已在目标环境执行成功。
3. 管理员账号已初始化，上线后立即修改初始密码。
4. 后端回归测试通过：`python -m pytest backend/tests`。
5. 前端构建通过：`npm run build`。
6. Nginx 正确代理 `/api` 和 `/uploads`，前端 history fallback 生效。
7. HTTPS、上传目录权限、数据库端口访问控制已配置。
8. 生产环境关闭验证码明文返回，真实验证码和支付能力按实际部署接入或明确作为演示功能。
9. 保留后端、反向代理、数据库日志，并配置备份和日志轮转。
10. 在生产等价环境记录性能和浏览器兼容性验收结果。
