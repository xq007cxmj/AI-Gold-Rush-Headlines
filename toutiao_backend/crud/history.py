from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from toutiao_backend.models.history import History
from toutiao_backend.models.news import News


async def add_history(db: AsyncSession, user_id: int, news_id: int):
    """
    添加历史记录，如果已存在则更新浏览时间
    """
    query = select(History).where(
        History.user_id == user_id, History.news_id == news_id
    )
    result = await db.execute(query)
    existing_history = result.scalar_one_or_none()
    if existing_history:
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    else:
        history = History(user_id=user_id, news_id=news_id)
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history


# 获取历史记录列表：获取的是某个用户的浏览历史 + 分页功能
async def get_history_list(
    db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10
):
    # 总量 + 浏览历史列表
    count_query = select(func.count()).where(History.user_id == user_id)

    count_result = await db.execute(count_query)

    total = count_result.scalar_one()

    # 获取浏览历史列表 - 联表查询 join() + 浏览时间排序 + 分页
    # select(查询主体模型类, 给和主体模型类重复的字段的联合查询的模型类里的字段设置字段别名).join(联合查询的模型类, 联合查询的条件).where().order_by().offset().limit()
    # 别名： History.view_time.label("view_time")
    offset = (page - 1) * page_size
    # [
    #   (新闻对象, 浏览时间, 浏览id)
    # ]
    query = (
        select(
            News,
            History.view_time.label("view_time"),
            History.id.label("view_id"),
        )
        .join(History, History.news_id == News.id)
        .where(History.user_id == user_id)
        .order_by(History.view_time.desc())
        .offset(offset)
        .limit(page_size)
    )

    result = await db.execute(query)
    rows = result.all()
    # print("**" * 20)
    # print("result:", result)
    # print("rows:", rows)
    return rows, total


# 删除单条历史记录
async def remove_history(db: AsyncSession, user_id: int, news_id: int):
    """
    删除历史记录
    """
    query = delete(History).where(
        History.user_id == user_id, History.news_id == news_id
    )
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0


# 清空历史记录列表：当前用户的歷史记录列表
async def remove_all_history(db: AsyncSession, user_id: int):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()

    # 返回一个删除的数量
    return result.rowcount or 0
