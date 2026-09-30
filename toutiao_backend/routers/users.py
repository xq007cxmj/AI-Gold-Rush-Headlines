from crud import users
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.users import UserAuthResponse, UserInfoResponse, UserRequest
from sqlalchemy.ext.asyncio import AsyncSession
from utils.response import success_reponse

from toutiao_backend.config.db_conf import get_db

# 创建APIRouter实例
router = APIRouter(
    prefix="/api/user", tags=["users"]
)  # prefix->添加路由前缀“/api/user”；tags->分组，组名为“users”


# 写装饰器和路由处理函数
@router.post("/register")
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 注册逻辑：验证用户是否存在->创建用户->生成Token->响应结果
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在"
        )
    user = await users.create_user(db, user_data)

    token = await users.create_token(db, user.id)
    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar,
    #         },
    #     },
    # }
    print(user)
    response_data = UserAuthResponse(
        token=token, userInfo=UserInfoResponse.model_validate(user)
    )
    print(UserInfoResponse.model_validate(user))
    return success_reponse(message="注册成功", data=response_data)
