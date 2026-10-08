from config.db_conf import get_db
from crud import users
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

bearer_scheme = HTTPBearer(auto_error=False)


# 整合 根据 Token 查询用户，返回用户
async def get_current_user(
    # authorization: str = Header(..., alias="Authorization"),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    # Bearer xxxxx
    # token = authorization.split(" ")[1]
    # token = authorization.replace("Bearer ", "")

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="不符合格式的令牌",
        )
    token = credentials.credentials

    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌或已经过期的令牌",
        )

    return user
