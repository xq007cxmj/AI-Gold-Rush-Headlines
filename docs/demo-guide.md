# 项目演示指南

> 用于录制「演示视频」或「在线 Demo」，可按脚本一步步展示。
> 演示前先按 `deployment.md` 启动后端与 Redis。

## 演示准备

1. 启动 MySQL、Redis。
2. 启动后端：`uvicorn toutiao_backend.main:app --host 0.0.0.0 --port 8000 --reload`。
3. 启动前端（若已联调）：`npm run dev`（Vite 默认 5173）。
4. 打开 Swagger：`http://127.0.0.1:8000/docs`。

## 演示流程（录制脚本）

### ① 新闻浏览（无需登录）
1. 调用 `GET /api/news/categories`，展示分类列表。
2. 调用 `GET /api/news/list?categoryId=1&page=1&pageSize=10`，展示分页列表与 `has_more`。
3. 调用 `GET /api/news/detail?id=10`，展示详情 + `views` 自增至 121 + `related_news`。

### ② 用户体系
4. `POST /api/user/register`（`{username, password}`），展示返回 `token` + `userInfo`。
5. `POST /api/user/login` 重新登录，拿到 token。
6. 携带 `Authorization: Bearer <token>` 调用 `GET /api/user/info`，展示鉴权通过。
7. 不带 token 再调一次，展示 401 —— 突出鉴权。

### ③ 收藏
8. `POST /api/favorite/add`（`{newsId:10}`）添加收藏。
9. `GET /api/favorite/check?newsId=10` 展示 `isFavorite:true`。
10. `GET /api/favorite/list` 展示收藏列表 + 分页。
11. `DELETE /api/favorite/remove?newsId=10` 取消，再 check 展示 `false`。

### ④ 浏览历史
12. `POST /api/history/add`、`GET /api/history/list`、`DELETE /api/history/remove/{id}`、`DELETE /api/history/clear`。

### ⑤ 性能亮点
13. 打开 Redis：`redis-cli`，`KEYS *` 展示缓存 key；同一接口二次调用命中缓存（附响应更快）。

## 演示文案要点（口播 / 字幕）

- 「这是一个类今日头条的资讯网站，后端用 FastAPI + SQLAlchemy 异步 + MySQL + Redis 实现。」
- 「四个核心模块：新闻、用户、收藏、历史。所有接口统一 `code/message/data` 响应。」
- 「权限通过 JWT Bearer Token 控制，密码用 bcrypt 加密。」
- 「高频接口走 Redis Cache-Aside 缓存，降低数据库压力。」

## 录制建议

- 用 Swagger 演示后端接口最直观；有前端界面则录页面。
- 中间切换「无 token 401 → 有 token 成功」能体现鉴权闭环，是加分镜头。
- 结尾展示 Redis `KEYS` 说明缓存真实生效。

## 在线 Demo 海报文案（可选）

```
头条资讯网站 · Vue3 + FastAPI
新闻浏览 / 用户系统 / 收藏 / 历史
JWT 鉴权 · bcrypt · Redis 缓存 · 异步 SQLAlchemy
🔗 演示地址：<你的链接>
```
