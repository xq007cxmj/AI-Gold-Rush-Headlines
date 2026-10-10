# 部署说明

## 1. 环境要求

- Python 3.8+
- MySQL 8.x（utf8mb4）
- Redis
- Node.js 16+（前端，可选）

## 2. 后端启动

### 2.1 安装依赖

```bash
pip install fastapi uvicorn[standard] sqlalchemy aiomysql redis passlib[bcrypt] pydantic httpx
```

### 2.2 配置数据库

编辑 `toutiao_backend/config/db_conf.py`：

```python
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb4"
```

> 按本机修改账号、密码、库名。Redis 在 `config/cache_conf.py`（默认 `localhost:6379`）。

### 2.3 初始化数据库表

按 `models/` 下 ORM 模型创建表：

- `news_category`、`news`、`user`、`user_token`、`favorite`、`history`

示例（MySQL）：

```sql
-- 新闻分类
CREATE TABLE news_category (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE,
  sort_order INT NOT NULL DEFAULT 0,
  created_at DATETIME,
  updated_at DATETIME
);

-- 新闻
CREATE TABLE news (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  description VARCHAR(500),
  content VARCHAR(1000) NOT NULL,
  image VARCHAR(255),
  author VARCHAR(50),
  category_id INT NOT NULL,
  views INT NOT NULL DEFAULT 0,
  publish_time DATETIME,
  created_at DATETIME,
  updated_at DATETIME,
  INDEX idx_category_id (category_id),
  INDEX idx_publish_time (publish_time)
);
```

### 2.4 插入分类示例数据

```sql
INSERT INTO news_category (name, sort_order) VALUES ('科技', 1), ('体育', 2), ('娱乐', 3);
```

### 2.5 启动服务

```bash
uvicorn toutiao_backend.main:app --host 0.0.0.0 --port 8000 --reload
```

生产环境去掉 `--reload`，可增加 worker：

```bash
uvicorn toutiao_backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2.6 接口文档

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## 3. 前端部署（可选）

```bash
cd 前端目录
npm install
npm run build        # 产物在 dist/
```

使用 Nginx 托管 `dist/`，并代理 `/api` 到后端：

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## 4. 常见问题

| 问题 | 处理 |
| --- | --- |
| 连接数据库失败 | 检查 MySQL 是否启动、账号密码、`news_app` 库是否创建 |
| Redis 连接失败 | 检查 Redis 是否启动（`redis-server`）、端口 |
| 接口 401 | 未携带或 token 过期，先登录获取 token |
| 跨域报错 | 前端地址需在 `main.py` 的 `origins` 白名单中 |
