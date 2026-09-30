from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from toutiao_backend.routers import news, users

# 创建app实例
app = FastAPI()
# 允许跨域请求的来源
# origins = [
#     "http://localhost",  # 前端开发环境地址
#     "http://localhost:3000",  # 前端开发环境地址
# ]
# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许指定来源的请求
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],  # 允许所有请求方法
    allow_headers=["*"],  # 允许所有请求头
)


@app.get("/")
async def root():
    return {"message": "Hello world"}


# 挂载路由/注册路由
app.include_router(news.router)
app.include_router(users.router)


def main():
    import uvicorn

    uvicorn.run(
        "toutiao_backend.main:app", host="127.0.0.1", port=8000, reload=True
    )  # reload=True->代码修改后自动重启
