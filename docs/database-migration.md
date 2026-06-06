# 数据库迁移

本项目使用 MySQL 存储业务数据，使用 Flask-Migrate/Alembic 管理表结构。迁移脚本位于 `backend/migrations/versions/`，团队协作时应提交模型变更和对应迁移文件，不要依赖本机数据库状态。

## 基本原则

开发和生产环境都应该通过迁移同步 schema。`AUTO_CREATE_DB=true` 只适合临时开发环境，生产或团队协作环境应设置为 `AUTO_CREATE_DB=false`，避免 `db.create_all()` 绕过 Alembic。

`backend/.env` 是本机私有配置，不要提交到 Git。仓库只提交 `backend/.env.example`。

## 新成员初始化数据库

先准备依赖和环境文件：

```powershell
python -m venv .venv
.\.venv\Scripts\pip.exe install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
```

在本机 MySQL 创建数据库：

```powershell
mysql -u root -p -e "CREATE DATABASE rent_house CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

修改 `backend\.env`：

```env
FLASK_CONFIG=production
AUTO_CREATE_DB=false
DATABASE_URI=mysql+pymysql://root:你的密码@127.0.0.1:3306/rent_house
SECRET_KEY=替换为随机值
JWT_SECRET_KEY=替换为随机值
SENSITIVE_DATA_KEY=替换为随机值
ADMIN_USERNAME=admin
ADMIN_PASSWORD=替换为管理员初始密码
```

执行迁移和管理员初始化：

```powershell
Set-Location backend
$env:FLASK_CONFIG = "production"
$env:AUTO_CREATE_DB = "false"
..\.venv\Scripts\flask.exe --app run:app db upgrade
..\.venv\Scripts\flask.exe --app run:app seed-admin
```

确认当前迁移版本：

```powershell
..\.venv\Scripts\flask.exe --app run:app db current
```

当前迁移链包含：

| 版本 | 说明 |
| --- | --- |
| `20260509_0001` | 初始表结构和基础角色 |
| `20260521_0002` | 扩展用户身份证字段长度，用于加密值 |

## 拉取新代码后的迁移

每次 `git pull` 后，如果 `backend/migrations/versions/` 有新增文件，执行：

```powershell
Set-Location backend
$env:FLASK_CONFIG = "production"
$env:AUTO_CREATE_DB = "false"
..\.venv\Scripts\flask.exe --app run:app db upgrade
```

也可以在仓库根目录直接使用脚本：

```powershell
.\scripts\backend_migrate.ps1
```

如果本次变更涉及管理员初始化逻辑或基础角色，也重新执行：

```powershell
..\.venv\Scripts\flask.exe --app run:app seed-admin
```

`seed-admin` 可重复执行。默认不会重置已有管理员密码；只有设置 `ADMIN_RESET_PASSWORD=true` 时才会更新密码。

## 创建新的迁移

模型变更后在 `backend/` 下生成迁移：

```powershell
Set-Location backend
$env:FLASK_CONFIG = "production"
$env:AUTO_CREATE_DB = "false"
..\.venv\Scripts\flask.exe --app run:app db migrate -m "describe schema change"
```

生成后必须人工检查 `backend/migrations/versions/*.py`，重点确认：

1. 新表、字段、索引和外键符合模型预期。
2. 枚举状态、默认值和 nullable 设置正确。
3. 不会误删业务表或误改无关字段。
4. 必要时补充 `downgrade()`，至少保证本地可理解回滚影响。

检查后执行：

```powershell
..\.venv\Scripts\flask.exe --app run:app db upgrade
..\.venv\Scripts\python.exe -m pytest tests
```

提交时同时提交模型文件和迁移文件。不要只提交本机数据库变更。

## 演示数据

不要把真实本地数据库直接交给别人，尤其不要包含手机号、身份证、真实聊天、合同或支付记录。推荐写种子脚本生成假数据。

临时演示可以导出脱敏数据：

```powershell
mysqldump -u root -p --databases rent_house --no-tablespaces > rent_house_demo.sql
```

别人导入：

```powershell
mysql -u root -p < rent_house_demo.sql
```

如果只需要表结构，不需要数据：

```powershell
mysqldump -u root -p --no-data --databases rent_house --no-tablespaces > rent_house_schema.sql
```

## 常见问题

`Access denied`：检查 `DATABASE_URI` 的用户名、密码、主机、端口和数据库名。

`Unknown database`：先在 MySQL 创建 `rent_house`。

`Target database is not up to date`：先执行 `flask db upgrade`，再生成新迁移。

迁移后接口报字段不存在：确认后端连接的是同一个数据库，执行 `flask db current` 检查版本。

误把真实密码写进代码：立即修改数据库密码，并把真实配置移回 `backend/.env`。
