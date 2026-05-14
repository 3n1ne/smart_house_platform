# 智能房屋租赁系统

基于 Vue 3 + Flask + MySQL 的智能房屋租赁系统。

## 项目结构

- `backend/`：Flask 后端项目
- `frontend/`：Vue 3 前端项目
- `docs/`：需求分解、数据库设计与 API 说明

## 当前进度

1. 初始项目脚手架已完成。
2. 数据库设计和后端模型骨架已完成。
3. 核心 REST API 契约设计已完成。
4. 前端认证流程和房源浏览页面已对接后端 API。
5. 房东端房源管理页面已对接房源管理 API。
6. 预约流程已对接后端 API 和前端租客/房东仪表盘。
7. 合同创建、合同签署和支付流程已对接后端 API 和前端仪表盘。
8. 维修、投诉、报表和监控流程已对接后端 API 和角色仪表盘。
9. 房东端房源管理的真实媒体上传、预览和删除已对接。
10. 关键写操作的操作日志已对接，并通过管理员监控概览展示。
11. 管理员用户管理已对接角色/状态/关键词筛选和账号启用/禁用操作。
12. 新闻和公告管理已对接房东/管理员发布和公开公告浏览。
13. 后端测试基础设施已添加，包含基于 SQLite 的 pytest 覆盖，涵盖认证、房源发布/浏览和新闻生命周期 API。
14. Alembic 迁移基线已添加，包含核心 schema 和角色种子数据，以及端到端租赁流程 API 覆盖。

## 后端数据库迁移

从 `backend/` 目录运行数据库迁移：

```powershell
$env:FLASK_CONFIG = "production"
$env:AUTO_CREATE_DB = "false"
$env:DATABASE_URI = "mysql+pymysql://user:password@host:3306/rent_house"
..\.venv\Scripts\flask.exe --app run:app db upgrade
```

## 迭代计划

1. 设计数据库 schema。
2. 定义 REST API 契约。
3. 实现认证和房源管理模块。
4. 实现租赁流程、消息和维修模块。
5. 完善报表、监控和部署支持。
6. 扩展自动化测试并添加 Alembic 迁移脚本用于生产 schema 管理。
7. 添加部署配置、种子数据/管理员引导策略和更广泛的回归覆盖。
