from fastapi.encoders import jsonable_encoder  # 使格式正常转换
from fastapi.responses import JSONResponse


def success_response(message: str = "success", data=None):
    content = {"code": 200, "message": message, "data": data}
    # 目标：把任何的Fastapi、Pydantic、ORM对象都要正常响应->code、message、data
    return JSONResponse(content=jsonable_encoder(content))
