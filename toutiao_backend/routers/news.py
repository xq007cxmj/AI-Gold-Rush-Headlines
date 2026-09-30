from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from toutiao_backend.config.db_conf import get_db
from toutiao_backend.crud import news

# 创建APIRouter实例
# prefix路由前缀（API接口规范文档）
# tags分组，标签
router = APIRouter(
    prefix="/api/news", tags=["news"]
)  # prefix->添加路由前缀“/api/news”；tags->分组，组名为“news”


# 获取新闻分类接口实现流程
# 1.模块化路由-> API接口规范文档，创建APIRouter实例
# 2.定义模型类->数据库表（数据库设计文档）
# 3.在crud文件夹里面创建文件，封装操作数据库的方法
# 4.在routers文件夹里面创建文件，定义路由，调用crud里面的方法，响应结果


@router.get("/categories")
async def get_categories(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    # 先获取数据库里面新闻分类数据->先定义模型类->封装查询数据的方法
    categories = await news.get_categories(
        db, skip, limit
    )  # 调用get_categories方法获取新闻分类
    return {"code": 200, "message": "获取新闻分类成功", "data": categories}


# 获取新闻列表接口实现流程
# 1.模块化路由-> API接口规范文档，创建APIRouter实例
# 2.定义模型类->数据库表（数据库设计文档）
# 3.在crud文件夹里面创建文件，封装操作数据库的方法
# 4.在routers文件夹里面创建文件，定义路由，调用crud里面的方法
@router.get("/list")
async def get_news_list(
    category_id: int = Query(..., alias="categoryId"),
    page: int = 1,
    page_size: int = Query(10, alias="pageSize"),
    db: AsyncSession = Depends(get_db),
):
    # 先获取数据库里面新闻列表数据->先定义模型类->封装查询数据的方法
    # news_list = await news.get_news_list(
    #     db, category_id, (page - 1) * page_size, page_size
    # )
    # 思路：处理分页规则->查询新闻列表->计算总量->计算是否有更多数据->返回结果
    offset = (page - 1) * page_size
    news_list = await news.get_news_list(
        db, category_id, offset, page_size
    )  # 调用get_news_list方法获取新闻列表
    total_count = await news.get_news_count(db, category_id)
    # 逻辑判断是否有更多数据（跳过的数据+当前查询的数据<总数据量）
    has_more = offset + len(news_list) < total_count

    return {
        "code": 200,
        "message": "获取新闻列表成功",
        "data": {"list": news_list, "total": total_count, "has_more": has_more},
    }


# 获取新闻详细信息接口实现流程


@router.get("/detail")
async def get_news_detail(
    news_id: int = Query(..., alias="newsId"), db: AsyncSession = Depends(get_db)
):
    # 获取新闻详情 + 浏览量+1 + 相关新闻
    news_detail = await news.get_news_detail(
        db, news_id
    )  # 调用increase_news_views方法增加浏览量
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>views:", news_detail.views)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")
    views_result = await news.increase_news_views(
        db, news_detail.id
    )  # 调用increase_news_views方法增加浏览量
    if not views_result:
        raise HTTPException(status_code=404, detail="新闻不存在")

    related_news = await news.get_related_news(
        db, news_detail.id, news_detail.category_id
    )
    return {
        "code": 200,
        "message": "获取新闻详细信息成功",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publish_time": news_detail.publish_time,
            "category_id": news_detail.category_id,
            "views": news_detail.views,
            "related_news": related_news,
            # ),  # 获取相关新闻列表，默认获取5条
        },
    }
