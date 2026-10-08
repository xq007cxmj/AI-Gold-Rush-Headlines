from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="change-me-to-a-long-random-secret-key",
)


@app.get("/")
def index(request: Request):
    count = request.session.get("count", 0)
    count += 1
    request.session["count"] = count
    return {"count": count}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app4:app", host="0.0.0.0", port=8001, reload=True)
