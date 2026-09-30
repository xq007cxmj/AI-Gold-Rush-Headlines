# main.py
"""
FastAPI + GitHub OAuth 登录示例
依赖: pip install fastapi "uvicorn[standard]" httpx itsdangerous python-dotenv
"""

import os
import secrets
from urllib.parse import urlencode

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

# starlette.middleware.sessions 模块里导入了 itsdangerous
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- 配置 ----------
GITHUB_CLIENT_ID = os.environ["GITHUB_CLIENT_ID"]
GITHUB_CLIENT_SECRET = os.environ["GITHUB_CLIENT_SECRET"]
GITHUB_REDIRECT_URI = os.getenv(
    "GITHUB_REDIRECT_URI", "http://localhost:8000/auth/github/callback"
)
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API = "https://api.github.com"

# ---------- 应用 ----------
# 关键：关闭自带文档
app = FastAPI(
    docs_url=None,  # 关闭 /docs
    redoc_url=None,  # 关闭 /redoc
    openapi_url=None,  # 关闭 /openapi.json（否则 schema 依然会暴露）
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,  # 用于对 session cookie 做签名
    session_cookie="sid",
    max_age=14 * 24 * 3600,  # 14 天
    same_site="lax",  # 防 CSRF 的第一道防线
    https_only=False,  # 生产环境务必改 True（需要 HTTPS）
)


# ---------- 工具函数 ----------
def _safe_next(next_url: str | None) -> str:
    """防止开放重定向：只允许站内相对路径"""
    if not next_url or not next_url.startswith("/") or next_url.startswith("//"):
        return "/"
    return next_url


def current_user(request: Request) -> dict:
    """依赖注入：获取当前登录用户，未登录抛 401"""
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    return user


# ---------- 页面 ----------
@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(os.path.join(BASE_DIR, "static3", "index.html"))


# ---------- ① 发起登录：跳转到 GitHub ----------
@app.get("/auth/github/login", include_in_schema=False)
async def github_login(request: Request, next: str = "/"):
    # 生成随机 state，存进 session，用于回调时校验（防 CSRF）
    state = secrets.token_urlsafe(32)

    # 服务器生成一个唯一的 SessionID，并保存在服务器内存,
    # 服务器通过响应头里的 Set-Cookie 字段，把这个 SessionID 发给浏览器。
    request.session["oauth_state"] = state
    request.session["oauth_next"] = _safe_next(next)

    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "scope": "read:user user:email",  # 最小权限原则
        "state": state,
        "allow_signup": "true",
    }
    return RedirectResponse(
        f"{GITHUB_AUTHORIZE_URL}?{urlencode(params)}", status_code=302
    )


# ---------- ② 回调：用 code 换 token，再换用户信息 ----------
@app.get("/auth/github/callback", include_in_schema=False)
async def github_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
):
    # 用户点了"取消授权"
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"GitHub 授权失败: {error} {error_description or ''}",
        )

    if not code or not state:
        raise HTTPException(status_code=400, detail="缺少 code 或 state 参数")

    # --- 校验 state（一次性使用，用完即删）---
    expected_state = request.session.pop("oauth_state", None)
    if not expected_state or not secrets.compare_digest(
        expected_state.encode(), state.encode()
    ):
        raise HTTPException(status_code=400, detail="state 校验失败，疑似 CSRF")

    async with httpx.AsyncClient(timeout=10.0) as client:
        # --- 用 code 换 access_token（这一步必须在后端做，因为要带 client_secret）---
        token_resp = await client.post(
            GITHUB_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_REDIRECT_URI,
            },
        )
        token_resp.raise_for_status()
        token_data = token_resp.json()

        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=400,
                detail=f"获取 access_token 失败: {token_data.get('error_description') or token_data}",
            )

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        # --- 拉取用户资料 ---
        user_resp = await client.get(f"{GITHUB_API}/user", headers=headers)
        user_resp.raise_for_status()
        gh_user = user_resp.json()

        # --- 邮箱可能没公开，单独查一次 ---
        email = gh_user.get("email")
        if not email:
            email_resp = await client.get(f"{GITHUB_API}/user/emails", headers=headers)
            if email_resp.status_code == 200:
                for item in email_resp.json():
                    if item.get("primary") and item.get("verified"):
                        email = item["email"]
                        break

    # --- 写入 session（只存必要信息，绝不放 access_token）---
    request.session["user"] = {
        "id": gh_user["id"],
        "login": gh_user["login"],
        "name": gh_user.get("name"),
        "avatar_url": gh_user.get("avatar_url"),
        "email": email,
        "html_url": gh_user.get("html_url"),
    }

    next_url = _safe_next(request.session.pop("oauth_next", "/"))
    return RedirectResponse(next_url, status_code=302)


# ---------- ③ 退出登录 ----------
@app.post("/auth/logout", include_in_schema=False)
@app.get("/auth/logout", include_in_schema=False)
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)


# ---------- ④ 给前端用的 API ----------
@app.get("/api/me")
async def api_me(request: Request):
    user = request.session.get("user")
    if not user:
        return JSONResponse({"authenticated": False, "user": None})
    return JSONResponse({"authenticated": True, "user": user})


@app.get("/api/profile")
async def api_profile(request: Request):
    """
    受保护接口示例。
    未登录会返回 401，前端据此引导去登录。
    """
    u = current_user(request)
    return {
        "message": f"你好 {u['login']}，这是需要登录才能看到的数据",
        "user": u,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app3:app", host="127.0.0.1", port=8000, reload=True)
