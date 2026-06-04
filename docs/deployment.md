# 部署与验收

本文档合并生产部署、运维脚本、安全、性能和兼容性验收说明。生产环境不应依赖 `db.create_all()` 自动建表，应使用 Alembic 管理 schema。

## 环境变量

复制 `backend/.env.example` 为 `backend/.env`，按环境修改数据库、密钥、上传目录和管理员账号。生产环境至少确认：

| 变量 | 要求 |
| --- | --- |
| `FLASK_CONFIG` | 使用 `production` |
| `AUTO_CREATE_DB` | 保持 `false` |
| `DATABASE_URI` | 指向生产 MySQL |
| `SECRET_KEY` / `JWT_SECRET_KEY` | 使用独立强随机值 |
| `SENSITIVE_DATA_KEY` | 独立于其他密钥，建议托管到 KMS 或服务器密钥管理 |
| `UPLOAD_FOLDER` | 指向持久化上传目录 |
| `MFA_CODE_VISIBLE` | 生产保持 `false` |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | 首次初始化管理员使用 |

前端复制 `frontend/.env.example` 并按部署方式设置：

| 变量 | 说明 |
| --- | --- |
| `VITE_API_BASE_URL` | API 基础地址，同源部署默认 `/api` |
| `VITE_ASSET_BASE_URL` | 上传资源基础地址，同源部署可留空 |

## 后端部署

在 `backend/` 目录执行迁移和管理员初始化：

```powershell
$env:FLASK_CONFIG = "production"
$env:AUTO_CREATE_DB = "false"
..\.venv\Scripts\flask.exe --app run:app db upgrade
..\.venv\Scripts\flask.exe --app run:app seed-admin
```

`seed-admin` 可重复执行。已有管理员只会更新邮箱、手机、真实姓名和启用状态；只有 `ADMIN_RESET_PASSWORD=true` 时才会重置密码。

生产服务使用 `backend/wsgi.py` 作为 WSGI 入口，由进程管理器托管，并通过 Nginx 或同类反向代理转发 `/api` 和 `/uploads`。仓库提供 `deploy/nginx-rent-house.conf`，上线前替换域名、证书路径、前端 `dist` 目录、上传目录和后端 upstream。

## 前端部署

```powershell
Set-Location frontend
npm install
npm run build
```

将 `frontend/dist` 交给 Nginx 或静态资源服务托管。单页应用需要配置 history fallback，参考 `deploy/nginx-rent-house.conf`。

## 运维脚本

| 脚本 | 用途 |
| --- | --- |
| `scripts/backend_migrate.ps1` | 执行 Alembic 迁移 |
| `scripts/backend_start.ps1` | 通过 `backend/wsgi.py` 启动后端 |
| `scripts/mysql_backup.ps1` | 使用 `mysqldump` 导出 MySQL 备份 |
| `scripts/performance_acceptance.ps1` | 对公开核心接口执行性能验收 |
| `scripts/security_acceptance.ps1` | 执行安全相关语法检查、回归测试和可选依赖审计 |
| `scripts/compatibility_acceptance.ps1` | 对前端关键页面执行 HTTP 可达性检查 |

备份示例：

```powershell
.\scripts\mysql_backup.ps1 -Database rent_house -User root -OutputPath .\backups\rent_house.sql
```

业务写操作进入 `operation_logs` 表。生产环境还应保留 WSGI、反向代理和数据库日志，并配置日志轮转。

## 安全验收

系统已实现 JWT、角色权限控制、管理员引导、操作日志、动态验证码登录、上传文件类型限制、身份证号加密存储和接口脱敏展示。生产上线前还需要完成这些外部配置：

| 项目 | 要求 |
| --- | --- |
| HTTPS | 使用真实证书，启用 TLS 1.2/1.3 |
| 验证码 | 接入短信、邮件或内部消息通道 |
| 密钥 | 不提交仓库，优先使用 KMS 或服务器密钥管理 |
| 网络 | 只开放必要端口，数据库端口仅允许后端访问 |
| 上传目录 | 禁止脚本执行 |
| 安全扫描 | 保存依赖、主机和 Web 漏洞扫描报告 |

本地安全回归：

```powershell
.\scripts\security_acceptance.ps1 -SkipNpmAudit
```

网络允许时去掉 `-SkipNpmAudit`，执行前端依赖审计。

## 性能验收

需求目标是常规用户请求 2 秒内响应，并支持高峰期 1000 并发。仓库提供压测入口，但最终结论必须来自生产等价环境。

轻量验证：

```powershell
.\.venv\Scripts\python.exe backend\scripts\performance_smoke.py --url http://127.0.0.1:5000/api/houses --requests 100 --concurrency 10
```

生产等价验收：

```powershell
.\scripts\performance_acceptance.ps1 -BaseUrl https://rent-house.example.com -Requests 1000 -Concurrency 1000
```

核心接口 P95 应小于或等于 2 秒，失败数应为 0。记录结果时同时保存应用进程数、数据库配置、反向代理配置、CPU、内存、磁盘 IO、数据库连接池和错误日志。

## 兼容性验收

前端服务启动后可先执行页面可达性冒烟：

```powershell
.\scripts\compatibility_acceptance.ps1 -BaseUrl http://127.0.0.1:5173
```

该脚本不能替代真实浏览器验收。发布前应人工验证 Chrome、Firefox、Edge、360 浏览器，以及 375px、390px、414px、768px 等移动端宽度。重点检查登录注册、房源筛选、详情页、预约、合同、支付、消息、维修投诉和管理员报表，记录浏览器版本、设备宽度、问题和修复结果。

## 当前剩余项

应用代码层面的身份验证、授权、资料加密、业务闭环、日志、测试和基础文档已完成。生产验收仍需补齐 2 秒响应和 1000 并发实测、HTTPS、防火墙/IDS/WAF、漏洞扫描报告、真实验证码通道、真实支付通道和跨浏览器兼容性记录。
