# Casino API (Django + DRF + MySQL)

基于 Django、Django REST framework 的后端 API，提供注册登录（JWT）、用户资料/余额、充值提现、投注记录与统计等接口。

## 技术栈
- Django 5
- Django REST framework (DRF)
- djangorestframework-simplejwt（JWT 认证）
- django-cors-headers（跨域）
- MySQL + mysqlclient（Windows 已验证 2.2.7）

## 环境要求
- Python 3.10+（建议 3.11/3.12）
- MySQL 8+（本项目默认数据库名 `casino_db`）
- 可选：PowerShell 或 Bash 终端

## 快速开始
在 `casinoAPI/` 目录执行：

```bash
# 1) 创建并激活虚拟环境（Windows PowerShell）
python -m venv venv
./venv/Scripts/activate

# 2) 安装依赖
python -m pip install --upgrade pip
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers mysqlclient

# 3) 准备 MySQL（确保 root 密码为 123456，或修改 settings.py）
#    如需创建数据库（在系统 MySQL CLI 中执行）：
#    CREATE DATABASE IF NOT EXISTS casino_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 4) 迁移数据库
python manage.py makemigrations
python manage.py migrate

# 5) 创建超级用户
python manage.py createsuperuser

# 6) 启动开发服务
python manage.py runserver 0.0.0.0:8000
```

访问：
- 管理后台：`http://localhost:8000/admin/`
- API 根：`http://localhost:8000/api/`

## 项目结构
- `backend/settings.py`：已配置 MySQL（`root/123456`、`casino_db`）、CORS、DRF、JWT、时区与中文
- `accounts/`：用户模型、交易记录、认证/资料/充值提现接口
- `bets/`：投注记录与统计接口

## API 概览（主要端点）
基础前缀：`http://localhost:8000/api`

- 认证（JWT）`/accounts/`
  - POST `/register/` 注册
    - body: `{ "username": "u", "email": "e@x.com", "password": "p", "password2": "p" }`
  - POST `/login/` 获取 JWT：`{ access, refresh }`
    - body: `{ "username": "u", "password": "p" }`
  - POST `/token/refresh/` 刷新 access：`{ refresh }`

- 用户 `/accounts/`
  - GET `/profile/` 获取资料（需授权）
  - PUT `/profile/` 更新资料（可改邮箱等，需授权）
  - GET `/balance/` 获取余额（需授权）

- 交易 `/accounts/`
  - GET `/transactions/` 获取交易记录（需授权）
  - POST `/deposit/` 充值（需授权）
    - body: `{ "amount": 100 }`
  - POST `/withdraw/` 提现（需授权）
    - body: `{ "amount": 50 }`

- 投注 `/bets/`
  - GET `/records/` 获取投注记录（需授权）
  - POST `/create/` 创建投注记录（需授权）
    - body: `{ "game": "Blackjack", "bet_amount": 10, "profit": -10, "game_details": { ... } }`
  - GET `/statistics/` 投注统计（总盈亏/金额 & 按游戏汇总）（需授权）

说明：所有需授权的接口，请在请求头添加 `Authorization: Bearer <access-token>`。

## 数据模型（简要）
- `accounts.User`：继承 `AbstractUser`，新增 `balance: Decimal`
- `accounts.Transaction`：`user, amount, transaction_type(deposit/withdraw/...), status, created_at`
- `bets.BetRecord`：`user, game(枚举), bet_amount, profit, bet_time, game_details(JSON)`

## CORS
开发环境已开启：`CORS_ALLOW_ALL_ORIGINS = True`。生产环境请按域名白名单配置。

## 常见问题
- mysqlclient 报错或版本不符
  - 使用 `mysqlclient>=2.2.7`（Windows 有预编译轮子）。
  - 若仍报编译工具错误，请安装 Microsoft C++ Build Tools 或改用 WSL/容器。
- 无法连接 MySQL / 认证失败
  - 确认 MySQL 已启动、用户/密码正确（默认 `root/123456`），且数据库 `casino_db` 已存在。
  - 如需修改，请在 `backend/settings.py` 的 `DATABASES` 中更新。
- 401 未授权
  - 确保前端携带 `Authorization: Bearer <access>`，并在过期后使用 `/token/refresh/` 刷新。

## 生产部署要点
- 将 `DEBUG=False`，配置 `ALLOWED_HOSTS`
- 配置数据库/Redis（如需）与静态文件 `STATIC_ROOT`，执行 `collectstatic`
- 仅允许特定 CORS 源
- 使用 gunicorn/uwsgi + nginx 或容器化 