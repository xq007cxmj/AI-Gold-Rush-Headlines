# API 接口文档

> 基址：`http://127.0.0.1:8000`
> 需要登录的接口在请求头携带：`Authorization: Bearer <token>`

## 通用响应

所有接口返回统一结构：

```json
{
  "code": 200,
  "message": "成功提示",
  "data": {}
}
```

| 字段 | 说明 |
| --- | --- |
| code | 200 成功；非 200 为异常 |
| message | 提示信息 |
| data | 业务数据 |

---

## 一、新闻模块 `/api/news`

### 1.1 获取新闻分类

`GET /api/news/categories`

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| skip | int | 跳过条数，默认 0 |
| limit | int | 返回条数，默认 100 |

```json
{
  "code": 200,
  "message": "获取新闻分类成功",
  "data": [{ "id": 1, "name": "科技", "sort_order": 1 }]
}
```

### 1.2 获取新闻列表

`GET /api/news/list`

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| categoryId | int | 必填，分类 ID |
| page | int | 页码，默认 1 |
| pageSize | int | 每页条数，默认 10 |

```json
{
  "code": 200,
  "message": "获取新闻列表成功",
  "data": {
    "list": [
      {
        "id": 10,
        "title": "标题",
        "description": "描述",
        "image": "https://…",
        "author": "作者",
        "category_id": 1,
        "views": 120,
        "publish_time": "2025-01-01T12:00:00"
      }
    ],
    "total": 100,
    "has_more": true
  }
}
```

### 1.3 获取新闻详情

`GET /api/news/detail?id=10`

调用后浏览量 `views` 自动 +1，并返回相关推荐。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| id | int | 必填，新闻 ID |

```json
{
  "code": 200,
  "message": "获取新闻详细信息成功",
  "data": {
    "id": 10,
    "title": "标题",
    "content": "内容",
    "image": "https://…",
    "author": "作者",
    "publish_time": "2025-01-01T12:00:00",
    "category_id": 1,
    "views": 121,
    "related_news": []
  }
}
```

---

## 二、用户模块 `/api/user`

### 2.1 注册

`POST /api/user/register`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| username | string | 用户名，必填 |
| password | string | 密码，必填 |

```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "token": "eyJhbGciOi…",
    "userInfo": { "id": 1, "username": "alice", "nickname": null, "avatar": "…", "gender": null, "bio": null }
  }
}
```

### 2.2 登录

`POST /api/user/login`

请求体同上（`username`、`password`）。返回结构与注册一致。

### 2.3 获取当前用户信息 🔒

`GET /api/user/info`

```json
{
  "code": 200,
  "message": "获取用户信息成功",
  "data": { "id": 1, "username": "alice", "nickname": null, "avatar": "…", "gender": null, "bio": null }
}
```

### 2.4 修改用户信息 🔒

`PUT /api/user/update`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| nickname | string | 昵称 |
| avatar | string | 头像 URL |
| gender | string | 性别 |
| bio | string | 个人简介 |
| phone | string | 手机号 |

返回更新后的 `userInfo`。

### 2.5 修改密码 🔒

`PUT /api/user/password`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| oldPassword | string | 旧密码，必填 |
| newPassword | string | 新密码，必填，≥6 位 |

---

## 三、收藏模块 `/api/favorite`（全部需登录）

### 3.1 检查收藏状态 🔒

`GET /api/favorite/check?newsId=10`

```json
{ "code": 200, "message": "检查收藏状态成功", "data": { "isFavorite": true } }
```

### 3.2 添加收藏 🔒

`POST /api/favorite/add`，请求体：`{ "newsId": 10 }`

### 3.3 取消收藏 🔒

`DELETE /api/favorite/remove?newsId=10`

### 3.4 收藏列表 🔒

`GET /api/favorite/list?page=1&pageSize=10`

```json
{
  "code": 200,
  "message": "获取收藏列表成功",
  "data": {
    "list": [
      { "id": 10, "title": "标题", "categoryId": 1, "views": 10, "favoriteTime": "…", "favoriteId": 1 }
    ],
    "total": 20,
    "hasMore": false
  }
}
```

### 3.5 清空收藏 🔒

`DELETE /api/favorite/clear`

---

## 四、浏览历史模块 `/api/history`（全部需登录）

### 4.1 添加历史记录 🔒

`POST /api/history/add`，请求体：`{ "newsId": 10 }`

### 4.2 历史列表 🔒

`GET /api/history/list?page=1&pageSize=10`

```json
{
  "code": 200,
  "message": "获取浏览历史列表成功",
  "data": {
    "list": [
      { "id": 10, "title": "标题", "categoryId": 1, "viewTime": "…", "viewId": 1 }
    ],
    "total": 20,
    "hasMore": false
  }
}
```

### 4.3 删除单条历史 🔒

`DELETE /api/history/remove/{history_id}`

### 4.4 清空历史 🔒

`DELETE /api/history/clear`

> 🔒 表示需要携带 `Authorization: Bearer <token>`。
> 完整接口也可通过 Swagger 在线查看：`http://127.0.0.1:8000/docs`。
