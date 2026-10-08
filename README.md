# 头条资讯网站后端服务

一个类「今日头条」的资讯类网站后端接口服务，基于 **FastAPI + SQLAlchemy 2.0（异步）** 构建，为前端提供新闻资讯、用户体系、收藏、浏览历史等 RESTful API。

## 功能特性

- **新闻模块**：新闻分类、按分类分页拉取新闻列表、新闻详情（浏览量自增）、相关新闻推荐
- **用户模块**：注册、登录、个人信息查询与修改、修改密码
- **收藏模块**：收藏状态校验、添加 / 取消收藏、收藏列表（分页）、清空收藏
- **浏览历史模块**：记录浏览、历史列表（分页）、单条删除、清空历史
- **缓存优化**：新闻分类与列表采用 Redis 缓存（Cache-Aside 模式），降低数据库压力

## 技术栈

| 分类 | 技术 |
| --- | --- |
| 后端框架 | Python 3.11 / FastAPI / Uvicorn |
| ORM | SQLAlchemy 2.0（Async）+ aiomysql |
| 数据存储 | MySQL 8（utf8mb4）、Redis（redis.asyncio） |
| 数据校验 | Pydantic v2 |
| 安全 | bcrypt 密码哈希、JWT / Bearer Token 鉴权 |
| 其他 | python-dotenv、httpx |

## 目录结构

```
toutiao_backend/
├── main.py                 # FastAPI 入口，注册路由 / CORS / 异常处理
├── routers/                # 路由层（news / users / favorite / history）
├── crud/                   # 数据操作层（封装数据库查询）
├── models/                 # SQLAlchemy ORM 模型
├── schemas/                # Pydantic 校验与响应模型
├── cache/                  # Redis 缓存逻辑
├── config/                 # 数据库 / Redis 配置
└── utils/                  # 鉴权、密码加密、统一响应、异常处理
```

### 分层说明

项目采用 **routers（路由）→ crud（数据操作）→ models（ORM 模型）→ schemas（校验模型）** 的分层设计，职责清晰、便于扩展：

- `routers/`：定义接口路由，统一路径前缀与响应格式
- `crud/`：封装操作数据库的方法，供路由层调用
- `models/`：定义数据库表结构（ORM 映射）
- `schemas/`：定义请求 / 响应的数据校验模型
- `utils/`：通用工具（`get_current_user` 鉴权、`security` 密码加密、`response` 统一响应）

## 快速开始

### 环境要求

- Python 3.8+
- MySQL 8.x
- Redis

### 1. 安装依赖

```bash
pip install fastapi uvicorn[standard] sqlalchemy aiomysql redis passlib[bcrypt] pydantic httpx
```

### 2. 配置数据库与 Redis

数据库连接在 `toutiao_backend/config/db_conf.py` 中配置（默认使用 `news_app` 库）：

```python
# toutiao_backend/config/db_conf.py
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb4"
```

Redis 连接在 `toutiao_backend/config/cache_conf.py` 中配置：

```python
# toutiao_backend/config/cache_conf.py
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
```

> 请根据本机环境修改数据库账号、密码与库名，并确保 MySQL、Redis 已启动。

### 3. 初始化数据库表

本项目未内置建表脚本，可按 `models/` 下的 ORM 模型在 MySQL 中创建对应表：
`news_category`、`news`、`user`、`user_token`、`favorite`、`history`。

### 4. 启动服务

```bash
# 启动主后端服务（默认 127.0.0.1:8000）
uvicorn toutiao_backend.main:app --host 127.0.0.1 --port 8000 --reload
```

启动后访问接口文档：

- Swagger UI：<http://127.0.0.1:8000/docs>
- ReDoc：<http://127.0.0.1:8000/redoc>

## API 接口一览

| 模块 | 方法 & 路径 | 说明 |
| --- | --- | --- |
| 新闻 | `GET /api/news/categories` | 获取新闻分类 |
| 新闻 | `GET /api/news/list` | 按分类分页获取新闻列表 |
| 新闻 | `GET /api/news/detail?id=` | 获取新闻详情（浏览量 +1） |
| 用户 | `POST /api/user/register` | 用户注册 |
| 用户 | `POST /api/user/login` | 用户登录 |
| 用户 | `GET /api/user/info` | 获取当前用户信息 |
| 用户 | `PUT /api/user/update` | 修改用户信息 |
| 用户 | `PUT /api/user/password` | 修改密码 |
| 收藏 | `GET /api/favorite/check` | 检查收藏状态 |
| 收藏 | `POST /api/favorite/add` | 添加收藏 |
| 收藏 | `DELETE /api/favorite/remove` | 取消收藏 |
| 收藏 | `GET /api/favorite/list` | 收藏列表（分页） |
| 收藏 | `DELETE /api/favorite/clear` | 清空收藏 |
| 历史 | `POST /api/history/add` | 添加浏览记录 |
| 历史 | `GET /api/history/list` | 历史列表（分页） |
| 历史 | `DELETE /api/history/remove/{id}` | 删除单条历史 |
| 历史 | `DELETE /api/history/clear` | 清空历史 |

> 用户 / 收藏 / 历史等需要登录的接口，需在请求头中携带 `Authorization: Bearer <token>`。

## 技术要点

- **鉴权**：通过 `HTTPBearer` 依赖注入统一解析 `Authorization` 头，据此查询 `user_token` 表得到当前用户，实现接口权限控制。
- **密码安全**：使用 bcrypt 对密码进行哈希加密存储，验证时通过 `verify_password` 比对。
- **数据约束**：收藏表通过 `UniqueConstraint(user_id, news_id)` 保证同一用户对同一新闻只能收藏一次。
- **缓存策略**：分类与新闻列表采用 Cache-Aside 模式，先读 Redis，未命中再查库并回写。
- **索引优化**：对 `category_id`、`publish_time` 等高频查询字段建立索引，提升查询性能。
