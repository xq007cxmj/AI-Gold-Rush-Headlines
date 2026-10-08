from crud import users
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.users import (
    UserAuthResponse,
    UserChangePasswordRequest,
    UserInfoResponse,
    UserRequest,
    UserUpdateRequest,
)
from sqlalchemy.ext.asyncio import AsyncSession
from utils.response import success_response

from toutiao_backend.config.db_conf import get_db
from toutiao_backend.models.users import User
from toutiao_backend.utils.auth import get_current_user

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
    return success_response(message="注册成功", data=response_data)


# 用户登录
@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 登录逻辑：验证用户是否存在 -> 验证密码 -> 生成 Token -> 响应结果
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )

    token = await users.create_token(db, user.id)

    response_data = UserAuthResponse(
        token=token, userInfo=UserInfoResponse.model_validate(user)
    )

    return success_response(data=response_data)


# 查 Token 查用户 -> 封装 crud -> 功能整合成一个工具函数 -> 路由导入使用：依赖注入
@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response(
        message="获取用户信息成功", data=UserInfoResponse.model_validate(user)
    )


# 修改用户信息：验证Token -> 更新（用户输入数据 put提交 -> 请求体参数 -> 定义Pydantic模型类） -> 响应结果
# 参数：用户输入的 + 验证Token的 + db（调用更新的方法）
@router.put("/update")
async def update_user_info(
    user_data: UserUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await users.update_user(db, user.username, user_data)
    return success_response(
        message="更新用户信息成功", data=UserInfoResponse.model_validate(user)
    )


@router.put("/password")
async def update_password(
    password_data: UserChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res_change_pwd = await users.change_password(
        db, user, password_data.old_password, password_data.new_password
    )

    if not res_change_pwd:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败，请检查旧密码",
        )

    return success_response(message="修改密码成功")
