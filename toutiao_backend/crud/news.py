from models.news import Category, News
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    # 先获取数据库里面新闻分类数据->先定义模型类->封装查询数据的方法
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()

    return {"code": 200, "message": "获取新闻分类成功", "data": categories}


async def get_news_list(
    db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10
):
    # 先获取数据库里面新闻列表数据->先定义模型类->封装查询数据的方法
    # 查询的是指定分类的所有新闻列表数据
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    return {"code": 200, "message": "获取新闻列表成功", "data": news_list}


async def get_news_count(db: AsyncSession, category_id: int):
    # 查询指定分类的新闻总数
    stmt = select(func.count()).where(News.category_id == category_id)
    result = await db.execute(stmt)
    count = (
        result.scalar_one()
    )  # 只能返回一个结果，如果查询结果为空或者有多个结果都会抛出异常
    return count


async def get_news_detail(db: AsyncSession, news_id: int):
    # 查询指定新闻的详细信息
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news_detail = (
        result.scalar_one_or_none()
    )  # 返回一个结果，如果查询结果为空返回None，如果有多个结果抛出异常
    return news_detail


async def increase_news_views(db: AsyncSession, news_id: int):
    # 查询指定新闻的详细信息
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()  # 提交事务，保存修改

    # 更新->检查数据库是否真的命中了数据->命中返回True->没有命中返回False
    return result.rowcount > 0


async def get_related_news(
    db: AsyncSession, news_id: int, category_id: int, limit: int = 5
):
    # 查询指定新闻的相关信息
    # order_by(News.created_at.desc())->按浏览量和发布时间排序
    stmt = (
        select(News)
        .where(News.id != news_id, News.category_id == category_id)
        .order_by(News.views.desc(), News.publish_time.desc())
        .limit(limit)
    )  # 默认升序，desc()降序
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    # 使用列表推导式 推导出新闻核心数据，再return出去
    return [
        {
            "id": news.id,
            "title": news.title,
            "content": news.content,
            "image": news.image,
            "author": news.author,
            "publish_time": news.publish_time,
            "category_id": news.category_id,
            "views": news.views,
        }
        for news in related_news
    ]
