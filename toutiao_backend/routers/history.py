from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from toutiao_backend.config.db_conf import get_db
from toutiao_backend.crud import history
from toutiao_backend.models.users import User
from toutiao_backend.schemas.history import HistoryAddRequest, HistoryListResponse
from toutiao_backend.utils.auth import get_current_user
from toutiao_backend.utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])


# 添加历史记录
@router.post("/add")
async def add_history(
    data: HistoryAddRequest,  # 请求参数
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    添加历史记录
    """
    result = await history.add_history(db, user.id, data.news_id)
    return success_response(message="添加成功", data=result)


# 获取浏览历史列表
@router.get("/list")
async def get_history_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows, total = await history.get_history_list(db, user.id, page, page_size)
    history_list = [
        {**news.__dict__, "view_time": view_time, "view_id": view_id}
        for news, view_time, view_id in rows
    ]
    has_more = total > page * page_size

    data = HistoryListResponse(list=history_list, total=total, hasMore=has_more)
    return success_response(message="获取浏览历史列表成功", data=data)


# 删除历史记录
@router.delete("/remove/{history_id}")
async def remove_history(
    history_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await history.remove_history(db, user.id, history_id)
    if not result:
        return success_response(message="历史记录不存在", data={"deleted": False})
    return success_response(message="删除成功", data={"deleted": True})


# 清空收藏列表：当前用户的收藏列表
@router.delete("/clear")
async def clear_favorite(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    count = await history.remove_all_history(db, user.id)
    return success_response(message=f"清空了{count}条记录")
