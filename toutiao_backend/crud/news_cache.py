from fastapi.encoders import jsonable_encoder
from models.news import Category, News
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from toutiao_backend.cache.news_cache import (
    get_cache_news_list,
    get_cached_categories,
    set_cache_categories,
    set_cache_news_list,
)
from toutiao_backend.schemas.base import NewsItemBase


# 获取新闻分类
async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    # 先尝试从缓存中获取数据
    cached_categories = await get_cached_categories()
    if cached_categories:
        return cached_categories

    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()  # ORM实例

    # 写入缓存
    if categories:
        categories = jsonable_encoder(categories)  # ORM实例转换成字典
        await set_cache_categories(categories)

    # 返回数据
    return categories


# 获取新闻列表
async def get_news_list(
    db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10
):
    # 先尝试从缓存获取新闻列表
    # 跳过的数量skip = (页码 - 1) * 每页数量 -> 页码 = 跳过的数量 // 每页数量 + 1
    # await get_cache_news_list(分类id, 页码, 每页数量)

    page = skip // limit + 1
    cached_list = await get_cache_news_list(category_id, page, limit)  # 缓存数据 json
    if cached_list:
        # return cached_list  # 要的是 ORM
        return [News(**item) for item in cached_list]

    # 查询的是指定分类下的所有新闻
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    # 写入缓存
    if news_list:
        # 先把 ORM 数据 转换 字典才能写入缓存
        # ORM 转成 Pydantic，再转为 字典，注意orm对象必须与pydantic中的属性一致
        # by_alias=False 不适用别名，保存 Python 风格，因为 Redis 数据是给后端用的
        news_data = [
            NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False)
            for item in news_list
        ]
        await set_cache_news_list(category_id, page, limit, news_data)

    return news_list


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
